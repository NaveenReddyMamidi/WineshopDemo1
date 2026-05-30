from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

shop_workers = db.Table(
    "shop_workers",
    db.Column("shop_id", db.Integer, db.ForeignKey("shop.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column("password", db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="worker")
    shops = db.relationship("Shop", secondary=shop_workers, back_populates="workers")

    def __repr__(self):
        return f"<User {self.username} {self.role}>"


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    workers = db.relationship("User", secondary=shop_workers, back_populates="shops")
    prices = db.relationship("WinePrice", back_populates="shop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Shop {self.name}>"


class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shop.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    short_name = db.Column(db.String(20), nullable=True)
    ml = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    prices = db.relationship("WinePrice", back_populates="wine", cascade="all, delete-orphan")
    shop = db.relationship("Shop")

    def __repr__(self):
        return f"<Wine {self.name} ({self.short_name}) {self.ml}ml>"


class WinePrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shop.id"), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey("wine.id"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)

    shop = db.relationship("Shop", back_populates="prices")
    wine = db.relationship("Wine", back_populates="prices")

    def __repr__(self):
        return f"<WinePrice shop={self.shop_id} wine={self.wine_id} price={self.price}>"


class DailyStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shop.id"), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey("wine.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    opening_stock = db.Column(db.Integer, nullable=False, default=0)
    closing_stock = db.Column(db.Integer, nullable=False, default=0)
    sales_qty = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    sales_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)

    shop = db.relationship("Shop")
    wine = db.relationship("Wine")

    __table_args__ = (
        db.UniqueConstraint("shop_id", "wine_id", "date", name="uix_shop_wine_date"),
        db.Index("ix_daily_stock_shop_date", "shop_id", "date"),
    )

    def __repr__(self):
        return f"<DailyStock shop={self.shop_id} wine={self.wine_id} date={self.date} sales_amount={self.sales_amount}>"
