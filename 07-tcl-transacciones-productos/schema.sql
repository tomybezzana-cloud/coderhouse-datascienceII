-- Esquema base para la práctica de TCL (BEGIN / COMMIT / ROLLBACK).
-- Se recrea desde cero antes de cada caso para que los tres partan siempre
-- del mismo estado inicial y sean reproducibles.

DROP TABLE IF EXISTS ventas_log;
DROP TABLE IF EXISTS productos;

CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    stock INTEGER NOT NULL
);

-- Tabla de auditoría: registra cada movimiento de stock confirmado.
CREATE TABLE ventas_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    detalle TEXT
);

-- id 1 y 4 representan el mismo producto en dos depósitos distintos,
-- para poder simular una transferencia de stock entre almacenes (Caso 3).
INSERT INTO productos (id, nombre, stock) VALUES
    (1, 'Tornillos 3mm - Depósito Norte', 500),
    (2, 'Tuercas 3mm', 300),
    (3, 'Arandelas 3mm', 800),
    (4, 'Tornillos 3mm - Depósito Sur', 100);
