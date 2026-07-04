from database.db import SessionLocal
from database.models import Brand, Product, Mention


# ---------------- PRODUCT ---------------- #


def get_all_products():

    session = SessionLocal()

    try:
        return session.query(Product).all()

    finally:
        session.close()


def get_product_by_id(product_id):

    session = SessionLocal()

    try:
        return session.query(Product).filter(
            Product.id == product_id
        ).first()

    finally:
        session.close()


def get_product_by_asin(asin):

    session = SessionLocal()

    try:
        return session.query(Product).filter(
            Product.amazon_asin == asin
        ).first()

    finally:
        session.close()


def get_products_with_asin():

    session = SessionLocal()

    try:
        return session.query(Product).filter(
            Product.amazon_asin != None
        ).all()

    finally:
        session.close()


def save_product(product):

    session = SessionLocal()

    try:
        session.add(product)
        session.commit()
        session.refresh(product)

        return product

    finally:
        session.close()

# ---------------- BRAND ---------------- #

def get_brand_by_name(name):

    session = SessionLocal()

    try:
        return session.query(Brand).filter(
            Brand.brand_name.ilike(name)
        ).first()

    finally:
        session.close()


def save_brand(brand):

    session = SessionLocal()

    try:
        session.add(brand)
        session.commit()
        session.refresh(brand)

        return brand

    finally:
        session.close()


# ---------------- MENTION ---------------- #

def save_mention(mention):

    session = SessionLocal()

    try:
        session.add(mention)
        session.commit()
        session.refresh(mention)

        return mention

    finally:
        session.close()


def mention_exists(product_id, content):

    session = SessionLocal()

    try:
        return session.query(Mention).filter(
            Mention.product_id == product_id,
            Mention.content == content
        ).first()

    finally:
        session.close()