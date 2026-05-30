import os
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Shop, Wine, WinePrice

with app.app_context():
    db.drop_all()
    db.create_all()

    owner = User(
        username="owner",
        password_hash=generate_password_hash("ownerpass"),
        role="owner",
    )
    worker = User(
        username="worker",
        password_hash=generate_password_hash("workerpass"),
        role="worker",
    )
    db.session.add(owner)
    db.session.add(worker)

    shop_a = Shop(name="Shop-1", location="Shop-1 Location")
    shop_b = Shop(name="Shop-2", location="Shop-2 Location")
    shop_c = Shop(name="Shop-3", location="Shop-3 Location")
    shop_d = Shop(name="Shop-4", location="Shop-4 Location")
    shop_e = Shop(name="Shop-5", location="Shop-5 Location")
    db.session.add_all([shop_a, shop_b, shop_c, shop_d, shop_e])
    db.session.commit()

    wine1_a = Wine(shop_id=shop_a.id, name="Blender Spride", short_name="BS180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine2_a = Wine(shop_id=shop_a.id, name="Royal Challenge", short_name="RC180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine3_a = Wine(shop_id=shop_a.id, name="Royal Stag W", short_name="RSW180", ml=180, description="Crisp white wine with green apple notes.")
    wine4_a = Wine(shop_id=shop_a.id, name="M/C No.1", short_name="MC750", ml=750, description="Soft red wine with plum and berry flavors.")
    wine5_a = Wine(shop_id=shop_a.id, name="M/C No.1", short_name="MC180", ml=180, description="Crisp white wine with green apple notes.")
    wine6_a = Wine(shop_id=shop_a.id, name="M/C No.1", short_name="MC90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine7_a = Wine(shop_id=shop_a.id, name="M/C Luxary", short_name="MCL180", ml=180, description="Crisp white wine with green apple notes.")
    wine8_a = Wine(shop_id=shop_a.id, name="Imperial Blue", short_name="IB750", ml=750, description="Soft red wine with plum and berry flavors.")
    wine9_a = Wine(shop_id=shop_a.id, name="Imperial Blue", short_name="IB180", ml=180, description="Crisp white wine with green apple notes.")
    wine10_a = Wine(shop_id=shop_a.id, name="Imperial Blue", short_name="IB90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine11_a = Wine(shop_id=shop_a.id, name="B.P.", short_name="BP750", ml=750, description="Crisp white wine with green apple notes.")
    wine12_a = Wine(shop_id=shop_a.id, name="B.P.", short_name="BP180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine13_a = Wine(shop_id=shop_a.id, name="B.P.", short_name="BP90", ml=90, description="Crisp white wine with green apple notes.")
    wine14_a = Wine(shop_id=shop_a.id, name="D.S.P. Black", short_name="DSP180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine15_a = Wine(shop_id=shop_a.id, name="D.S.P.", short_name="DSP90", ml=90, description="Crisp white wine with green apple notes.")
    wine16_a = Wine(shop_id=shop_a.id, name="Officer Choice", short_name="OC180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine17_a = Wine(shop_id=shop_a.id, name="Officer Choice", short_name="OC90", ml=90, description="Crisp white wine with green apple notes.")
    wine18_a = Wine(shop_id=shop_a.id, name="O.T.", short_name="OT750", ml=750, description="Soft red wine with plum and berry flavors.")
    wine19_a = Wine(shop_id=shop_a.id, name="O.T.", short_name="OT180", ml=180, description="Crisp white wine with green apple notes.")
    wine20_a = Wine(shop_id=shop_a.id, name="O.T.", short_name="OT90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine21_a = Wine(shop_id=shop_a.id, name="8 P.M.", short_name="8PM750", ml=750, description="Crisp white wine with green apple notes.")
    wine22_a = Wine(shop_id=shop_a.id, name="8 P.M.", short_name="8PM180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine23_a = Wine(shop_id=shop_a.id, name="8 P.M.", short_name="8PM90", ml=90, description="Crisp white wine with green apple notes.")
    wine24_a = Wine(shop_id=shop_a.id, name="O.C. Star", short_name="OCS180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine25_a = Wine(shop_id=shop_a.id, name="Original Choice", short_name="OCH750", ml=750, description="Crisp white wine with green apple notes.")
    wine26_a = Wine(shop_id=shop_a.id, name="Original Choice", short_name="OCH180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine27_a = Wine(shop_id=shop_a.id, name="Original Choice", short_name="OCH90", ml=90, description="Crisp white wine with green apple notes.")
    wine28_a = Wine(shop_id=shop_a.id, name="Traveller", short_name="TRV180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine29_a = Wine(shop_id=shop_a.id, name="Traveller", short_name="TRV90", ml=90, description="Crisp white wine with green apple notes.")
    wine30_a = Wine(shop_id=shop_a.id, name="I Konic", short_name="IKO180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine31_a = Wine(shop_id=shop_a.id, name="I Konic", short_name="IKO90", ml=90, description="Crisp white wine with green apple notes.")
    wine32_a = Wine(shop_id=shop_a.id, name="U.S. Whisky", short_name="USW180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine33_a = Wine(shop_id=shop_a.id, name="U.S. Whisky", short_name="USW90", ml=90, description="Crisp white wine with green apple notes.")
    wine34_a = Wine(shop_id=shop_a.id, name="Haywords Plane", short_name="HAY90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine35_a = Wine(shop_id=shop_a.id, name="Gonas Wines", short_name="GON180", ml=180, description="Crisp white wine with green apple notes.")
    wine36_a = Wine(shop_id=shop_a.id, name="O.R.C. Gin", short_name="ORC90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine37_a = Wine(shop_id=shop_a.id, name="D.K.", short_name="DK90", ml=90, description="Crisp white wine with green apple notes.")
    wine38_a = Wine(shop_id=shop_a.id, name="K.F.L. Beer", short_name="KFL650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine39_a = Wine(shop_id=shop_a.id, name="K.F.L. Beer Tinn", short_name="KFLT330", ml=330, description="Crisp white wine with green apple notes.")
    wine40_a = Wine(shop_id=shop_a.id, name="K.F.S. Beer", short_name="KFS650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine41_a = Wine(shop_id=shop_a.id, name="K.F.S. Beer Tinn", short_name="KFST500", ml=500, description="Crisp white wine with green apple notes.")
    wine42_a = Wine(shop_id=shop_a.id, name="K.F. Strong Beer Can", short_name="KFSC330", ml=330, description="Soft red wine with plum and berry flavors.")
    wine43_a = Wine(shop_id=shop_a.id, name="K.F. Strong Beer Bottle", short_name="KFSB330", ml=330, description="Crisp white wine with green apple notes.")
    wine44_a = Wine(shop_id=shop_a.id, name="K. Out", short_name="KOUT650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine45_a = Wine(shop_id=shop_a.id, name="K. Out", short_name="KOUT330", ml=330, description="Crisp white wine with green apple notes.")
    wine46_a = Wine(shop_id=shop_a.id, name="Tubarg (S)", short_name="TUB650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine47_a = Wine(shop_id=shop_a.id, name="K.F. Ultra", short_name="KFUL650", ml=650, description="Crisp white wine with green apple notes.")
    wine48_a = Wine(shop_id=shop_a.id, name="K.F. Max", short_name="KFMAX650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine49_a = Wine(shop_id=shop_a.id, name="Budwiser Magnium", short_name="BUD650", ml=650, description="Crisp white wine with green apple notes.")
    wine50_a = Wine(shop_id=shop_a.id, name="Power Cool", short_name="POWER650", ml=650, description="Soft red wine with plum and berry flavors.")
    wine51_a = Wine(shop_id=shop_a.id, name="Power Cool", short_name="POWER500", ml=500, description="Crisp white wine with green apple notes.")
    wine52_a = Wine(shop_id=shop_a.id, name="Power Cool", short_name="POWER330", ml=330, description="Soft red wine with plum and berry flavors.")
    wine53_a = Wine(shop_id=shop_a.id, name="Bullet", short_name="BUL650", ml=650, description="Crisp white wine with green apple notes.")
    wine54_a = Wine(shop_id=shop_a.id, name="Bullet", short_name="BUL330", ml=330, description="Soft red wine with plum and berry flavors.")
    wine55_a = Wine(shop_id=shop_a.id, name="Heinken", short_name="HEI650", ml=650, description="Crisp white wine with green apple notes.")
    wine56_a = Wine(shop_id=shop_a.id, name="Haywords Gold", short_name="HAY180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine57_a = Wine(shop_id=shop_a.id, name="Haywords Gold", short_name="HAY90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine58_a = Wine(shop_id=shop_a.id, name="MC. XXX Rum", short_name="MCXXX750", ml=750, description="Soft red wine with plum and berry flavors.")
    wine59_a = Wine(shop_id=shop_a.id, name="MC. XXX Rum", short_name="MCXXX180", ml=180, description="Crisp white wine with green apple notes.")
    wine60_a = Wine(shop_id=shop_a.id, name="MC. XXX Rum", short_name="MCXXX90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine61_a = Wine(shop_id=shop_a.id, name="Banglore Rum", short_name="BAN90", ml=90, description="Crisp white wine with green apple notes.")
    wine62_a = Wine(shop_id=shop_a.id, name="Old Monk Rum", short_name="OLD180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine63_a = Wine(shop_id=shop_a.id, name="Old Monk Rum", short_name="OLD90", ml=90, description="Crisp white wine with green apple notes.")
    wine64_a = Wine(shop_id=shop_a.id, name="B.P. Rum", short_name="BPR90", ml=90, description="Soft red wine with plum and berry flavors.")
    wine65_a = Wine(shop_id=shop_a.id, name="W M Vodka", short_name="WLV180", ml=180, description="Crisp white wine with green apple notes.")
    wine66_a = Wine(shop_id=shop_a.id, name="Oxigen Vodka", short_name="OXI180", ml=180, description="Soft red wine with plum and berry flavors.")
    wine67_a = Wine(shop_id=shop_a.id, name="Breezer Orange", short_name="BREO275", ml=275, description="Crisp white wine with green apple notes.")
    wine68_a = Wine(shop_id=shop_a.id, name="Breezer Canberry", short_name="BREC275", ml=275, description="Soft red wine with plum and berry flavors.")
    wine69_a = Wine(shop_id=shop_a.id, name="B+ Canberry", short_name="B+C275", ml=275, description="Crisp white wine with green apple notes.")
    wine70_a = Wine(shop_id=shop_a.id, name="B+ Orange", short_name="B+O275", ml=275, description="Soft red wine with plum and berry flavors.")
    wine71_a = Wine(shop_id=shop_a.id, name="I.B. Black", short_name="IB750", ml=750, description="Crisp white wine with green apple notes.")

    wine1_b = Wine(shop_id=shop_b.id, name="Chardonnay", short_name="CHR", ml=750, description="Crisp white wine with green apple notes.")
    wine2_b = Wine(shop_id=shop_b.id, name="Merlot", short_name="MER", ml=750, description="Soft red wine with plum and berry flavors.")
    db.session.add_all([wine1_a, wine2_a,wine3_a,wine4_a,wine5_a,wine6_a,wine7_a,wine8_a,wine9_a,wine10_a,wine11_a,wine12_a,wine13_a,wine14_a,wine15_a,wine16_a,wine17_a,wine18_a,wine19_a,wine20_a,wine21_a,wine22_a,wine23_a,wine24_a,wine25_a,wine26_a,wine27_a,wine28_a,wine29_a,wine30_a,wine31_a,wine32_a,wine33_a,wine34_a,wine35_a,wine36_a,wine37_a,wine38_a,wine39_a,wine40_a,wine41_a,wine42_a,wine43_a,wine44_a,wine45_a,wine46_a,
                        wine47_a,wine48_a,wine49_a,wine50_a,wine51_a,wine52_a,wine53_a,wine54_a,wine55_a,wine56_a,wine57_a,wine58_a,wine59_a,wine60_a,wine61_a,wine62_a,wine63_a,wine64_a,wine65_a,wine66_a,wine67_a,wine68_a,wine69_a,wine70_a,wine71_a])
    wine2_b = Wine(shop_id=shop_b.id, name="Merlot", short_name="MER", ml=750, description="Soft red wine with plum and berry flavors.")
    db.session.add_all([wine1_b, wine2_b])
    db.session.commit()

    prices = [
        WinePrice(shop_id=shop_a.id, wine_id=wine1_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine2_a.id, price=12.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine3_a.id, price=13.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine4_a.id, price=14.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine5_a.id, price=15.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine6_a.id, price=16.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine7_a.id, price=12.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine8_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine9_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine10_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine11_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine12_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine13_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine14_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine15_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine16_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine17_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine18_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine19_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine20_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine21_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine22_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine23_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine24_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine25_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine26_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine27_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine28_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine29_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine30_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine31_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine32_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine33_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine34_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine35_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine36_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine37_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine38_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine39_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine40_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine41_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine42_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine43_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine44_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine45_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine46_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine47_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine48_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine49_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine50_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine51_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine52_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine53_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine54_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine55_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine56_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine57_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine58_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine59_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine60_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine61_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine62_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine63_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine64_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine65_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine66_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine67_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine68_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine69_a.id, price=18.25),
        WinePrice(shop_id=shop_a.id, wine_id=wine70_a.id, price=130),
        WinePrice(shop_id=shop_a.id, wine_id=wine71_a.id, price=18.25),
        WinePrice(shop_id=shop_b.id, wine_id=wine1_b.id, price=24.75),
        WinePrice(shop_id=shop_b.id, wine_id=wine2_b.id, price=24.75),
    ]
    db.session.add_all(prices)
    db.session.commit()

    shop_a.workers.append(worker)
    shop_b.workers.append(worker)
    db.session.commit()

    print("Database initialized with sample data.")
