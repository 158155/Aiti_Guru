-- categories: дерево категорий с неограниченной вложенностью
-- parent_id ссылается на эту же таблицу, NULL = корневая категория
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    parent_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- products: номенклатура
-- quantity — остаток на складе, price — текущая цена
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 0,
    price       DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

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
