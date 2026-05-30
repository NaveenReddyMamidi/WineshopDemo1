import csv
from io import StringIO

from flask import Flask, Response, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime
from models import db, User, Shop, Wine, WinePrice, DailyStock
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_filter("inr")
def format_inr(value):
    return f"₹{float(value or 0):,.2f}"


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/account/password", methods=["GET", "POST"])
@login_required
def account_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_password or not new_password or not confirm_password:
            flash("Complete all password fields", "warning")
            return redirect(url_for("account_password"))
        if not check_password_hash(current_user.password_hash, current_password):
            flash("Current password is incorrect", "danger")
            return redirect(url_for("account_password"))
        if new_password != confirm_password:
            flash("New password and confirmation do not match", "warning")
            return redirect(url_for("account_password"))
        if len(new_password) < 6:
            flash("New password must be at least 6 characters", "warning")
            return redirect(url_for("account_password"))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password updated successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("account_password.html")


def owner_required():
    return current_user.is_authenticated and current_user.role == "owner"


def can_access_shop(shop):
    if current_user.role == "owner":
        return True
    return shop in current_user.shops


def worker_shops_query():
    if current_user.role == "owner":
        return Shop.query.order_by(Shop.name)
    return current_user.shops


def percent_growth(current_value, previous_value):
    if previous_value:
        return round(((current_value - previous_value) / previous_value) * 100, 1)
    if current_value:
        return 100.0
    return 0.0


def build_dashboard_metrics(shops):
    today = date.today()
    trend_days = 1
    recent_start = today - timedelta(days=trend_days - 1)
    previous_start = recent_start - timedelta(days=trend_days)
    previous_end = recent_start - timedelta(days=1)
    shop_ids = [shop.id for shop in shops]

    empty_metrics = {
        "total_sales": 0.0,
        "total_units": 0,
        "daily_trend": [],
        "product_trends": [],
        "shop_growth": [],
        "stock_balances": [],
        "max_daily_sales": 1.0,
        "max_product_sales": 1.0,
        "top_shop_name": "No sales yet",
        "top_shop_sales": 0.0,
    }
    if not shop_ids:
        return empty_metrics

    entries = (
        DailyStock.query.filter(DailyStock.shop_id.in_(shop_ids))
        .filter(DailyStock.date >= previous_start)
        .all()
    )
    recent_entries = [entry for entry in entries if entry.date >= recent_start]
    previous_entries = [entry for entry in entries if previous_start <= entry.date <= previous_end]

    daily_sales = {recent_start + timedelta(days=offset): 0.0 for offset in range(trend_days)}
    product_totals = {}
    shop_recent = {shop.id: 0.0 for shop in shops}
    shop_previous = {shop.id: 0.0 for shop in shops}
    today_stock = {shop.id: {"opening": 0, "closing": 0, "opening_value": 0.0, "closing_value": 0.0} for shop in shops}

    for entry in recent_entries:
        sales_amount = float(entry.sales_amount)
        daily_sales[entry.date] = daily_sales.get(entry.date, 0.0) + sales_amount
        shop_recent[entry.shop_id] = shop_recent.get(entry.shop_id, 0.0) + sales_amount

        product = product_totals.setdefault(
            entry.wine_id,
            {
                "name": entry.wine.name,
                "shop_name": entry.shop.name,
                "sales": 0.0,
                "units": 0,
            },
        )
        product["sales"] += sales_amount
        product["units"] += entry.sales_qty

        if entry.date == today:
            stock = today_stock[entry.shop_id]
            price = float(entry.price)
            stock["opening"] += entry.opening_stock
            stock["closing"] += entry.closing_stock
            stock["opening_value"] += entry.opening_stock * price
            stock["closing_value"] += entry.closing_stock * price

    for entry in previous_entries:
        shop_previous[entry.shop_id] = shop_previous.get(entry.shop_id, 0.0) + float(entry.sales_amount)

    shop_growth = []
    for shop in shops:
        current_sales = round(shop_recent.get(shop.id, 0.0), 2)
        previous_sales = round(shop_previous.get(shop.id, 0.0), 2)
        shop_growth.append(
            {
                "shop": shop,
                "current_sales": current_sales,
                "previous_sales": previous_sales,
                "growth": percent_growth(current_sales, previous_sales),
            }
        )
    shop_growth.sort(key=lambda item: item["current_sales"], reverse=True)

    product_trends = sorted(product_totals.values(), key=lambda item: item["sales"], reverse=True)[:8]
    max_daily_sales = max(daily_sales.values()) if daily_sales else 0
    max_product_sales = max((item["sales"] for item in product_trends), default=0)
    top_shop = shop_growth[0] if shop_growth else None

    return {
        "total_sales": round(sum(float(entry.sales_amount) for entry in recent_entries), 2),
        "total_units": sum(entry.sales_qty for entry in recent_entries),
        "daily_trend": [
            {
                "date": trend_date,
                "label": trend_date.strftime("%d %b"),
                "sales": round(amount, 2),
                "height": max(4, round((amount / max_daily_sales) * 100)) if max_daily_sales else 4,
            }
            for trend_date, amount in daily_sales.items()
        ],
        "product_trends": [
            {
                "name": item["name"],
                "shop_name": item["shop_name"],
                "sales": round(item["sales"], 2),
                "units": item["units"],
                "width": max(4, round((item["sales"] / max_product_sales) * 100)) if max_product_sales else 4,
            }
            for item in product_trends
        ],
        "shop_growth": shop_growth,
        "stock_balances": [
            {
                "shop": shop,
                "opening": today_stock[shop.id]["opening"],
                "closing": today_stock[shop.id]["closing"],
                "opening_value": round(today_stock[shop.id]["opening_value"], 2),
                "closing_value": round(today_stock[shop.id]["closing_value"], 2),
            }
            for shop in shops
        ],
        "max_daily_sales": max(max_daily_sales, 1.0),
        "max_product_sales": max(max_product_sales, 1.0),
        "top_shop_name": top_shop["shop"].name if top_shop else "No sales yet",
        "top_shop_sales": top_shop["current_sales"] if top_shop else 0.0,
    }


def build_today_shop_report(shop, report_date=None):
    if report_date is None:
        report_date = date.today()
    entries = (
        DailyStock.query.filter_by(shop_id=shop.id, date=report_date)
        .join(Wine)
        .order_by(Wine.name)
        .all()
    )
    total_opening = sum(entry.opening_stock for entry in entries)
    total_closing = sum(entry.closing_stock for entry in entries)
    total_units = sum(entry.sales_qty for entry in entries)
    total_sales = sum(float(entry.sales_amount) for entry in entries)
    opening_value = sum(entry.opening_stock * float(entry.price) for entry in entries)
    closing_value = sum(entry.closing_stock * float(entry.price) for entry in entries)

    return {
        "shop": shop,
        "date": report_date,
        "entries": entries,
        "total_opening": total_opening,
        "total_closing": total_closing,
        "total_units": total_units,
        "total_sales": round(total_sales, 2),
        "opening_value": round(opening_value, 2),
        "closing_value": round(closing_value, 2),
    }


def pdf_escape(value):
    text = str(value)
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(title, lines):
    page_width = 612
    page_height = 792
    margin_left = 50
    start_y = 742
    line_height = 14
    lines_per_page = 46
    pages = [lines[index:index + lines_per_page] for index in range(0, len(lines), lines_per_page)] or [[]]
    objects = []
    page_object_ids = []

    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(None)
    font_object_id = 3
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    next_object_id = 4
    for page_lines in pages:
        content_lines = ["BT", "/F1 11 Tf", f"{margin_left} {start_y} Td"]
        content_lines.append(f"({pdf_escape(title)}) Tj")
        content_lines.append(f"0 -{line_height * 2} Td")
        for line in page_lines:
            content_lines.append(f"({pdf_escape(line)}) Tj")
            content_lines.append(f"0 -{line_height} Td")
        content_lines.append("ET")
        stream = "\n".join(content_lines)

        page_object_id = next_object_id
        content_object_id = next_object_id + 1
        page_object_ids.append(page_object_id)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> /Contents {content_object_id} 0 R >>"
        )
        stream_bytes = stream.encode("latin-1", "replace")
        objects.append(
            f"<< /Length {len(stream_bytes)} >>\nstream\n"
            f"{stream_bytes.decode('latin-1')}\nendstream"
        )
        next_object_id += 2

    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>"

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n{body}\nendobj\n".encode("latin-1", "replace"))

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )
    return bytes(pdf)


def pdf_text(x, y, text, size=9):
    return f"BT /F1 {size} Tf {x} {y} Td ({pdf_escape(text)}) Tj ET"


def fit_pdf_cell(value, width, size=8):
    text = str(value)
    max_chars = max(int((width - 8) / (size * 0.6)), 3)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def build_sales_report_pdf(title, report):
    page_width = 612
    page_height = 792
    margin_x = 40
    top_y = 750
    row_height = 22
    table_width = 532
    columns = [
        ("Wine", 135),
        ("Short", 50),
        ("ML", 35),
        ("Opening", 55),
        ("Closing", 55),
        ("Sold", 40),
        ("Price INR", 78),
        ("Sales INR", 84),
    ]
    entries = report["entries"]
    rows_per_first_page = 19
    rows_per_page = 27
    chunks = []
    if entries:
        chunks.append(entries[:rows_per_first_page])
        remaining = entries[rows_per_first_page:]
        for index in range(0, len(remaining), rows_per_page):
            chunks.append(remaining[index:index + rows_per_page])
    else:
        chunks.append([])

    def draw_line(commands, x1, y1, x2, y2):
        commands.append(f"{x1} {y1} m {x2} {y2} l S")

    def draw_cell_text(commands, x, y, text, width, size=8):
        commands.append(pdf_text(x + 4, y + 7, fit_pdf_cell(text, width, size), size))

    def draw_table(commands, rows, start_y):
        y = start_y
        commands.append("0.92 0.95 0.98 rg")
        commands.append(f"{margin_x} {y - row_height} {table_width} {row_height} re f")
        commands.append("0 g")

        current_x = margin_x
        for label, width in columns:
            draw_cell_text(commands, current_x, y - row_height, label, width, 8)
            current_x += width

        total_rows = max(len(rows), 1)
        table_height = row_height * (total_rows + 1)
        commands.append(f"{margin_x} {y - table_height} {table_width} {table_height} re S")

        current_x = margin_x
        for _, width in columns[:-1]:
            current_x += width
            draw_line(commands, current_x, y, current_x, y - table_height)

        for offset in range(total_rows + 2):
            row_y = y - (offset * row_height)
            draw_line(commands, margin_x, row_y, margin_x + table_width, row_y)

        if rows:
            for row_index, entry in enumerate(rows):
                row_top = y - row_height * (row_index + 1)
                values = [
                    entry.wine.name,
                    entry.wine.short_name or "-",
                    entry.wine.ml or "-",
                    entry.opening_stock,
                    entry.closing_stock,
                    entry.sales_qty,
                    f"{float(entry.price):.2f}",
                    f"{float(entry.sales_amount):.2f}",
                ]
                current_x = margin_x
                for value, (_, width) in zip(values, columns):
                    draw_cell_text(commands, current_x, row_top - row_height, value, width, 8)
                    current_x += width
        else:
            commands.append(pdf_text(margin_x + 4, y - (row_height * 2) + 7, "No sales entries found for today.", 8))

    page_streams = []
    for page_index, chunk in enumerate(chunks):
        commands = ["0.75 w", "0 g"]
        commands.append(pdf_text(margin_x, top_y, title, 15))
        commands.append(pdf_text(margin_x, top_y - 22, f"Shop: {report['shop'].name}", 10))
        commands.append(pdf_text(margin_x, top_y - 38, f"Address: {report['shop'].location or ''}", 10))
        commands.append(pdf_text(margin_x, top_y - 54, f"Date: {report['date'].isoformat()}", 10))

        if page_index == 0:
            summary_y = top_y - 88
            summary_rows = [
                ("Opening Qty", report["total_opening"]),
                ("Closing Qty", report["total_closing"]),
                ("Units Sold", report["total_units"]),
                ("Total Sales INR", f"{report['total_sales']:.2f}"),
                ("Opening Value INR", f"{report['opening_value']:.2f}"),
                ("Closing Value INR", f"{report['closing_value']:.2f}"),
            ]
            commands.append(pdf_text(margin_x, summary_y, "Summary", 11))
            box_x = margin_x
            box_y = summary_y - 12
            label_width = 150
            value_width = 110
            for index, (label, value) in enumerate(summary_rows):
                row_y = box_y - (index * row_height)
                commands.append(f"{box_x} {row_y - row_height} {label_width + value_width} {row_height} re S")
                draw_line(commands, box_x + label_width, row_y, box_x + label_width, row_y - row_height)
                draw_cell_text(commands, box_x, row_y - row_height, label, label_width, 8)
                draw_cell_text(commands, box_x + label_width, row_y - row_height, value, value_width, 8)

            table_title_y = box_y - (len(summary_rows) * row_height) - 30
            commands.append(pdf_text(margin_x, table_title_y, "Product Sales", 11))
            draw_table(commands, chunk, table_title_y - 12)
        else:
            commands.append(pdf_text(margin_x, top_y - 78, "Product Sales Continued", 11))
            draw_table(commands, chunk, top_y - 92)

        page_streams.append("\n".join(commands))

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    page_object_ids = []
    next_object_id = 4
    for stream in page_streams:
        page_object_id = next_object_id
        content_object_id = next_object_id + 1
        page_object_ids.append(page_object_id)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_object_id} 0 R >>"
        )
        stream_bytes = stream.encode("latin-1", "replace")
        objects.append(
            f"<< /Length {len(stream_bytes)} >>\nstream\n"
            f"{stream_bytes.decode('latin-1')}\nendstream"
        )
        next_object_id += 2

    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>"

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n{body}\nendobj\n".encode("latin-1", "replace"))

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )
    return bytes(pdf)


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "owner":
        return redirect(url_for("owner_home"))

    return redirect(url_for("shops"))


@app.route("/reports")
@login_required
def reports():
    shops = Shop.query.order_by(Shop.name).all() if current_user.role == "owner" else sorted(current_user.shops, key=lambda shop: shop.name.lower())
    selected_shop = None
    report = None
    shop_id = request.args.get("shop_id")
    report_date_str = request.args.get("date")
    
    report_date = None
    try:
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date() if report_date_str else date.today()
    except (ValueError, TypeError):
        report_date = date.today()
    
    if shop_id:
        try:
            selected_shop = Shop.query.get_or_404(int(shop_id))
            if not can_access_shop(selected_shop):
                flash("You can access only your assigned shop", "danger")
                return redirect(url_for("reports"))
            report = build_today_shop_report(selected_shop, report_date)
        except ValueError:
            flash("Invalid shop selected", "warning")

    return render_template(
        "owner_reports.html",
        shops=shops,
        selected_shop=selected_shop,
        report=report,
        reports_endpoint="reports",
        selected_date=report_date,
    )


@app.route("/owner/home")
@app.route("/owner/dashboard")
@login_required
def owner_home():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    shops = Shop.query.order_by(Shop.name).all()
    shop_count = len(shops)
    wine_count = Wine.query.count()
    metrics = build_dashboard_metrics(shops)
    return render_template(
        "owner_home.html",
        shops=shops,
        shop_count=shop_count,
        wine_count=wine_count,
        metrics=metrics,
    )


@app.route("/owner/add-shop", methods=["GET", "POST"])
@login_required
def owner_add_shop():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        if not name:
            flash("Shop name is required", "warning")
        else:
            shop = Shop(name=name.strip(), location=location.strip() if location else None)
            db.session.add(shop)
            db.session.commit()
            flash(f"Shop {name} created successfully", "success")
            return redirect(url_for("owner_add_shop"))
    shops = Shop.query.order_by(Shop.name).all()
    return render_template("owner_add_shop.html", shops=shops)


@app.route("/owner/wines")
@login_required
def owner_wines():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    shops = Shop.query.order_by(Shop.name).all()
    wines = Wine.query.join(Shop).order_by(Shop.name, Wine.name).all()
    return render_template("owner_wines.html", shops=shops, wines=wines)


@app.route("/owner/prices")
@login_required
def owner_prices():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    shops = Shop.query.order_by(Shop.name).all()
    return render_template("owner_prices.html", shops=shops)


@app.route("/owner/prices/<int:shop_id>")
@login_required
def owner_manage_prices(shop_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    shop = Shop.query.get_or_404(shop_id)
    wines = Wine.query.filter_by(shop_id=shop_id).order_by(Wine.name).all()
    prices = WinePrice.query.filter_by(shop_id=shop_id).join(Wine).order_by(Wine.name).all()
    price_map = {price.wine.id: price for price in prices}
    return render_template("owner_manage_prices.html", shop=shop, prices=prices, wines=wines, price_map=price_map)


@app.route("/owner/workers")
@login_required
def owner_workers():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    shops = Shop.query.order_by(Shop.name).all()
    all_workers = User.query.filter_by(role="worker").all()
    return render_template("owner_workers.html", shops=shops, all_workers=all_workers)


@app.route("/owner/reports")
@login_required
def owner_reports():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    shops = Shop.query.order_by(Shop.name).all()
    selected_shop = None
    report = None
    shop_id = request.args.get("shop_id")
    report_date_str = request.args.get("date")
    
    report_date = None
    try:
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date() if report_date_str else date.today()
    except (ValueError, TypeError):
        report_date = date.today()
    
    if shop_id:
        try:
            selected_shop = Shop.query.get_or_404(int(shop_id))
            report = build_today_shop_report(selected_shop, report_date)
        except ValueError:
            flash("Invalid shop selected", "warning")

    return render_template(
        "owner_reports.html",
        shops=shops,
        selected_shop=selected_shop,
        report=report,
        selected_date=report_date,
    )


@app.route("/owner/reports/download")
@login_required
def owner_download_report():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    shop_id = request.args.get("shop_id")
    report_date_str = request.args.get("date")
    
    if not shop_id:
        flash("Select a shop before downloading report", "warning")
        return redirect(url_for("owner_reports"))

    report_date = None
    try:
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date() if report_date_str else date.today()
    except (ValueError, TypeError):
        report_date = date.today()

    try:
        shop = Shop.query.get_or_404(int(shop_id))
    except ValueError:
        flash("Invalid shop selected", "warning")
        return redirect(url_for("owner_reports"))

    report = build_today_shop_report(shop, report_date)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sales Report"])
    writer.writerow(["Shop", shop.name])
    writer.writerow(["Address", shop.location or ""])
    writer.writerow(["Date", report["date"].isoformat()])
    writer.writerow([])
    writer.writerow(["Wine", "Short Name", "ML", "Opening", "Closing", "Sold", "Price (INR)", "Sales Amount (INR)"])
    for entry in report["entries"]:
        writer.writerow(
            [
                entry.wine.name,
                entry.wine.short_name or "",
                entry.wine.ml or "",
                entry.opening_stock,
                entry.closing_stock,
                entry.sales_qty,
                f"{float(entry.price):.2f}",
                f"{float(entry.sales_amount):.2f}",
            ]
        )
    writer.writerow([])
    writer.writerow(["Summary"])
    writer.writerow(["Opening Qty", report["total_opening"]])
    writer.writerow(["Closing Qty", report["total_closing"]])
    writer.writerow(["Units Sold", report["total_units"]])
    writer.writerow(["Total Sales (INR)", f"{report['total_sales']:.2f}"])
    writer.writerow(["Opening Value (INR)", f"{report['opening_value']:.2f}"])
    writer.writerow(["Closing Value (INR)", f"{report['closing_value']:.2f}"])

    filename = f"{shop.name.lower().replace(' ', '-')}-sales-{report['date'].isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/owner/reports/download/pdf")
@login_required
def owner_download_report_pdf():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    shop_id = request.args.get("shop_id")
    report_date_str = request.args.get("date")
    
    if not shop_id:
        flash("Select a shop before downloading report", "warning")
        return redirect(url_for("owner_reports"))

    report_date = None
    try:
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date() if report_date_str else date.today()
    except (ValueError, TypeError):
        report_date = date.today()

    try:
        shop = Shop.query.get_or_404(int(shop_id))
    except ValueError:
        flash("Invalid shop selected", "warning")
        return redirect(url_for("owner_reports"))

    report = build_today_shop_report(shop, report_date)
    title = f"Sales Report - {report_date.strftime('%B %d, %Y')}"

    filename = f"{shop.name.lower().replace(' ', '-')}-sales-{report['date'].isoformat()}.pdf"
    return Response(
        build_sales_report_pdf(title, report),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/owner/add-worker", methods=["POST"])
@login_required
def owner_add_worker():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))
    username = request.form.get("username")
    password = request.form.get("password")
    shop_id = request.form.get("shop_id")
    if not username or not password or not shop_id:
        flash("Username, password, and shop are required", "warning")
        return redirect(url_for("owner_workers"))
    if User.query.filter_by(username=username).first():
        flash("Username already exists", "warning")
        return redirect(url_for("owner_workers"))
    try:
        shop_id = int(shop_id)
    except ValueError:
        flash("Invalid shop ID", "warning")
        return redirect(url_for("owner_workers"))
    worker = User(username=username.strip(), password_hash=generate_password_hash(password), role="worker")
    db.session.add(worker)
    db.session.commit()
    shop = Shop.query.get_or_404(shop_id)
    shop.workers.append(worker)
    db.session.commit()
    flash(f"Worker {username} assigned to {shop.name}", "success")
    return redirect(url_for("owner_workers"))




@app.route("/owner/update-worker-password/<int:user_id>", methods=["POST"])
@login_required
def owner_update_worker_password(user_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    worker = User.query.get_or_404(user_id)
    if worker.role != "worker":
        flash("Only worker passwords can be updated here", "warning")
        return redirect(url_for("owner_workers"))

    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    if not new_password or not confirm_password:
        flash("New password and confirmation are required", "warning")
        return redirect(url_for("owner_workers"))
    if new_password != confirm_password:
        flash("Worker password confirmation does not match", "warning")
        return redirect(url_for("owner_workers"))
    if len(new_password) < 6:
        flash("Worker password must be at least 6 characters", "warning")
        return redirect(url_for("owner_workers"))

    worker.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash(f"Password updated for {worker.username}", "success")
    return redirect(url_for("owner_workers"))


@app.route("/owner/delete-shop/<int:shop_id>", methods=["POST"])
@login_required
def owner_delete_shop(shop_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    shop = Shop.query.get_or_404(shop_id)
    shop_name = shop.name
    DailyStock.query.filter_by(shop_id=shop.id).delete(synchronize_session=False)
    WinePrice.query.filter_by(shop_id=shop.id).delete(synchronize_session=False)
    Wine.query.filter_by(shop_id=shop.id).delete(synchronize_session=False)
    shop.workers.clear()
    db.session.delete(shop)
    db.session.commit()
    flash(f"Shop {shop_name} deleted", "success")
    return redirect(url_for("owner_add_shop"))


@app.route("/owner/delete-wine/<int:wine_id>", methods=["POST"])
@login_required
def owner_delete_wine(wine_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    wine = Wine.query.get_or_404(wine_id)
    wine_name = wine.name
    DailyStock.query.filter_by(wine_id=wine.id).delete(synchronize_session=False)
    WinePrice.query.filter_by(wine_id=wine.id).delete(synchronize_session=False)
    db.session.delete(wine)
    db.session.commit()
    flash(f"Wine {wine_name} deleted", "success")
    return redirect(url_for("owner_wines"))


@app.route("/owner/delete-price/<int:price_id>", methods=["POST"])
@login_required
def owner_delete_price(price_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    price = WinePrice.query.get_or_404(price_id)
    shop_id = price.shop_id
    wine_name = price.wine.name
    db.session.delete(price)
    db.session.commit()
    flash(f"{wine_name} removed from price list", "success")
    return redirect(url_for("owner_manage_prices", shop_id=shop_id))


@app.route("/owner/delete-worker/<int:user_id>", methods=["POST"])
@login_required
def owner_delete_worker(user_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    worker = User.query.get_or_404(user_id)
    if worker.role != "worker":
        flash("Only worker users can be deleted here", "warning")
        return redirect(url_for("owner_workers"))

    username = worker.username
    worker.shops.clear()
    db.session.delete(worker)
    db.session.commit()
    flash(f"Worker {username} deleted", "success")
    return redirect(url_for("owner_workers"))


@app.route("/shops")
@login_required
def shops():
    if current_user.role == "owner":
        shops = Shop.query.order_by(Shop.name).all()
    else:
        shops = sorted(current_user.shops, key=lambda shop: shop.name.lower())
    return render_template("shops.html", shops=shops)


@app.route("/shop/<int:shop_id>")
@login_required
def shop_detail(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if not can_access_shop(shop):
        flash("You can access only your assigned shop", "danger")
        return redirect(url_for("dashboard"))
    prices = WinePrice.query.filter_by(shop_id=shop.id).join(Wine).order_by(Wine.name).all()
    return render_template("shop_detail.html", shop=shop, prices=prices)


@app.route("/shop/<int:shop_id>/daily_stock", methods=["GET", "POST"])
@login_required
def daily_stock(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if not can_access_shop(shop):
        flash("You can access only your assigned shop", "danger")
        return redirect(url_for("dashboard"))
    
    # Get selected date from request, default to today
    selected_date_str = request.args.get("date") or request.form.get("date")
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else date.today()
    except (ValueError, TypeError):
        selected_date = date.today()
    
    shop_wines = Wine.query.filter_by(shop_id=shop.id).order_by(Wine.name).all()
    price_records = WinePrice.query.filter_by(shop_id=shop.id).all()
    price_map = {price.wine_id: float(price.price) for price in price_records}

    product_list = []
    product_map = {}
    for wine in shop_wines:
        details = {
            "wine_id": wine.id,
            "name": wine.name,
            "short_name": wine.short_name or "",
            "ml": wine.ml,
            "price": price_map.get(wine.id, 0.0),
        }
        product_list.append(details)
        product_map[wine.name.lower()] = details
        if wine.short_name:
            product_map[wine.short_name.lower()] = details

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        wine_id = request.form.get("wine_id")
        opening_stock = request.form.get("opening_stock")
        closing_stock = request.form.get("closing_stock")

        if not product_name or not wine_id or not opening_stock or not closing_stock:
            flash("Complete all product and stock fields", "warning")
            return redirect(url_for("daily_stock", shop_id=shop_id, date=selected_date.isoformat()))

        try:
            wine_id = int(wine_id)
            opening_stock = int(opening_stock)
            closing_stock = int(closing_stock)
        except ValueError:
            flash("Stock values must be whole numbers", "warning")
            return redirect(url_for("daily_stock", shop_id=shop_id, date=selected_date.isoformat()))

        if not any(wine.id == wine_id for wine in shop_wines):
            flash("Selected product is not available in this shop", "warning")
            return redirect(url_for("daily_stock", shop_id=shop_id, date=selected_date.isoformat()))

        price_value = price_map.get(wine_id, 0.0)
        sales_qty = max(opening_stock - closing_stock, 0)
        sales_amount = round(price_value * sales_qty, 2)

        stock_record = DailyStock.query.filter_by(shop_id=shop.id, wine_id=wine_id, date=selected_date).first()
        if not stock_record:
            stock_record = DailyStock(
                shop_id=shop.id,
                wine_id=wine_id,
                date=selected_date,
                opening_stock=opening_stock,
                closing_stock=closing_stock,
                sales_qty=sales_qty,
                price=price_value,
                sales_amount=sales_amount,
            )
            db.session.add(stock_record)
        else:
            stock_record.opening_stock = opening_stock
            stock_record.closing_stock = closing_stock
            stock_record.sales_qty = sales_qty
            stock_record.price = price_value
            stock_record.sales_amount = sales_amount

        db.session.commit()
        flash(f"Daily stock saved for {product_name}", "success")
        return redirect(url_for("daily_stock", shop_id=shop_id, date=selected_date.isoformat()))

    daily_entries = DailyStock.query.filter_by(shop_id=shop.id, date=selected_date).join(Wine).order_by(Wine.name).all()
    total_sales = sum(float(entry.sales_amount) for entry in daily_entries)
    closing_inventory_value = sum(float(entry.closing_stock) * float(entry.price) for entry in daily_entries)

    return render_template(
        "daily_stock.html",
        shop=shop,
        product_list=product_list,
        product_map=product_map,
        daily_entries=daily_entries,
        total_sales=total_sales,
        closing_inventory_value=closing_inventory_value,
        selected_date=selected_date,
    )


@app.route("/shop/<int:shop_id>/update_price", methods=["POST"])
@login_required
def update_price(shop_id):
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    wine_id = request.form.get("wine_id")
    new_price = request.form.get("price")
    if not wine_id or not new_price:
        flash("Wine and price are required", "warning")
        return redirect(url_for("shop_detail", shop_id=shop_id))

    try:
        wine_id = int(wine_id)
    except ValueError:
        flash("Invalid wine ID", "warning")
        return redirect(url_for("shop_detail", shop_id=shop_id))

    price_record = WinePrice.query.filter_by(shop_id=shop_id, wine_id=wine_id).first()
    if price_record:
        try:
            price_record.price = float(new_price)
            db.session.commit()
            flash("Price updated successfully", "success")
        except ValueError:
            flash("Invalid price entered", "warning")
    else:
        flash("Wine price record not found", "warning")

    return redirect(request.referrer or url_for("owner_manage_prices", shop_id=shop_id))


@app.route("/create_wine", methods=["POST"])
@login_required
def create_wine():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    shop_id = request.form.get("shop_id")
    name = request.form.get("name")
    short_name = request.form.get("short_name")
    ml = request.form.get("ml")
    description = request.form.get("description")

    if not shop_id or not name:
        flash("Shop and wine name are required", "warning")
        return redirect(url_for("owner_wines"))

    try:
        shop_id = int(shop_id)
        ml_value = int(ml) if ml else None
    except ValueError:
        flash("Invalid shop or volume", "warning")
        return redirect(url_for("owner_wines"))

    shop = Shop.query.get_or_404(shop_id)
    wine = Wine(shop_id=shop_id, name=name.strip(), short_name=short_name.strip() if short_name else None, ml=ml_value, description=description.strip() if description else None)
    db.session.add(wine)
    db.session.commit()

    price_record = WinePrice(shop_id=shop_id, wine_id=wine.id, price=0.0)
    db.session.add(price_record)
    db.session.commit()

    flash(f"Wine {name} added to {shop.name}", "success")
    return redirect(url_for("owner_wines"))


@app.route("/create_shop", methods=["POST"])
@login_required
def create_shop():
    if not owner_required():
        flash("Permission denied", "danger")
        return redirect(url_for("dashboard"))

    name = request.form.get("name")
    location = request.form.get("location")
    if not name:
        flash("Shop name is required", "warning")
        return redirect(url_for("dashboard"))

    shop = Shop(name=name.strip(), location=location.strip() if location else None)
    db.session.add(shop)
    db.session.commit()

    flash("Shop created successfully", "success")
    return redirect(url_for("owner_add_shop"))


if __name__ == "__main__":
    app.run(debug=True)
