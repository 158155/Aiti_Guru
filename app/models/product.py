from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    #Связь с категорией
    category = relationship("Category", back_populates="products", lazy="select")

    #Связь с позициями в заказе
    order_items = relationship("OrderItem", back_populates="product", lazy="select")

    def __repr__(self):
        return f"<Product=({self.id}, name='{self.name}', quantity={self.quantity}, price={self.price})>"
    