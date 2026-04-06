-- categories: дерево категорий с неограниченной вложенностью
-- parent_id ссылается на эту же таблицу, NULL = корневая категория
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    parent_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_categories_parent_id ON categories(parent_id);

-- products: номенклатура
-- quantity — остаток на складе, price — текущая цена
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 0,
    price       DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_products_category_id ON products(category_id);

-- clients: покупатели
CREATE TABLE clients (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    address TEXT
);

-- orders: шапка заказа
-- created_at ставится автоматически, но можно переопределить при импорте
CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    client_id   INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_client_id ON orders(client_id);

-- order_items: строки заказа
-- price дублируется из products на момент оформления, чтобы история покупок не менялась
-- unique(order_id, product_id) не даёт добавить один товар дважды — при повторном добавлении нужно делать update
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE ON UPDATE CASCADE,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    quantity    INTEGER NOT NULL,
    price       DECIMAL(10,2) NOT NULL,

    CONSTRAINT uq_order_product UNIQUE (order_id, product_id)
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- top5_products_last_month: отчёт «самые покупаемые товары за 30 дней»
-- рекурсивный CTE поднимается по дереву категорий до корня, чтобы показать категорию 1-го уровня
CREATE OR REPLACE VIEW top5_products_last_month AS
WITH RECURSIVE category_root AS (
    -- стартовая точка: категория, к которой привязан товар
    SELECT
        p.id            AS product_id,
        p.name          AS product_name,
        c.id            AS category_id,
        c.parent_id,
        c.name          AS category_name,
        1               AS level
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id

    UNION ALL

    -- шаг рекурсии: идём к родителю, пока parent_id не станет null
    SELECT
        cr.product_id,
        cr.product_name,
        cr.category_id,
        c.parent_id,
        c.name          AS category_name,
        cr.level + 1
    FROM category_root cr
    JOIN categories c ON c.id = cr.parent_id
    WHERE cr.parent_id IS NOT NULL
),
-- оставляем только корневую запись (максимальный level) для каждого товара
root_categories AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        product_name,
        category_name AS category_level1
    FROM category_root
    ORDER BY product_id, level DESC
)
SELECT
    rc.product_name,
    rc.category_level1,
    SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN orders o          ON o.id = oi.order_id
JOIN root_categories rc ON rc.product_id = oi.product_id
WHERE o.created_at >= NOW() - INTERVAL '30 days'
GROUP BY rc.product_id, rc.product_name, rc.category_level1
ORDER BY total_quantity_sold DESC
LIMIT 5;