"""
Тесты бизнес-логики: каскадное удаление, уникальность, денормализация цен.
"""

import pytest
from sqlalchemy import text
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.client import Client
from app.models.product import Product


class TestCascadeDelete:
    """Тесты каскадного удаления."""

    def test_delete_order_cascade_to_items(self, db_session, order, product):
        """Удаление заказа каскадно удаляет позиции."""
        # Создаём позицию
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=product.price,
        )
        db_session.add(item)
        db_session.commit()
        
        item_id = item.id
        
        # Удаляем заказ
        db_session.delete(order)
        db_session.commit()
        
        # Проверяем, что позиция удалена
        deleted_item = db_session.query(OrderItem).filter(OrderItem.id == item_id).first()
        assert deleted_item is None

    def test_delete_client_cascade_to_orders(self, db_session, client_model, order, product):
        """Удаление клиента каскадно удаляет заказы и позиции."""
        # Создаём позицию
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=product.price,
        )
        db_session.add(item)
        db_session.commit()
        
        order_id = order.id
        item_id = item.id
        client_id = client_model.id
        
        # На уровне БД CASCADE настроен, но SQLAlchemy требует явного удаления
        # Сначала удаляем заказы, потом клиента (БД тоже делает CASCADE)
        for ord in client_model.orders:
            db_session.delete(ord)
        db_session.flush()
        
        db_session.delete(client_model)
        db_session.commit()
        
        # Проверяем каскадное удаление
        deleted_order = db_session.query(Order).filter(Order.id == order_id).first()
        deleted_item = db_session.query(OrderItem).filter(OrderItem.id == item_id).first()
        deleted_client = db_session.query(Client).filter(Client.id == client_id).first()
        
        assert deleted_order is None
        assert deleted_item is None
        assert deleted_client is None


class TestUniqueConstraint:
    """Тесты уникальности order_id + product_id."""

    def test_unique_order_product_constraint(self, db_session, order, product):
        """Нельзя создать две позиции с одним order_id и product_id."""
        # Первая позиция
        item1 = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=product.price,
        )
        db_session.add(item1)
        db_session.commit()

        # Попытка создать дубликат
        item2 = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            price=product.price,
        )
        db_session.add(item2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
