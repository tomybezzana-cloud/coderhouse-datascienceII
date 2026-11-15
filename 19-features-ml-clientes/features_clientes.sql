-- =============================================================================
-- Tabla maestra de features de clientes para Machine Learning
-- Autor: Tomás Bezzana
--
-- Corre tal cual en SQLite (3.25 o superior) y en DuckDB:
--   python ejecutar.py            (SQLite, sin instalar nada)
--   python ejecutar.py --duckdb   (DuckDB, requiere pip install duckdb)
--
-- Objetivo: pasar de cuatro tablas relacionales (clientes, pedidos,
-- detalles_pedido, productos) a una fila por cliente con features que
-- resumen su comportamiento de compra.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. Esquema y datos de prueba
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS features_clientes;
DROP TABLE IF EXISTS detalles_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    cliente_id INTEGER PRIMARY KEY,
    nombre     VARCHAR(50) NOT NULL,
    ciudad     VARCHAR(30) NOT NULL
);

CREATE TABLE productos (
    producto_id INTEGER PRIMARY KEY,
    nombre      VARCHAR(50)    NOT NULL,
    categoria   VARCHAR(20)    NOT NULL,
    precio      DECIMAL(10, 2) NOT NULL
);

-- El pedido es la "cabecera": quién compró y cuándo. No guarda el importe;
-- el importe sale de sus líneas en detalles_pedido.
CREATE TABLE pedidos (
    pedido_id  INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes (cliente_id),
    fecha      DATE    NOT NULL
);

-- Una fila por producto dentro de un pedido. precio_unitario es el precio al
-- momento de la venta (puede diferir del precio de lista actual).
CREATE TABLE detalles_pedido (
    detalle_id      INTEGER PRIMARY KEY,
    pedido_id       INTEGER        NOT NULL REFERENCES pedidos (pedido_id),
    producto_id     INTEGER        NOT NULL REFERENCES productos (producto_id),
    cantidad        INTEGER        NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL
);

-- 10 clientes en 3 ciudades. Inés (9) y Julián (10) todavía no compraron:
-- son los que un INNER JOIN haría desaparecer.
INSERT INTO clientes (cliente_id, nombre, ciudad) VALUES
    ( 1, 'Ana Gómez',     'Córdoba'),
    ( 2, 'Bruno Díaz',    'Córdoba'),
    ( 3, 'Carla Ruiz',    'Córdoba'),
    ( 4, 'Diego Sosa',    'Rosario'),
    ( 5, 'Elena Paz',     'Rosario'),
    ( 6, 'Fabián Torres', 'Rosario'),
    ( 7, 'Gabriela Luna', 'Mendoza'),
    ( 8, 'Hernán Vega',   'Mendoza'),
    ( 9, 'Inés Castro',   'Mendoza'),
    (10, 'Julián Ríos',   'Córdoba');

-- 10 productos en 3 categorías. Hogar no tiene columna propia en las
-- features, así que gasto_alimentos + gasto_tecnologia no siempre da el total.
INSERT INTO productos (producto_id, nombre, categoria, precio) VALUES
    ( 1, 'Arroz 1 kg',       'Alimentos',   2.50),
    ( 2, 'Aceite de oliva',  'Alimentos',  12.00),
    ( 3, 'Café en grano',    'Alimentos',  15.00),
    ( 4, 'Yerba 1 kg',       'Alimentos',   6.00),
    ( 5, 'Auriculares',      'Tecnología', 45.00),
    ( 6, 'Mouse',            'Tecnología', 25.00),
    ( 7, 'Teclado',          'Tecnología', 60.00),
    ( 8, 'Monitor',          'Tecnología', 220.00),
    ( 9, 'Sartén',           'Hogar',      35.00),
    (10, 'Juego de toallas', 'Hogar',      28.00);

INSERT INTO pedidos (pedido_id, cliente_id, fecha) VALUES
    ( 1, 1, '2025-01-04'), ( 2, 1, '2025-02-10'), ( 3, 1, '2025-03-15'),
    ( 4, 1, '2025-04-20'), ( 5, 1, '2025-05-28'),
    ( 6, 2, '2025-01-09'), ( 7, 2, '2025-02-13'), ( 8, 2, '2025-03-19'),
    ( 9, 2, '2025-04-24'),
    (10, 3, '2025-02-02'), (11, 3, '2025-05-07'),
    (12, 4, '2025-01-11'), (13, 4, '2025-02-08'), (14, 4, '2025-03-03'),
    (15, 4, '2025-04-01'), (16, 4, '2025-05-05'), (17, 4, '2025-06-09'),
    (18, 5, '2025-01-22'), (19, 5, '2025-03-01'), (20, 5, '2025-04-12'),
    (21, 5, '2025-06-01'),
    (22, 6, '2025-02-17'), (23, 6, '2025-04-03'), (24, 6, '2025-06-14'),
    (25, 7, '2025-01-15'), (26, 7, '2025-02-20'), (27, 7, '2025-03-25'),
    (28, 7, '2025-04-29'), (29, 7, '2025-06-03'),
    (30, 8, '2025-05-16');

INSERT INTO detalles_pedido (detalle_id, pedido_id, producto_id, cantidad, precio_unitario) VALUES
    -- Ana: 5 pedidos, mucha tecnología
    ( 1,  1, 5, 1,  45.00), ( 2,  1, 3, 1,  15.00),
    ( 3,  2, 7, 1,  60.00),
    ( 4,  3, 2, 2,  12.00), ( 5,  3, 1, 4,   2.50),
    ( 6,  4, 8, 1, 220.00),
    ( 7,  5, 6, 1,  25.00), ( 8,  5, 4, 2,   6.00),
    -- Bruno: 4 pedidos con muchas líneas baratas de alimentos
    ( 9,  6, 1, 4,   2.50), (10,  6, 2, 2,  12.00), (11,  6, 4, 3,   6.00),
    (12,  7, 3, 2,  15.00), (13,  7, 1, 2,   2.50), (14,  7, 4, 2,   6.00), (15, 7, 2, 1, 12.00),
    (16,  8, 6, 1,  25.00), (17,  8, 1, 4,   2.50), (18,  8, 4, 2,   6.00),
    (19,  9, 3, 2,  15.00), (20,  9, 2, 2,  12.00), (21,  9, 1, 2,   2.50),
    -- Carla: solo 2 pedidos, pero caros
    (22, 10, 8, 1, 220.00),
    (23, 11, 7, 1,  60.00), (24, 11, 5, 1,  45.00),
    -- Diego: 6 pedidos variados
    (25, 12, 9, 1,  35.00), (26, 12, 3, 1,  15.00),
    (27, 13, 5, 1,  45.00), (28, 13, 1, 2,   2.50),
    (29, 14, 8, 1, 220.00),
    (30, 15, 10, 2, 28.00),
    (31, 16, 2, 3,  12.00), (32, 16, 4, 2,   6.00),
    (33, 17, 7, 1,  60.00), (34, 17, 6, 1,  25.00),
    -- Elena: 4 pedidos
    (35, 18, 8, 1, 220.00),
    (36, 19, 3, 2,  15.00), (37, 19, 2, 1,  12.00),
    (38, 20, 9, 1,  35.00), (39, 20, 10, 1, 28.00),
    (40, 21, 5, 2,  45.00),
    -- Fabián: exactamente 3 pedidos, pero con 8 líneas
    (41, 22, 7, 1,  60.00), (42, 22, 6, 1,  25.00), (43, 22, 3, 1,  15.00),
    (44, 23, 8, 1, 220.00), (45, 23, 5, 1,  45.00),
    (46, 24, 2, 2,  12.00), (47, 24, 4, 1,   6.00), (48, 24, 1, 2,   2.50),
    -- Gabriela: 5 pedidos chicos
    (49, 25, 4, 2,   6.00), (50, 25, 1, 2,   2.50),
    (51, 26, 6, 1,  25.00),
    (52, 27, 3, 1,  15.00), (53, 27, 2, 1,  12.00),
    (54, 28, 10, 1, 28.00),
    (55, 29, 5, 1,  45.00),
    -- Hernán: un solo pedido
    (56, 30, 9, 1,  35.00), (57, 30, 3, 2,  15.00);


-- -----------------------------------------------------------------------------
-- 1. Valor del cliente (LTV): gasto total por cliente
-- -----------------------------------------------------------------------------
-- LEFT JOIN clientes -> pedidos -> detalles_pedido
--   La tabla de la izquierda es clientes: TODOS sus registros quedan, compren
--   o no. A un cliente sin pedidos el LEFT JOIN le pone NULL en las columnas
--   de pedidos y detalles. La cadena tiene que ser LEFT en cada paso: un solo
--   INNER JOIN más adelante descartaría esas filas con NULL.
--
-- importe de una línea = cantidad * precio_unitario
--   El gasto se suma a nivel de línea (detalles_pedido), que es donde está el
--   dinero, así cada artículo se cuenta exactamente una vez.
--
-- COALESCE(SUM(...), 0)
--   SUM de puros NULL da NULL, no 0. COALESCE lo convierte en 0 para que el
--   modelo reciba un número y no un faltante.
--
-- COUNT(DISTINCT p.pedido_id)
--   Después del JOIN con detalles hay una fila por LÍNEA, no por pedido.
--   COUNT(*) contaría líneas; DISTINCT cuenta pedidos. Además COUNT ignora
--   NULL, así que un cliente sin pedidos da 0.
--
-- GROUP BY cliente_id, nombre, ciudad: todas las columnas del SELECT que no
-- están dentro de una función de agregación.
-- Consulta: 1. Valor del cliente (LTV)
SELECT
    c.cliente_id,
    c.nombre,
    c.ciudad,
    COUNT(DISTINCT p.pedido_id)                            AS cantidad_pedidos,
    COALESCE(SUM(d.cantidad * d.precio_unitario), 0)       AS gasto_total
FROM clientes AS c
LEFT JOIN pedidos         AS p ON p.cliente_id = c.cliente_id
LEFT JOIN detalles_pedido AS d ON d.pedido_id  = p.pedido_id
GROUP BY c.cliente_id, c.nombre, c.ciudad
ORDER BY gasto_total DESC, c.cliente_id;


-- -----------------------------------------------------------------------------
-- 2. Gasto por categoría con agregación condicionada
-- -----------------------------------------------------------------------------
-- SUM(CASE WHEN categoria = 'X' THEN importe ELSE 0 END)
--   El CASE se evalúa fila por fila ANTES de sumar: si la línea es de la
--   categoría aporta su importe, si no aporta 0. La suma de esa columna
--   "filtrada" es el gasto en la categoría. Así se crean varias features en
--   una sola pasada por los datos, sin subconsultas.
--
-- ELSE 0 (y no dejarlo sin ELSE)
--   Sin ELSE el CASE devuelve NULL, y un cliente sin compras de esa categoría
--   (o sin compras en general) terminaría con NULL en vez de 0.
--
-- Se unen las cuatro tablas, siempre con LEFT JOIN, para no perder a Inés ni
-- a Julián.
-- Consulta: 2. Gasto por categoría
SELECT
    c.cliente_id,
    c.nombre,
    c.ciudad,
    COALESCE(SUM(d.cantidad * d.precio_unitario), 0)                AS gasto_total,
    SUM(CASE WHEN pr.categoria = 'Alimentos'
             THEN d.cantidad * d.precio_unitario ELSE 0 END)        AS gasto_alimentos,
    SUM(CASE WHEN pr.categoria = 'Tecnología'
             THEN d.cantidad * d.precio_unitario ELSE 0 END)        AS gasto_tecnologia
FROM clientes AS c
LEFT JOIN pedidos         AS p  ON p.cliente_id   = c.cliente_id
LEFT JOIN detalles_pedido AS d  ON d.pedido_id    = p.pedido_id
LEFT JOIN productos       AS pr ON pr.producto_id = d.producto_id
GROUP BY c.cliente_id, c.nombre, c.ciudad
ORDER BY c.cliente_id;


-- -----------------------------------------------------------------------------
-- 3. Segmentación de clientes activos con HAVING
-- -----------------------------------------------------------------------------
-- Condición: más de 3 compras y gasto promedio por compra mayor a 50.
--
-- HAVING y no WHERE
--   WHERE filtra filas sueltas ANTES de agrupar, cuando COUNT y SUM todavía
--   no existen. HAVING filtra los grupos DESPUÉS de agregar, así que es el
--   único lugar donde se puede preguntar por un COUNT o un SUM.
--
-- "Compra" = pedido, no línea
--   cantidad de compras  = COUNT(DISTINCT pedido_id)
--   gasto promedio       = gasto total / cantidad de pedidos
--   AVG(cantidad * precio_unitario) NO sirve: promediaría las líneas, y un
--   pedido con muchas líneas baratas parecería un cliente que gasta poco.
--   (La consulta 5 muestra la diferencia con números.)
--
-- * 1.0 antes de dividir
--   SQLite guarda 220.00 como el entero 220, así que SUM(...) / COUNT(...)
--   sería una división ENTERA: 415 / 4 daría 103 y no 103.75. Multiplicar por
--   1.0 fuerza la división decimal (DuckDB ya la hace, y así no cambia nada).
--
-- En HAVING se repiten las expresiones en lugar de usar los alias del SELECT,
-- porque es la forma estándar y la que acepta cualquier motor.
-- Consulta: 3. Clientes activos (HAVING)
SELECT
    c.cliente_id,
    c.nombre,
    c.ciudad,
    COUNT(DISTINCT p.pedido_id)                                          AS cantidad_pedidos,
    SUM(d.cantidad * d.precio_unitario)                                  AS gasto_total,
    ROUND(SUM(d.cantidad * d.precio_unitario)
          * 1.0 / COUNT(DISTINCT p.pedido_id), 2)                        AS gasto_promedio
FROM clientes AS c
LEFT JOIN pedidos         AS p ON p.cliente_id = c.cliente_id
LEFT JOIN detalles_pedido AS d ON d.pedido_id  = p.pedido_id
GROUP BY c.cliente_id, c.nombre, c.ciudad
HAVING COUNT(DISTINCT p.pedido_id) > 3
   AND SUM(d.cantidad * d.precio_unitario) * 1.0 / COUNT(DISTINCT p.pedido_id) > 50
ORDER BY gasto_promedio DESC;


-- -----------------------------------------------------------------------------
-- 4. Tabla maestra de features + ranking dentro de la ciudad
-- -----------------------------------------------------------------------------
-- Junta todo en una fila por cliente y la guarda como tabla, lista para
-- exportar a un pipeline de ML.
--
-- RANK() OVER (PARTITION BY ciudad ORDER BY gasto_total DESC)
--   Las funciones de ventana se evalúan DESPUÉS del GROUP BY, así que pueden
--   trabajar sobre los agregados en la misma consulta.
--   PARTITION BY ciudad -> el ranking vuelve a empezar en 1 en cada ciudad.
--   ORDER BY ... DESC   -> el que más gastó queda primero.
--   RANK                -> si dos clientes empatan comparten puesto y el
--                          siguiente se saltea (1, 1, 3).
--
-- es_activo: el mismo criterio de la consulta 3, pero como feature binaria
-- (1/0) en lugar de filtro, para no sacar a nadie de la población. Lo que
-- excluye el HAVING en la consulta 3 acá queda marcado con 0.
--
-- NULLIF(COUNT(...), 0) evita dividir por cero en clientes sin pedidos; la
-- división da NULL y COALESCE la deja en 0.
-- No se usa ningún WHERE: la población de clientes queda completa.
CREATE TABLE features_clientes AS
SELECT
    c.cliente_id,
    c.nombre,
    c.ciudad,
    COUNT(DISTINCT p.pedido_id)                                          AS cantidad_pedidos,
    COALESCE(SUM(d.cantidad * d.precio_unitario), 0)                     AS gasto_total,
    COALESCE(ROUND(SUM(d.cantidad * d.precio_unitario)
                   * 1.0 / NULLIF(COUNT(DISTINCT p.pedido_id), 0), 2), 0) AS gasto_promedio,
    SUM(CASE WHEN pr.categoria = 'Alimentos'
             THEN d.cantidad * d.precio_unitario ELSE 0 END)             AS gasto_alimentos,
    SUM(CASE WHEN pr.categoria = 'Tecnología'
             THEN d.cantidad * d.precio_unitario ELSE 0 END)             AS gasto_tecnologia,
    CASE WHEN COUNT(DISTINCT p.pedido_id) > 3
          AND SUM(d.cantidad * d.precio_unitario)
              * 1.0 / COUNT(DISTINCT p.pedido_id) > 50
         THEN 1 ELSE 0 END                                               AS es_activo,
    RANK() OVER (
        PARTITION BY c.ciudad
        ORDER BY COALESCE(SUM(d.cantidad * d.precio_unitario), 0) DESC
    )                                                                    AS ranking_ciudad
FROM clientes AS c
LEFT JOIN pedidos         AS p  ON p.cliente_id   = c.cliente_id
LEFT JOIN detalles_pedido AS d  ON d.pedido_id    = p.pedido_id
LEFT JOIN productos       AS pr ON pr.producto_id = d.producto_id
GROUP BY c.cliente_id, c.nombre, c.ciudad;

-- Consulta: 4. Tabla maestra features_clientes
SELECT
    cliente_id,
    nombre,
    ciudad,
    ranking_ciudad,
    cantidad_pedidos,
    gasto_total,
    gasto_promedio,
    gasto_alimentos,
    gasto_tecnologia,
    es_activo
FROM features_clientes
ORDER BY ciudad, ranking_ciudad;


-- -----------------------------------------------------------------------------
-- 5. Errores comunes, lado a lado
-- -----------------------------------------------------------------------------
-- Para cada cliente con compras, compara la forma correcta con la incorrecta:
--   pedidos_ok       COUNT(DISTINCT pedido_id): cuenta compras.
--   filas_join       COUNT(*): cuenta líneas, porque el JOIN con detalles
--                    repite el pedido una vez por línea. Con este conteo
--                    Fabián (3 pedidos, 8 líneas) pasaría el filtro "> 3".
--   promedio_ok      gasto total / pedidos: promedio por compra.
--   promedio_lineas  AVG del importe de cada línea: con este cálculo Bruno
--                    (54,25 por compra) quedaría por debajo de 50 y se
--                    perdería un cliente activo.
-- Consulta: 5. Errores comunes: COUNT(*) y AVG por línea
SELECT
    c.cliente_id,
    c.nombre,
    COUNT(DISTINCT p.pedido_id)                                          AS pedidos_ok,
    COUNT(*)                                                             AS filas_join,
    ROUND(SUM(d.cantidad * d.precio_unitario)
          * 1.0 / COUNT(DISTINCT p.pedido_id), 2)                        AS promedio_ok,
    ROUND(AVG(d.cantidad * d.precio_unitario), 2)                        AS promedio_lineas
FROM clientes AS c
JOIN pedidos         AS p ON p.cliente_id = c.cliente_id
JOIN detalles_pedido AS d ON d.pedido_id  = p.pedido_id
GROUP BY c.cliente_id, c.nombre
ORDER BY c.cliente_id;


-- Y por qué LEFT JOIN: con INNER JOIN los clientes sin compras desaparecen
-- de la población (8 en lugar de 10), y el modelo nunca vería ese perfil.
-- Consulta: 6. LEFT JOIN vs. INNER JOIN: tamaño de la población
SELECT
    (SELECT COUNT(*) FROM clientes)                                      AS clientes_totales,
    (SELECT COUNT(DISTINCT c.cliente_id)
       FROM clientes AS c
       LEFT JOIN pedidos AS p ON p.cliente_id = c.cliente_id)            AS con_left_join,
    (SELECT COUNT(DISTINCT c.cliente_id)
       FROM clientes AS c
       JOIN pedidos AS p ON p.cliente_id = c.cliente_id)                 AS con_inner_join;
