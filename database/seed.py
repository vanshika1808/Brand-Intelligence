from sqlalchemy import func

from database.db import SessionLocal
from database.models import Brand

session = SessionLocal()

brands = [

    Brand(brand_name="Zepto"),

    Brand(brand_name="Blinkit"),

    Brand(brand_name="boAt"),

    Brand(brand_name="Noise"),

    Brand(brand_name="Amul"),

    Brand(brand_name="Lux"),

    Brand(brand_name="Hocco"),

    Brand(brand_name="Swiggy")

]

for brand in brands:

    existing = session.query(Brand).filter(
        func.lower(Brand.brand_name) == brand.brand_name.lower()
    ).first()

    if existing is None:
        session.add(brand)

session.commit()

session.close()

print("Brands Inserted Successfully")