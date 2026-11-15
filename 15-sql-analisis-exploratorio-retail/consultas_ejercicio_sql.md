# SQL aplicado al análisis exploratorio: `ventas_retail`

Consultas SQL para responder cuatro preguntas de negocio sobre la tabla
`ventas_retail`, como parte de la exploración inicial de un proyecto de Data
Science.

## Tabla de trabajo

```sql
CREATE TABLE ventas_retail (
    id_transaccion  INTEGER PRIMARY KEY,
    fecha           DATE,
    producto        TEXT,
    categoria       TEXT,
    cantidad        INTEGER,
    precio_unitario DECIMAL(10, 2),
    region          TEXT
);
```

Las cuatro consultas se probaron en SQLite con 24 ventas de ejemplo (ver
[`probar_consultas.py`](probar_consultas.py)). Los resultados que se muestran
debajo de cada consulta salen de esa prueba.

---

## Consulta 1: Selección y alias

```sql
-- Consulta 1: Selección y alias
-- Utilidad: armar un catálogo rápido de productos y precios para revisar
-- rangos y detectar valores raros (precios en 0, negativos o fuera de escala).
-- El alias p_u_usd deja explícita la moneda en el nombre de la columna.
-- DISTINCT evita repetir el mismo producto con el mismo precio una vez por
-- cada venta: si un producto aparece con dos precios distintos, se ven ambos
-- (y eso ya es un hallazgo: el precio cambió en el tiempo o entre regiones).
SELECT DISTINCT
    producto,
    precio_unitario AS p_u_usd
FROM ventas_retail
ORDER BY producto, p_u_usd;
```

Resultado (23 filas: la "Cafetera" se vendió dos veces a 95.00 y aparece una
sola vez; los "Auriculares Bluetooth" y el "Smartwatch" aparecen dos veces
porque cambiaron de precio). Primeras filas:

| producto | p_u_usd |
|---|---:|
| Aspiradora robot | 420 |
| Auriculares Bluetooth | 44.5 |
| Auriculares Bluetooth | 45.9 |
| Auto a control remoto | 48 |
| Bicicleta urbana | 650 |
| Bloques de construcción | 59.9 |
| Cafetera | 95 |
| ... | ... |

---

## Consulta 2: Filtrado y ordenamiento

```sql
-- Consulta 2: Filtrado y ordenamiento
-- Utilidad: aislar las ventas "grandes" (más de 10 unidades) de la región
-- Norte para analizar qué se compra en volumen allí. Ordenar de la más
-- reciente a la más antigua deja arriba la actividad actual, que es lo
-- primero que se quiere revisar.
-- 'Norte' va entre comillas simples porque es un valor de texto.
SELECT *
FROM ventas_retail
WHERE region = 'Norte'
  AND cantidad > 10
ORDER BY fecha DESC;
```

Resultado (8 filas):

| id_transaccion | fecha | producto | categoria | cantidad | precio_unitario | region |
|---:|---|---|---|---:|---:|---|
| 24 | 2026-04-18 | Juego de mesa | Juguetes | 120 | 34.9 | Norte |
| 14 | 2026-04-14 | Freidora de aire | Hogar | 120 | 129.9 | Norte |
| 18 | 2026-03-19 | Colchoneta de yoga | Deportes | 110 | 19.9 | Norte |
| 6 | 2026-03-15 | Monitor 27 pulgadas | Electrónica | 12 | 289 | Norte |
| 3 | 2026-02-02 | Parlante portátil | Electrónica | 60 | 79.5 | Norte |
| 10 | 2026-01-27 | Juego de sábanas | Hogar | 150 | 32.5 | Norte |
| 20 | 2026-01-22 | Rompecabezas 1000 piezas | Juguetes | 75 | 15.5 | Norte |
| 1 | 2026-01-05 | Auriculares Bluetooth | Electrónica | 120 | 45.9 | Norte |

La venta 12 (Norte, **exactamente 10** unidades) queda afuera, porque la
condición es "mayor a 10" (`>`), no "mayor o igual" (`>=`).

---

## Consulta 3: Limitación

```sql
-- Consulta 3: Limitación (Top 5)
-- Utilidad: identificar las ventas de productos más caros (ticket alto), que
-- suelen tener otro comportamiento (menos unidades, más margen) y conviene
-- mirar por separado. Primero se ordena de mayor a menor precio y después
-- LIMIT se queda con las 5 primeras filas.
SELECT *
FROM ventas_retail
ORDER BY precio_unitario DESC
LIMIT 5;
```

Resultado:

| id_transaccion | fecha | producto | categoria | cantidad | precio_unitario | region |
|---:|---|---|---|---:|---:|---|
| 16 | 2026-02-06 | Bicicleta urbana | Deportes | 6 | 650 | Norte |
| 12 | 2026-03-08 | Aspiradora robot | Hogar | 10 | 420 | Norte |
| 4 | 2026-02-20 | Tablet 10 pulgadas | Electrónica | 8 | 349 | Norte |
| 6 | 2026-03-15 | Monitor 27 pulgadas | Electrónica | 12 | 289 | Norte |
| 2 | 2026-01-18 | Smartwatch | Electrónica | 35 | 189.99 | Sur |

> `LIMIT` es la sintaxis de SQLite, PostgreSQL y MySQL. En SQL Server se
> escribe `SELECT TOP 5 * FROM ventas_retail ORDER BY precio_unitario DESC;`.

---

## Consulta 4: Agregación por grupo

```sql
-- Consulta 4: Agregación por grupo (GROUP BY + HAVING)
-- Utilidad: comparar categorías por volumen y nivel de precio, y quedarse
-- solo con las de alta rotación (más de 500 unidades), que son las que más
-- peso van a tener en cualquier análisis o modelo posterior.
-- El filtro va en HAVING y no en WHERE: WHERE filtra filas ANTES de agrupar,
-- y la suma de unidades recién existe DESPUÉS de agrupar.
SELECT
    categoria,
    SUM(cantidad)                   AS total_unidades,
    ROUND(AVG(precio_unitario), 2)  AS precio_promedio
FROM ventas_retail
GROUP BY categoria
HAVING SUM(cantidad) > 500
ORDER BY total_unidades DESC;
```

Resultado:

| categoria | total_unidades | precio_promedio |
|---|---:|---:|
| Hogar | 640 | 131.86 |
| Electrónica | 520 | 154.99 |

Quedan afuera **Deportes** (exactamente 500 unidades, y la condición es
`> 500`) y **Juguetes** (310).

Notas:

- En `HAVING` se repite `SUM(cantidad)` en lugar de usar el alias
  `total_unidades`. SQLite y MySQL aceptan el alias, pero PostgreSQL y SQL
  Server no, así que repetir la expresión funciona en cualquier motor.
- `AVG(precio_unitario)` es el promedio simple por transacción: una venta de
  6 unidades pesa lo mismo que una de 180. Si se quisiera el precio promedio
  **por unidad vendida**, habría que ponderar:
  `SUM(cantidad * precio_unitario) / SUM(cantidad)`.

---

## Criterios de aceptación

| Criterio | Cómo se cumple |
|---|---|
| Orden sintáctico correcto | Todas siguen `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT` (usando solo las cláusulas que necesitan) |
| Consulta 4 con `GROUP BY` y `HAVING` | `GROUP BY categoria` + `HAVING SUM(cantidad) > 500` |
| Comentario de utilidad en cada consulta | Bloque `--` al inicio de cada una |
| Formato legible | Una cláusula por línea, palabras clave en mayúsculas e indentación |

Errores comunes evitados:

- **`WHERE` sobre una agregación:** el filtro por suma está en `HAVING`.
  Escribir `WHERE SUM(cantidad) > 500` da error ("misuse of aggregate").
- **Texto sin comillas:** `region = 'Norte'` lleva comillas simples. Sin
  ellas, el motor interpreta `Norte` como el nombre de una columna y falla.

---

Tomás Bezzana
