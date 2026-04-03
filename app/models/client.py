from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)

    #Связь с заказами
    orders = relationship("Order", back_populates="client", lazy="select")


    def __repr__(self):
        return f"<Client=({self.id}, name='{self.name}', email='{self.email}')>"