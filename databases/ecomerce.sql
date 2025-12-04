-- ===============================
--   BASE ECOMMERCE COMPLETA
-- ===============================

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS customer_address;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS activity_logs;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER,
    price REAL NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    last_update TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE customer_address (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    street TEXT,
    city TEXT,
    country TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total REAL,
    status TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    subtotal REAL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    method TEXT,
    amount REAL,
    paid_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ==== INSERTS DE PRUEBA ====

INSERT INTO users (fullname, email, password) VALUES
 ("Juan Pérez", "juan@example.com", "1234"),
 ("María López", "maria@example.com", "abcd"),
 ("Carlos Silva", "carlos@example.com", "pass");

INSERT INTO categories (name, description) VALUES
 ("Tecnología", "Dispositivos electrónicos"),
 ("Hogar", "Artículos para el hogar"),
 ("Ropa", "Moda para adultos y niños");

INSERT INTO products (name, category_id, price, description) VALUES
 ("Laptop Gamer", 1, 1200.50, "Laptop de alto rendimiento"),
 ("Aspiradora Robot", 2, 350.99, "Robot inteligente"),
 ("Polera Azul", 3, 19.99, "Polera básica azul");

INSERT INTO inventory (product_id, quantity) VALUES
 (1, 10), (2, 25), (3, 200);

INSERT INTO orders (user_id, total, status) VALUES
 (1, 1200.50, "Pagado"),
 (2, 370.99, "Pendiente");

INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES
 (1, 1, 1, 1200.50),
 (2, 2, 1, 350.99),
 (2, 3, 1, 19.99);

INSERT INTO payments (order_id, method, amount) VALUES
 (1, "Tarjeta Crédito", 1200.50);

INSERT INTO reviews (user_id, product_id, rating, comment) VALUES
 (1, 1, 5, "Excelente laptop!"),
 (2, 2, 4, "Funciona bien.");

INSERT INTO customer_address (user_id, street, city, country) VALUES
 (1, "Av. Central 123", "Santiago", "Chile"),
 (2, "Calle Norte 456", "Valparaíso", "Chile");

INSERT INTO activity_logs (user_id, action) VALUES
 (1, "Inició sesión"),
 (2, "Realizó una compra");
