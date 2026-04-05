from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    #Связь с заказом и товаром
    order = relationship("Order", back_populates="order_items", lazy="select")
    product = relationship("Product", back_populates="order_items", lazy="select")  

    #Уникальность заказа и товара в заказе
    __table_args__ = (UniqueConstraint("order_id", "product_id", name="uq_order_product"),)


    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity}))>"