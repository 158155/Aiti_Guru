"""
Тесты API заказов: добавление товара, ошибки, upsert-логика.
"""

import pytest
from fastapi import status


class TestAddItemToOrder:
    """Тесты эндпоинта POST /api/orders/{order_id}/items"""

    def test_add_item_success(self, client, order, product):
        """Успешное добавление товара в заказ."""
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 5},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["order_id"] == order.id
        assert data["product_id"] == product.id
        assert data["quantity"] == 5
        assert data["price"] == product.price

    def test_add_item_to_nonexistent_order(self, client, product):
        """Добавление товара в несуществующий заказ → 404."""
        response = client.post(
            "/api/orders/99999/items",
            json={"product_id": product.id, "quantity": 1},
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Заказ не найден" in response.json()["detail"]

    def test_add_nonexistent_product(self, client, order):
        """Добавление несуществующего товара → 404."""
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": 99999, "quantity": 1},
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Товар не найден" in response.json()["detail"]

    def test_insufficient_stock(self, client, order, product, db_session):
        """Превышение остатка на складе → 400."""
        # Уменьшаем остаток товара
        product.quantity = 3
        db_session.commit()
        
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 10},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in response.json()["detail"]

    def test_upsert_logic(self, client, order, product):
        """Upsert: повторное добавление товара увеличивает количество."""
        # Первое добавление
        response1 = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 3},
        )
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["quantity"] == 3
        
        # Второе добавление того же товара
        response2 = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 7},
        )
        assert response2.status_code == status.HTTP_200_OK
        # Количество должно суммироваться
        assert response2.json()["quantity"] == 10

    def test_upsert_with_stock_check(self, client, order, product, db_session):
        """Upsert с проверкой: сумма текущего и нового > остатка → 400."""
        # Добавляем товар с количеством 5
        client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 5},
        )
        
        # Уменьшаем остаток так, чтобы суммарно не хватило
        product.quantity = 8
        db_session.commit()
        
        # Пытаемся добавить ещё 5 (5+5=10 > 8)
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 5},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in response.json()["detail"]

    def test_price_is_denormalized(self, client, order, product, db_session):
        """Цена фиксируется на момент добавления в заказ."""
        original_price = product.price
        
        # Добавляем товар
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 1},
        )
        assert response.json()["price"] == original_price
        
        # Меняем цену товара
        product.price = 9999.99
        db_session.commit()
        
        # Добавляем ещё раз - должна остаться старая цена
        response2 = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 1},
        )
        # Для upsert цена не меняется, она была установлена при первом создании
        assert response2.json()["price"] == original_price

    def test_validation_error_zero_quantity(self, client, order, product):
        """Валидация: quantity=0 → 422."""
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": 0},
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_negative_quantity(self, client, order, product):
        """Валидация: quantity<0 → 422."""
        response = client.post(
            f"/api/orders/{order.id}/items",
            json={"product_id": product.id, "quantity": -5},
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
