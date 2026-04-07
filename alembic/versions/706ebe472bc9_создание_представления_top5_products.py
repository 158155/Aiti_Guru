"""создание представление top5_products

Revision ID: 706ebe472bc9
Revises: 7611f7c997cc
Create Date: 2026-04-07 14:54:52.628524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '706ebe472bc9'
down_revision: Union[str, None] = '7611f7c997cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VIEW_NAME = "top5_products_last_month"

VIEW_SQL = """
CREATE OR REPLACE VIEW top5_products_last_month AS
-- Товары, которые реально продавались за 30 дней
WITH RECURSIVE recent_products AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS total_quantity_sold
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.created_at >= NOW() - INTERVAL '30 days'
    GROUP BY oi.product_id
),
-- Рекурсия только для проданных товаров
category_root AS (
    -- Стартовая точка: категория проданного товара
    SELECT
        rp.product_id,
        p.name AS product_name,
        c.id AS category_id,
        c.parent_id,
        COALESCE(c.name, 'Без категории') AS category_name,
        1 AS level
    FROM recent_products rp
    JOIN products p ON p.id = rp.product_id
    LEFT JOIN categories c ON p.category_id = c.id

    UNION ALL

    -- Шаг рекурсии: идём к родителю, пока parent_id не станет null
    SELECT
        cr.product_id,
        cr.product_name,
        cr.category_id,
        c.parent_id,
        c.name AS category_name,
        cr.level + 1
    FROM category_root cr
    JOIN categories c ON c.id = cr.parent_id
    WHERE cr.parent_id IS NOT NULL
),
-- Оставляем только корневую запись (максимальный level) для каждого товара
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
    rp.total_quantity_sold
FROM recent_products rp
JOIN root_categories rc ON rc.product_id = rp.product_id
ORDER BY rp.total_quantity_sold DESC
LIMIT 5;
"""


def upgrade() -> None:
    op.execute(VIEW_SQL)


def downgrade() -> None:
    op.execute(f"DROP VIEW IF EXISTS {VIEW_NAME}")
