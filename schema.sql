-- categories: дерево категорий с неограниченной вложенностью
-- parent_id ссылается на эту же таблицу, NULL = корневая категория
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    parent_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

