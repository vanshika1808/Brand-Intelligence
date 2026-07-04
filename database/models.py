from sqlalchemy.orm import declarative_base

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
Base = declarative_base()


class Brand(Base):

    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String)


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    brand_id = Column(Integer, ForeignKey("brands.id"))

    product_name = Column(String)

    amazon_asin = Column(String)

    flipkart_url = Column(Text)


class Mention(Base):

    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True)

    brand_id = Column(Integer)

    product_id = Column(Integer)

    source = Column(String)

    title = Column(Text)

    content = Column(Text)

    author = Column(String)

    rating = Column(Float)

    score = Column(Integer)

    created_at = Column(DateTime)

    sentiment = Column(String)

    cluster_id = Column(Integer)