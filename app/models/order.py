from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    #Связь с клиентом
    client = relationship("Client", back_populates="orders", lazy="select")

    #Связь с позициями заказа (каскадное удаление)
    order_items = relationship("OrderItem", back_populates="order", lazy="select", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, client_id={self.client_id}, created_at={self.created_at})>"
    