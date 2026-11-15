-- =============================================================================
-- Funciones de ventana: analizar cada fila sin perder el contexto
-- Autor: Tomás Bezzana
--
-- Corre tal cual en SQLite (3.25 o superior) y en DuckDB:
--   sqlite3 :memory: < funciones_ventana.sql
--   duckdb < funciones_ventana.sql
--
-- Idea central: GROUP BY colapsa las filas (un resultado por grupo); una
-- función de ventana calcula lo mismo pero lo "pega" al lado de cada fila,
-- así que el resultado conserva las 20 filas de la tabla original.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. Tabla de pedidos con datos de prueba
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS pedidos;

CREATE TABLE pedidos (
    pedido_id  INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    fecha      DATE    NOT NULL,
    importe    DECIMAL(10, 2) NOT NULL,
    categoria  VARCHAR(20)    NOT NULL
);

-- 20 pedidos de 5 clientes en 3 categorías. Hay dos pedidos el mismo día
-- (2025-02-14) a propósito, para mostrar cómo se comporta el acumulado con
-- fechas repetidas.
INSERT INTO pedidos (pedido_id, cliente_id, fecha, importe, categoria) VALUES
    ( 1, 101, '2025-01-05',  500.00, 'Electrónica'),
    ( 2, 102, '2025-01-08',   45.50, 'Libros'),
    ( 3, 103, '2025-01-12',  120.00, 'Hogar'),
    ( 4, 101, '2025-01-20',  350.00, 'Electrónica'),
    ( 5, 104, '2025-01-25',   30.00, 'Libros'),
    ( 6, 102, '2025-02-02',  800.00, 'Electrónica'),
    ( 7, 105, '2025-02-09',   75.00, 'Hogar'),
    ( 8, 103, '2025-02-14',   60.00, 'Libros'),
    ( 9, 101, '2025-02-14',   90.00, 'Hogar'),
    (10, 104, '2025-02-21', 1200.00, 'Electrónica'),
    (11, 105, '2025-03-01',   25.00, 'Libros'),
    (12, 102, '2025-03-07',   55.00, 'Libros'),
    (13, 103, '2025-03-15',  300.00, 'Hogar'),
    (14, 101, '2025-03-22',  420.00, 'Electrónica'),
    (15, 104, '2025-04-02',  150.00, 'Hogar'),
    (16, 105, '2025-04-10',  650.00, 'Electrónica'),
    (17, 102, '2025-04-18',   40.00, 'Libros'),
    (18, 103, '2025-04-25',  980.00, 'Electrónica'),
    (19, 101, '2025-05-03',   35.00, 'Libros'),
    (20, 105, '2025-05-11',  210.00, 'Hogar');


-- -----------------------------------------------------------------------------
-- 1. Métricas por cliente: promedio histórico de gasto de cada cliente
-- -----------------------------------------------------------------------------
-- AVG(importe) OVER (PARTITION BY cliente_id)
--   OVER()        -> indica que AVG es una función de ventana: no colapsa filas.
--   PARTITION BY  -> la ventana de cada fila son solo los pedidos de SU cliente,
--                    así que cada pedido se compara con el promedio de quien lo
--                    hizo y no con el promedio de toda la empresa.
--   Sin ORDER BY  -> la ventana es la partición completa: el promedio es el
--                    histórico total del cliente (el mismo valor en todas sus filas).
--
-- desvio_vs_promedio = cuánto se aleja el pedido del promedio de ese cliente.
-- Un desvío grande marca un pedido fuera de su rango normal.
SELECT
    pedido_id,
    cliente_id,
    fecha,
    importe,
    categoria,
    ROUND(AVG(importe) OVER (PARTITION BY cliente_id), 2)           AS promedio_cliente,
    ROUND(importe - AVG(importe) OVER (PARTITION BY cliente_id), 2) AS desvio_vs_promedio
FROM pedidos
ORDER BY cliente_id, fecha;


-- -----------------------------------------------------------------------------
-- 2. Ventas acumuladas de la empresa en orden cronológico
-- -----------------------------------------------------------------------------
-- SUM(importe) OVER (ORDER BY fecha, pedido_id ROWS BETWEEN ...)
--   Sin PARTITION BY -> una sola ventana con toda la empresa.
--   ORDER BY fecha   -> recorre los pedidos en orden cronológico; cada fila suma
--                       desde el primer pedido hasta ella misma (total corrido).
--   pedido_id        -> desempata los pedidos del mismo día para que el orden
--                       sea determinista.
--   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--                    -> "desde la primera fila hasta esta", fila por fila. Es
--                       explícito porque el marco por defecto (RANGE) trata a
--                       las filas empatadas en el ORDER BY como una sola y les
--                       daría el mismo acumulado (ver consulta 2b).
SELECT
    fecha,
    importe,
    SUM(importe) OVER (
        ORDER BY fecha, pedido_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS ventas_acumuladas
FROM pedidos
ORDER BY fecha, pedido_id;


-- 2b. Comparación: qué pasa si se quita el ORDER BY (y con el marco por defecto)
--   sin_order_by    -> SUM() OVER (): sin orden no hay "hasta esta fila", así
--                      que suma toda la tabla y repite el total (6135.5) en las
--                      20 filas. Es el error común de la consigna.
--   rango_por_fecha -> ORDER BY fecha con el marco por defecto (RANGE): los dos
--                      pedidos del 2025-02-14 reciben el mismo acumulado, porque
--                      para RANGE son "la misma posición".
SELECT
    pedido_id,
    fecha,
    importe,
    SUM(importe) OVER (ORDER BY fecha, pedido_id
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS acumulado_correcto,
    SUM(importe) OVER ()                                                 AS sin_order_by,
    SUM(importe) OVER (ORDER BY fecha)                                   AS rango_por_fecha
FROM pedidos
ORDER BY fecha, pedido_id;


-- -----------------------------------------------------------------------------
-- 3. Contribución de cada pedido al total de su categoría
-- -----------------------------------------------------------------------------
-- SUM(importe) OVER (PARTITION BY categoria)
--   PARTITION BY categoria -> el total se calcula solo con los pedidos de la
--                             misma categoría y se repite en cada uno de ellos.
--   Sin ORDER BY           -> la suma es el total de la categoría completa, no
--                             un acumulado.
-- pct_categoria = importe / total de la categoría * 100 (100.0 evita la
-- división entera). La suma de pct_categoria dentro de cada categoría da 100.
SELECT
    pedido_id,
    categoria,
    importe,
    SUM(importe) OVER (PARTITION BY categoria)                               AS total_categoria,
    ROUND(importe * 100.0 / SUM(importe) OVER (PARTITION BY categoria), 2)  AS pct_categoria
FROM pedidos
ORDER BY categoria, pct_categoria DESC;


-- -----------------------------------------------------------------------------
-- Extra: filtrar por una columna de ventana
-- -----------------------------------------------------------------------------
-- Esto NO funciona:
--   SELECT ..., AVG(importe) OVER (PARTITION BY cliente_id) AS promedio_cliente
--   FROM pedidos
--   WHERE importe > promedio_cliente;
-- El WHERE se evalúa antes que las funciones de ventana, así que en ese paso
-- promedio_cliente todavía no existe. La solución es calcular la ventana en
-- una CTE (o subconsulta) y filtrar afuera.
--
-- Pedidos que superan en más de un 50 % el promedio de su cliente:
WITH pedidos_con_promedio AS (
    SELECT
        pedido_id,
        cliente_id,
        fecha,
        importe,
        AVG(importe) OVER (PARTITION BY cliente_id) AS promedio_cliente
    FROM pedidos
)
SELECT
    pedido_id,
    cliente_id,
    fecha,
    importe,
    ROUND(promedio_cliente, 2) AS promedio_cliente
FROM pedidos_con_promedio
WHERE importe > promedio_cliente * 1.5
ORDER BY cliente_id, fecha;
