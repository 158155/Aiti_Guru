"""
Скрипт для создания тестовых данных:
- 100 товаров из раздела "Бытовая техника" в 5 категориях разной вложенности
- 10 тестовых клиентов
- 5 тестовых заказов с позициями
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem


def create_categories(db):
    """Создаёт иерархию категорий для бытовой техники."""
    print("Создание категорий...")

    # Корневая категория
    root = Category(name="Бытовая техника")
    db.add(root)
    db.flush()

    # Уровень 2
    large_appliances = Category(name="Крупная техника", parent_id=root.id)
    small_appliances = Category(name="Мелкая техника", parent_id=root.id)
    db.add_all([large_appliances, small_appliances])
    db.flush()

    # Уровень 3 (под Крупная техника)
    fridges = Category(name="Холодильники", parent_id=large_appliances.id)
    washing_machines = Category(name="Стиральные машины", parent_id=large_appliances.id)
    db.add_all([fridges, washing_machines])
    db.flush()

    # Уровень 3 (под Мелкая техника)
    kitchen = Category(name="Кухонная техника", parent_id=small_appliances.id)
    climate = Category(name="Климатическая техника", parent_id=small_appliances.id)
    db.add_all([kitchen, climate])
    db.flush()

    # Уровень 4 (под Кухонная техника)
    blenders = Category(name="Блендеры", parent_id=kitchen.id)
    microwaves = Category(name="Микроволновки", parent_id=kitchen.id)
    db.add_all([blenders, microwaves])
    db.flush()

    # Уровень 4 (под Климатическая техника)
    heaters = Category(name="Обогреватели", parent_id=climate.id)
    fans = Category(name="Вентиляторы", parent_id=climate.id)
    db.add_all([heaters, fans])
    db.flush()

    db.commit()

    categories = {
        "fridges": fridges.id,
        "washing_machines": washing_machines.id,
        "blenders": blenders.id,
        "microwaves": microwaves.id,
        "heaters": heaters.id,
        "fans": fans.id,
    }

    print(f"Создано {len(categories)} конечных категорий")
    return categories


def create_products(db, category_ids, count=100):
    """Создаёт товары в указанных категориях."""
    print(f"Создание {count} товаров...")

    # Шаблоны названий для каждой категории
    product_templates = {
        "fridges": [
            "Холодильник {brand} {model}",
            "Холодильник двухкамерный {brand}",
            "Холодильник Side-by-Side {brand}",
        ],
        "washing_machines": [
            "Стиральная машина {brand} {model}",
            "Стиральная машина автомат {brand}",
            "Стиральная машина узкая {brand}",
        ],
        "blenders": [
            "Блендер {brand} {model}",
            "Блендер погружной {brand}",
            "Блендер стационарный {brand}",
        ],
        "microwaves": [
            "Микроволновка {brand} {model}",
            "СВЧ-печь {brand}",
            "Микроволновая печь с грилем {brand}",
        ],
        "heaters": [
            "Обогреватель {brand} {model}",
            "Масляный обогреватель {brand}",
            "Конвектор {brand}",
        ],
        "fans": [
            "Вентилятор {brand} {model}",
            "Вентилятор напольный {brand}",
            "Вентилятор настольный {brand}",
        ],
    }

    brands = ["Samsung", "LG", "Bosch", "Electrolux", "Philips", "Panasonic", "Haier", "Midea", "Xiaomi", "Indesit"]
    models = ["Pro", "Plus", "Max", "Ultra", "Eco", "Smart", "Lite", "Premium", "Advanced", "Prime"]

    products = []
    # Распределяем товары по категориям (примерно поровну)
    products_per_category = count // len(category_ids)
    remainder = count % len(category_ids)

    for idx, (cat_key, cat_id) in enumerate(category_ids.items()):
        # Добавляем остаток к первым категориям
        cat_count = products_per_category + (1 if idx < remainder else 0)

        templates = product_templates[cat_key]

        for i in range(cat_count):
            template = templates[i % len(templates)]
            brand = random.choice(brands)
            model = random.choice(models)
            name = template.format(brand=brand, model=model)

            # Если такое имя уже есть, добавляем номер
            if i > 0:
                name = f"{name} #{i+1}"

            product = Product(
                name=name,
                quantity=random.randint(5, 100),
                price=round(random.uniform(1500, 85000), 2),
                category_id=cat_id,
            )
            products.append(product)

    db.bulk_save_objects(products, return_defaults=True)
    db.commit()

    print(f"Создано {len(products)} товаров")
    return products


def create_clients(db, count=10):
    """Создаёт тестовых клиентов."""
    print(f"Создание {count} клиентов...")

    client_data = [
        {"name": "Иванов Иван", "address": "г. Москва, ул. Ленина, д. 10, кв. 5"},
        {"name": "Петрова Мария", "address": "г. Санкт-Петербург, Невский пр., д. 25"},
        {"name": "Сидоров Алексей", "address": "г. Казань, ул. Баумана, д. 15"},
        {"name": "Козлова Елена", "address": "г. Новосибирск, Красный пр., д. 50"},
        {"name": "Новиков Дмитрий", "address": "г. Екатеринбург, ул. Мира, д. 8"},
        {"name": "Морозова Анна", "address": "г. Нижний Новгород, ул. Горького, д. 12"},
        {"name": "Волков Сергей", "address": "г. Самара, ул. Куйбышева, д. 30"},
        {"name": "Алексеева Ольга", "address": "г. Ростов-на-Дону, пр. Стачки, д. 45"},
        {"name": "Лебедев Павел", "address": "г. Краснодар, ул. Красная, д. 100"},
        {"name": "Семёнова Наталья", "address": "г. Воронеж, пр. Революции, д. 20"},
    ]

    clients = []
    for i in range(count):
        data = client_data[i % len(client_data)]
        # Добавляем номер если клиент не первый
        if i >= len(client_data):
            name = f"{data['name']} #{i+1}"
        else:
            name = data['name']
        
        client = Client(
            name=name,
            address=data['address'],
        )
        clients.append(client)

    db.add_all(clients)
    db.commit()

    # Обновляем ID
    for client in clients:
        db.refresh(client)

    print(f"Создано {len(clients)} клиентов")
    return clients


def create_orders(db, clients, products, count=50):
    """Создаёт тестовые заказы с позициями."""
    print(f"Создание {count} заказов...")

    # Диапазон дат: 01.01.2026 — 31.03.2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31, 23, 59, 59)
    date_range_seconds = int((end_date - start_date).total_seconds())

    orders = []
    for i in range(count):
        # Выбираем случайного клиента
        client = random.choice(clients)
        
        # Генерируем случайную дату в диапазоне
        random_seconds = random.randint(0, date_range_seconds)
        created_at = start_date + timedelta(seconds=random_seconds)
        
        # Создаём заказ с указанной датой
        order = Order(client_id=client.id, created_at=created_at)
        db.add(order)
        db.flush()
        
        # Добавляем 2-4 случайных товара в заказ
        num_items = random.randint(2, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            
            # Проверяем остаток
            if product.quantity < quantity:
                quantity = product.quantity
            
            if quantity > 0:
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price,
                )
                db.add(item)
                
                # Уменьшаем остаток на складе
                product.quantity -= quantity
        
        db.flush()
        db.refresh(order)
        orders.append(order)
        
        print(f"Заказ #{order.id}: клиент={client.name}, дата={created_at.strftime('%d.%m.%Y')}, товаров={len(selected_products)}")

    db.commit()
    print(f"Создано {len(orders)} заказов")
    return orders


def print_category_tree(db):
    """Выводит дерево категорий для наглядности."""
    categories = db.query(Category).all()

    print("\nДерево категорий:")
    print("-" * 70)

    def print_tree(parent_id=None, level=0):
        for cat in categories:
            if cat.parent_id == parent_id:
                prefix = "  " * level + ("└─ " if level > 0 else "")
                children_count = sum(1 for c in categories if c.parent_id == cat.id)
                products_count = db.query(Product).filter(Product.category_id == cat.id).count()
                print(f"{prefix}{cat.name} [ID={cat.id}] (товаров: {products_count}, подкатегорий: {children_count})")
                print_tree(cat.id, level + 1)

    print_tree()
    print("-" * 70)


def print_summary(db, clients, orders, products):
    """Выводит сводку по созданным данным."""
    print("\nСводка:")
    print(f"   Категорий конечных: 6 (Холодильники, Стиральные машины, Блендеры, Микроволновки, Обогреватели, Вентиляторы)")
    print(f"   Товаров создано: {len(products)}")
    print(f"   Клиентов создано: {len(clients)}")
    print(f"   Заказов создано: {len(orders)}")
    
    # Считаем позиции
    total_items = db.query(OrderItem).join(Order).filter(Order.id.in_([o.id for o in orders])).count()
    print(f"   Позиций в заказах: {total_items}")


def main():
    """Основная функция."""
    print("=" * 70)
    print("Создание тестовых данных: Бытовая техника + клиенты + заказы")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Проверяем подключение к БД
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("Подключение к БД успешно\n")

        # Создаём категории
        category_ids = create_categories(db)

        # Создаём товары
        products = create_products(db, category_ids, count=100)

        # Создаём клиентов
        clients = create_clients(db, count=10)

        # Создаём заказы
        orders = create_orders(db, clients, products, count=50)

        # Выводим дерево категорий
        print_category_tree(db)

        # Выводим сводку
        print_summary(db, clients, orders, products)

        print("\nГотово!")

    except Exception as e:
        print(f"\nОшибка: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
