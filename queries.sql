# 2.1. Сумма товаров по каждому клиенту
SELECT
    c.name        AS client_name,
    SUM(oi.quantity * oi.price) AS total_sum
FROM clients c
JOIN orders o      ON o.id = c.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY c.id, c.name
ORDER BY total_sum DESC;

# 2.2. Сколько дочерних категорий первого уровня у каждой категории
SELECT
    cat.name       AS category_name,
    COUNT(child.id) AS children_count
FROM categories cat
LEFT JOIN categories child ON child.parent_id = cat.id
GROUP BY cat.id, cat.name
ORDER BY children_count DESC, cat.name;

# 2.3.1. Выборка из view «топ-5 за последний месяц»
# сам view определён в schema.sql
SELECT
    product_name,
    category_level1,
    total_quantity_sold
FROM top5_products_last_month;