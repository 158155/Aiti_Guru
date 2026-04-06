from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    """Схема для добавления товара в заказ"""
    product_id: int = Field(..., description="ID товара", gt=0)
    quantity: int = Field(..., description="Количество товара", gt=0)



class OrderItemResponse(BaseModel):
    """Схема для ответа для позиции товара"""
    order_id: int
    product_id: int
    quantity: int
    price: float


    model_config = ConfigDict(from_attributes=True)
    