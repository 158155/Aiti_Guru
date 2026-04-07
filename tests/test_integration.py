"""
Интеграционные тесты: health check, полный цикл заказа.
"""

import pytest
from fastapi import status
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem


class TestHealthCheck:
    """Тесты эндпоинта health."""

    def test_health_check_returns_ok(self, client):
        """Health check возвращает статус ok."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"


class TestFullOrderCycle:
    """Тесты полного цикла заказа."""

    def test_full_order_cycle(self, client, db_session):
        """Полный цикл: клиент → заказ → добавление товаров → проверка."""
        # 1. Создаём клиента
        client_data = {"name": "Иван Петров", "address": "г. Москва, ул. Ленина, 10"}
        # Прямого эндпоинта для клиентов нет, создаём через БД
        db_client = Client(**client_data)
        db_session.add(db_client)
        db_session.commit()
        db_session.refresh(db_client)
        
        # 2. Создаём категории и товары
        root_cat = Category(name="Электроника")
        db_session.add(root_cat)
        db_session.flush()
        
        product1 = Product(name="Смартфон", quantity=50, price=25000.0, category_id=root_cat.id)
        db_session.add(product1)
        db_session.flush()
        
        product2 = Product(name="Наушники", quantity=100, price=3500.0, category_id=root_cat.id)
        db_session.add(product2)
        db_session.flush()
        
        # 3. Создаём заказ
        db_order = Order(client_id=db_client.id)
        db_session.add(db_order)
        db_session.commit()
        db_session.refresh(db_order)
        
        # 4. Добавляем товары в заказ
        response1 = client.post(
            f"/api/orders/{db_order.id}/items",
            json={"product_id": product1.id, "quantity": 2},
        )
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["product_id"] == product1.id
        assert response1.json()["quantity"] == 2
        assert response1.json()["price"] == product1.price
        
        response2 = client.post(
            f"/api/orders/{db_order.id}/items",
            json={"product_id": product2.id, "quantity": 1},
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["product_id"] == product2.id
        
        # 5. Проверяем, что позиция заказа создана
        # (API НЕ уменьшает остаток на складе — это отдельная операция)
        item1 = db_session.query(OrderItem).filter(
            OrderItem.order_id == db_order.id,
            OrderItem.product_id == product1.id
        ).first()
        assert item1 is not None
        assert item1.quantity == 2
        
        item2 = db_session.query(OrderItem).filter(
            OrderItem.order_id == db_order.id,
            OrderItem.product_id == product2.id
        ).first()
        assert item2 is not None
        assert item2.quantity == 1
