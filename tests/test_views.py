"""
Тесты представления top5_products_last_month.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import text
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem


class TestTop5ProductsView:
    """Тесты представления top5_products_last_month."""

    def test_view_returns_top_selling_products(self, db_session):
        """Представление возвращает топ-5 товаров по продажам."""
        # Создаём структуру: категория → товар → клиент → заказ → позиция
        root_cat = Category(name="Корневая категория")
        db_session.add(root_cat)
        db_session.flush()
        
        product = Product(name="Топовый товар", quantity=100, price=500.0, category_id=root_cat.id)
        db_session.add(product)
        db_session.flush()
        
        client = Client(name="Тестовый клиент", address="Москва")
        db_session.add(client)
        db_session.flush()
        
        # Заказ за последние 30 дней
        order = Order(client_id=client.id)
        db_session.add(order)
        db_session.flush()
        
        # Позиция заказа
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=10,
            price=product.price,
        )
        db_session.add(item)
        db_session.commit()
        
        # Запрос к представлению
        result = db_session.execute(text("SELECT * FROM top5_products_last_month"))
        rows = result.fetchall()
        
        # Проверяем, что товар попал в результат
        assert len(rows) >= 1
        
        # Проверяем поля
        row = rows[0]
        assert row.product_name == "Топовый товар"
        assert row.total_quantity_sold == 10

    def test_view_recursive_cte_finds_root_category(self, db_session):
        """Рекурсивный CTE правильно находит корневую категорию."""
        # Создаём иерархию: Корень → Подкатегория → Конечная категория
        root = Category(name="Корень")
        db_session.add(root)
        db_session.flush()
        
        child = Category(name="Подкатегория", parent_id=root.id)
        db_session.add(child)
        db_session.flush()
        
        leaf = Category(name="Конечная", parent_id=child.id)
        db_session.add(leaf)
        db_session.flush()
        
        product = Product(name="Глубокий товар", quantity=50, price=300.0, category_id=leaf.id)
        db_session.add(product)
        db_session.flush()
        
        client = Client(name="Покупатель", address="СПб")
        db_session.add(client)
        db_session.flush()
        
        order = Order(client_id=client.id)
        db_session.add(order)
        db_session.flush()
        
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=5,
            price=product.price,
        )
        db_session.add(item)
        db_session.commit()
        
        # Запрос к представлению
        result = db_session.execute(text("SELECT * FROM top5_products_last_month"))
        rows = result.fetchall()
        
        assert len(rows) >= 1
        
        # Проверяем, что корневая категория определена правильно
        row = rows[0]
        assert row.product_name == "Глубокий товар"
        assert row.category_level1 == "Корень"
        assert row.total_quantity_sold == 5

    def test_view_filters_last_30_days(self, db_session):
        """Представление фильтрует только заказы за последние 30 дней."""
        root_cat = Category(name="Корень")
        db_session.add(root_cat)
        db_session.flush()
        
        product = Product(name="Старый товар", quantity=100, price=200.0, category_id=root_cat.id)
        db_session.add(product)
        db_session.flush()
        
        client = Client(name="Клиент", address="Казань")
        db_session.add(client)
        db_session.flush()
        
        # Заказ 60 дней назад (вне диапазона)
        old_order = Order(
            client_id=client.id,
        )
        db_session.add(old_order)
        db_session.flush()
        
        # Устанавливаем старую дату вручную
        old_date = datetime.now() - timedelta(days=60)
        db_session.execute(
            text("UPDATE orders SET created_at = :date WHERE id = :id"),
            {"date": old_date, "id": old_order.id},
        )
        db_session.flush()
        
        old_item = OrderItem(
            order_id=old_order.id,
            product_id=product.id,
            quantity=100,
            price=product.price,
        )
        db_session.add(old_item)
        db_session.commit()
        
        # Запрос к представлению - старых заказов быть не должно
        result = db_session.execute(text("SELECT * FROM top5_products_last_month"))
        rows = result.fetchall()
        
        # "Старый товар" не должен попасть в топ-5
        product_names = [row.product_name for row in rows]
        assert "Старый товар" not in product_names

    def test_view_aggregates_quantities(self, db_session):
        """Представление суммирует количества из多个 заказов."""
        root_cat = Category(name="Корень")
        db_session.add(root_cat)
        db_session.flush()
        
        product = Product(name="Суммируемый товар", quantity=100, price=400.0, category_id=root_cat.id)
        db_session.add(product)
        db_session.flush()
        
        client = Client(name="Клиент", address="Екб")
        db_session.add(client)
        db_session.flush()
        
        # Два заказа с одним товаром
        order1 = Order(client_id=client.id)
        db_session.add(order1)
        db_session.flush()
        
        order2 = Order(client_id=client.id)
        db_session.add(order2)
        db_session.flush()
        
        item1 = OrderItem(order_id=order1.id, product_id=product.id, quantity=3, price=product.price)
        db_session.add(item1)
        
        item2 = OrderItem(order_id=order2.id, product_id=product.id, quantity=7, price=product.price)
        db_session.add(item2)
        db_session.commit()
        
        # Запрос к представлению
        result = db_session.execute(text("SELECT * FROM top5_products_last_month"))
        rows = result.fetchall()
        
        assert len(rows) >= 1
        
        # Проверяем суммирование
        row = rows[0]
        assert row.product_name == "Суммируемый товар"
        assert row.total_quantity_sold == 10

    def test_view_handles_null_category(self, db_session):
        """Представление обрабатывает товары без категории."""
        product = Product(name="Без категории", quantity=50, price=100.0, category_id=None)
        db_session.add(product)
        db_session.flush()
        
        client = Client(name="Клиент", address="Нск")
        db_session.add(client)
        db_session.flush()
        
        order = Order(client_id=client.id)
        db_session.add(order)
        db_session.flush()
        
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            price=product.price,
        )
        db_session.add(item)
        db_session.commit()
        
        # Запрос к представлению - не должно быть ошибок
        result = db_session.execute(text("SELECT * FROM top5_products_last_month"))
        rows = result.fetchall()
        
        # Товар должен быть в результате с COALESCE
        assert len(rows) >= 1
