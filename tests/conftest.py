"""
Fixtures для тестирования: БД, клиенты, заказы, товары.
Использует реальную PostgreSQL из настроек приложения.
НЕ очищает и НЕ пересоздаёт таблицы — работает с существующими данными.
Все изменения откатываются через SAVEPOINT.
"""

import pytest
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db, SessionLocal, engine
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem
from app.main import app
from app.config import settings


@pytest.fixture
def db_session():
    """Создаёт сессию БД для теста с откатом через SAVEPOINT.
    
    Использует существующую БД из настроек.
    Все изменения откатываются после теста, даже если тест вызывал commit().
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    # Начинаем SAVEPOINT — вложенную транзакцию
    nested = connection.begin_nested()
    
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        """После каждого commit() в тесте — создаём новый SAVEPOINT."""
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    try:
        yield session
    finally:
        session.close()
        # Откатываем внешний transaction — все изменения теста исчезают
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """HTTP клиент с переопределённой БД."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def category(db_session):
    """Создаёт тестовую категорию (откатится после теста)."""
    cat = Category(name="Тестовая категория")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture
def product(db_session, category):
    """Создаёт тестовый товар (откатится после теста)."""
    prod = Product(
        name="Тестовый товар",
        quantity=100,
        price=1500.00,
        category_id=category.id,
    )
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)
    return prod


@pytest.fixture
def client_model(db_session):
    """Создаёт тестового клиента (модель) (откатится после теста)."""
    cli = Client(
        name="Тестовый Клиент",
        address="г. Москва, ул. Тестовая, д. 1",
    )
    db_session.add(cli)
    db_session.commit()
    db_session.refresh(cli)
    return cli


@pytest.fixture
def order(db_session, client_model):
    """Создаёт тестовый заказ (откатится после теста)."""
    ord = Order(client_id=client_model.id)
    db_session.add(ord)
    db_session.commit()
    db_session.refresh(ord)
    return ord


@pytest.fixture
def order_item(db_session, order, product):
    """Создаёт тестовую позицию заказа (откатится после теста)."""
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        price=product.price,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item
