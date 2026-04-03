from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    #Связь с родительской категорией (самоссылка)
    parent = relationship("Category", remote_side=[id], backref="children", lazy="select")

    #Связь с товарами
    products = relationship("Product", back_populates="category", lazy="select")

    def __repr__(self):
        return f"<Category=({self.id}, name='{self.name}')>"
    
