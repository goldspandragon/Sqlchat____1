-- ===============================================
-- Base de datos: ClientesDB
-- Descripción: Datos de ejemplo para pruebas web
-- ===============================================

-- Si la tabla ya existe, eliminarla primero
DROP TABLE IF EXISTS clientes;

-- Crear tabla de clientes (compatible con SQLite)
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT,
    edad INTEGER,
    gasto_total REAL
);

-- Insertar datos de ejemplo
INSERT INTO clientes (nombre, ciudad, edad, gasto_total) VALUES ('Juan Pérez', 'Santiago', 29, 1500.50);
INSERT INTO clientes (nombre, ciudad, edad, gasto_total) VALUES ('María Gómez', 'Valparaíso', 34, 2300.00);
INSERT INTO clientes (nombre, ciudad, edad, gasto_total) VALUES ('Carlos López', 'Concepción', 42, 890.75);
INSERT INTO clientes (nombre, ciudad, edad, gasto_total) VALUES ('Ana Torres', 'Antofagasta', 25, 3000.10);
INSERT INTO clientes (nombre, ciudad, edad, gasto_total) VALUES ('Pedro Sánchez', 'Santiago', 31, 1750.90);
