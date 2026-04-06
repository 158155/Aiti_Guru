import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/orders', tags=['orders'])


@router.get('/{order_id}/items', response_model=OrderItemResponse)
def add_item_to_order(
    order_id: int,
    item_data: OrderItemCreate,
    db: Session = Depends(get_db)
):
    """Добавить товар в заказ.
    
    Если товар уже есть в заказе - увеличивается его количество (upsert).
    Если товара нет в наличии - возвращается ошибка.
    """
    #Проверяем существование заказа
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        logger.warning("Заказ не найден: order_id=%s", order_id)
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    #Проверяем существование товара
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        logger.warning("Товар не найден: product_id=%s", item_data.product_id)
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    #Проверяем наличие товара на складе
    if product.quantity < item_data.quantity:
        logger.warning("Недостаточно товара: product_id=%s, запрошено=%s, на складе=%s",
                        item_data.product_id, item_data.quantity, product.quantity) 
        raise HTTPException(status_code=400, detail="Недостаточно товара на складе. Доступно: {product.quantity}")
    
    #Ищем товар в заказе (существующую позицию)
    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.product_id == item_data.product_id
    ).first()
    
    if existing_item:
        #Проверяем, хватил ли товара на складе (сумма текущего + нового)
        if existing_item.quantity + item_data.quantity > product.quantity:
            logger.warning("Недостаточно товара: product_id=%s, запрошено=%s, на складе=%s",
                            item_data.product_id, item_data.quantity, product.quantity) 
            raise HTTPException(status_code=400, detail="Недостаточно товара на складе. Доступно: {product.quantity}")
        
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
        logger.info("Товар добавлен в заказ: order_id=%s, product_id=%s, quantity=%s",
                     order_id, item_data.product_id, item_data.quantity)
        
        return OrderItemResponse(
            order_id=existing_item.order_id,
            product_id=existing_item.product_id,
            quantity=existing_item.quantity,
            price=existing_item.price
        )
    else:
        #Создаём новую позицию в заказе
        new_item = OrderItem(
            order_id=order_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price
        )
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        logger.info("Товар добавлен в заказ: order_id=%s, product_id=%s, quantity=%s",
                     order_id, item_data.product_id, item_data.quantity)
        
        return OrderItemResponse(
            order_id=new_item.order_id,
            product_id=new_item.product_id,
            quantity=new_item.quantity,
            price=new_item.price
        )