-- ==============================================
-- Base de datos: EmpresaVentasDB
-- Compatible con SQLite
-- ==============================================

DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS regiones;

CREATE TABLE regiones (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    region_id INTEGER,
    edad INTEGER,
    fecha_registro DATE,
    FOREIGN KEY (region_id) REFERENCES regiones(id)
);

CREATE TABLE empleados (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    puesto TEXT NOT NULL,
    region_id INTEGER,
    salario REAL,
    FOREIGN KEY (region_id) REFERENCES regiones(id)
);

CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL
);

CREATE TABLE ventas (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    empleado_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    fecha DATE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Regiones
INSERT INTO regiones (nombre) VALUES
('Santiago'),
('Valparaíso'),
('Concepción'),
('Antofagasta');

-- Clientes
INSERT INTO clientes (nombre, ciudad, region_id, edad, fecha_registro) VALUES
('Juan Pérez', 'Santiago', 1, 32, '2021-02-10'),
('María López', 'Viña del Mar', 2, 28, '2022-07-15'),
('Pedro Gómez', 'Concepción', 3, 41, '2020-12-01'),
('Laura Díaz', 'Santiago', 1, 35, '2023-01-20'),
('Andrés Silva', 'Antofagasta', 4, 29, '2022-03-10'),
('Claudia Rivas', 'Santiago', 1, 45, '2021-11-02');

-- Empleados
INSERT INTO empleados (nombre, puesto, region_id, salario) VALUES
('Carlos Soto', 'Vendedor', 1, 1200),
('Ana Torres', 'Vendedora', 2, 1100),
('Luis Morales', 'Supervisor', 1, 1800),
('Patricia Ruiz', 'Vendedora', 3, 1150),
('Ricardo Fuentes', 'Vendedor', 4, 1300);

-- Productos
INSERT INTO productos (nombre, categoria, precio) VALUES
('Notebook Lenovo', 'Tecnología', 750),
('Mouse Logitech', 'Accesorios', 25),
('Silla Ergonómica', 'Muebles', 200),
('Monitor Samsung', 'Tecnología', 300),
('Teclado Mecánico', 'Accesorios', 90),
('Escritorio OfficePro', 'Muebles', 350);

-- Ventas
INSERT INTO ventas (cliente_id, empleado_id, producto_id, cantidad, fecha) VALUES
(1, 1, 1, 2, '2023-01-15'),
(2, 2, 2, 3, '2023-03-11'),
(3, 4, 3, 1, '2023-04-05'),
(4, 1, 4, 2, '2023-06-09'),
(5, 5, 1, 1, '2023-07-21'),
(6, 3, 6, 1, '2023-09-13'),
(1, 1, 2, 5, '2024-01-10'),
(2, 2, 5, 2, '2024-02-19'),
(3, 4, 3, 3, '2024-03-25'),
(4, 1, 4, 1, '2024-04-17'),
(5, 5, 1, 4, '2024-05-08'),
(6, 3, 6, 2, '2024-06-22'),
(1, 1, 5, 1, '2024-07-15'),
(2, 2, 4, 3, '2024-08-09'),
(3, 4, 2, 2, '2024-09-12');
