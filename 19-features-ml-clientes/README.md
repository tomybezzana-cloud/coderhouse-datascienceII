# Tabla maestra de features de clientes con SQL

**Autor:** Tomás Bezzana

Transformación de cuatro tablas relacionales (`clientes`, `pedidos`,
`detalles_pedido`, `productos`) en una **tabla maestra de features**: una fila por
cliente con métricas que resumen su comportamiento de compra, lista para usar en
un modelo de Machine Learning.

## Archivos

| Archivo | Qué contiene |
|---------|--------------|
| [`features_clientes.sql`](features_clientes.sql) | Script completo: crea el esquema, carga los datos de prueba y ejecuta las consultas, todas comentadas |
| [`ejecutar.py`](ejecutar.py) | Corre el script en SQLite o en DuckDB e imprime cada resultado |

## Cómo ejecutarlo

```bash
python ejecutar.py            # SQLite: viene con Python, no requiere instalar nada
python ejecutar.py --duckdb   # DuckDB: pip install duckdb
```

El `.sql` también se puede ejecutar entero en DBeaver o con la CLI:
`sqlite3 :memory: < features_clientes.sql` o `duckdb < features_clientes.sql`.
Los dos motores devuelven exactamente los mismos resultados.

## Esquema y datos de prueba

```
clientes (cliente_id, nombre, ciudad)
    1 ── N  pedidos (pedido_id, cliente_id, fecha)
                1 ── N  detalles_pedido (detalle_id, pedido_id, producto_id, cantidad, precio_unitario)
                                N ── 1  productos (producto_id, nombre, categoria, precio)
```

El pedido es solo la cabecera (quién y cuándo). El dinero está en las líneas de
`detalles_pedido`: importe = `cantidad * precio_unitario`.

Los datos son 10 clientes en 3 ciudades (Córdoba, Rosario y Mendoza), 30 pedidos,
57 líneas y 10 productos de 3 categorías (Alimentos, Tecnología y Hogar). Algunos
clientes están armados a propósito para poner a prueba cada consigna:

| Cliente | Caso que representa |
|---------|---------------------|
| Inés (9) y Julián (10) | No compraron nunca: prueban el `LEFT JOIN` |
| Fabián (6) | Exactamente 3 pedidos con 8 líneas: prueban el `> 3` y el `COUNT(DISTINCT)` |
| Bruno (2) | Pedidos de muchas líneas baratas: prueban el cálculo del promedio |
| Gabriela (7) | Muchas compras chicas: más de 3, pero con un promedio menor a 50 |
| Carla (3) | Gasta mucho en pocas compras: un promedio alto, pero solo 2 pedidos |

## Consultas

### 1. Valor del cliente (LTV)

```sql
COUNT(DISTINCT p.pedido_id)                      AS cantidad_pedidos,
COALESCE(SUM(d.cantidad * d.precio_unitario), 0) AS gasto_total
FROM clientes AS c
LEFT JOIN pedidos         AS p ON p.cliente_id = c.cliente_id
LEFT JOIN detalles_pedido AS d ON d.pedido_id  = p.pedido_id
GROUP BY c.cliente_id, c.nombre, c.ciudad
```

`clientes` es la tabla de la izquierda, así que el resultado conserva a los **10
clientes**. Inés y Julián no tienen pedidos: el `LEFT JOIN` les completa las
columnas de pedidos con `NULL`, `SUM` de puros `NULL` da `NULL`, y `COALESCE` lo
convierte en `0`. Para un modelo, un cliente que no compró es información (gasto
0), no un dato faltante.

Toda la cadena de joins tiene que ser `LEFT`: si el segundo fuera un `JOIN` común,
descartaría las filas con `NULL` que generó el primero, y los dos clientes
desaparecerían igual. La consulta 6 lo cuantifica: con `INNER JOIN` la población
baja de 10 a 8 clientes.

### 2. Gasto por categoría (agregación condicionada)

```sql
SUM(CASE WHEN pr.categoria = 'Alimentos'
         THEN d.cantidad * d.precio_unitario ELSE 0 END) AS gasto_alimentos,
SUM(CASE WHEN pr.categoria = 'Tecnología'
         THEN d.cantidad * d.precio_unitario ELSE 0 END) AS gasto_tecnologia
```

El `CASE` se evalúa en cada línea antes de sumar: si la línea es de la categoría
aporta su importe, y si no aporta 0. Cada `SUM` funciona entonces como un total
filtrado, y se arman varias features en una sola pasada por las cuatro tablas, sin
subconsultas. El `ELSE 0` es necesario: sin él, el `CASE` devuelve `NULL` y un
cliente sin compras quedaría con `NULL` en lugar de 0.

| cliente | gasto_total | gasto_alimentos | gasto_tecnologia |
|---------|------------:|----------------:|-----------------:|
| Ana | 411,00 | 61,00 | 350,00 |
| Bruno | 217,00 | 192,00 | 25,00 |
| Diego | 509,00 | 68,00 | 350,00 |
| Julián | 0,00 | 0,00 | 0,00 |

Las dos columnas no siempre suman el total porque existe una tercera categoría
(Hogar): a Diego le faltan los $91 que gastó en Hogar.

### 3. Segmentación de clientes activos (`HAVING`)

```sql
HAVING COUNT(DISTINCT p.pedido_id) > 3
   AND SUM(d.cantidad * d.precio_unitario) * 1.0 / COUNT(DISTINCT p.pedido_id) > 50
```

El filtro va en `HAVING` porque se aplica sobre agregados. `WHERE` se evalúa antes
del `GROUP BY`, cuando `COUNT` y `SUM` todavía no existen. Resultado: **4 clientes
activos**.

| cliente | pedidos | gasto_total | gasto_promedio |
|---------|--------:|------------:|---------------:|
| Elena | 4 | 415,00 | 103,75 |
| Diego | 6 | 509,00 | 84,83 |
| Ana | 5 | 411,00 | 82,20 |
| Bruno | 4 | 217,00 | 54,25 |

Quedan afuera Fabián (justo 3 pedidos, no "más de 3"), Carla y Hernán (pocos
pedidos), Gabriela (promedio de $28,40) y los dos clientes sin compras.

Hay tres decisiones en esta consulta:

- **Compra = pedido, no línea.** La cantidad de compras se cuenta con
  `COUNT(DISTINCT pedido_id)`, y el promedio es el gasto total dividido por los
  pedidos.
- **No se usa `AVG(importe)`.** Ese cálculo promedia las *líneas*. A Bruno le daría
  $16,69, cuando gasta $54,25 por compra, y lo sacaría del segmento por error.
- **`* 1.0` antes de dividir.** SQLite guarda `220.00` como el entero `220`, así que
  `SUM / COUNT` sería una división entera: el promedio de Elena daría 103 en lugar
  de 103,75. Este error apareció al comparar las salidas de SQLite y DuckDB.

### 4. Tabla maestra + ranking por ciudad

La consulta final junta todo en `features_clientes`, con una fila por cliente:

```sql
RANK() OVER (
    PARTITION BY c.ciudad
    ORDER BY COALESCE(SUM(d.cantidad * d.precio_unitario), 0) DESC
) AS ranking_ciudad
```

Las funciones de ventana se evalúan **después** del `GROUP BY`, por eso pueden
ordenar por un `SUM` en la misma consulta. `PARTITION BY ciudad` hace que el
ranking vuelva a empezar en 1 en cada ciudad.

| ciudad | ranking | cliente | pedidos | gasto_total | gasto_promedio | es_activo |
|--------|--------:|---------|--------:|------------:|---------------:|:---------:|
| Córdoba | 1 | Ana | 5 | 411,00 | 82,20 | 1 |
| Córdoba | 2 | Carla | 2 | 325,00 | 162,50 | 0 |
| Córdoba | 3 | Bruno | 4 | 217,00 | 54,25 | 1 |
| Córdoba | 4 | Julián | 0 | 0,00 | 0,00 | 0 |
| Mendoza | 1 | Gabriela | 5 | 142,00 | 28,40 | 0 |
| Mendoza | 2 | Hernán | 1 | 65,00 | 65,00 | 0 |
| Mendoza | 3 | Inés | 0 | 0,00 | 0,00 | 0 |
| Rosario | 1 | Diego | 6 | 509,00 | 84,83 | 1 |
| Rosario | 2 | Elena | 4 | 415,00 | 103,75 | 1 |
| Rosario | 3 | Fabián | 3 | 400,00 | 133,33 | 0 |

(La tabla también incluye `gasto_alimentos` y `gasto_tecnologia`.)

En la tabla maestra, el criterio de la consulta 3 no filtra filas: queda como una
**feature binaria** (`es_activo`). Así la población sigue completa (10 clientes) y
el modelo aprende también de los que no cumplen. `NULLIF(COUNT(...), 0)` evita
dividir por cero en los clientes sin pedidos.

## Errores comunes, verificados

La consulta 5 compara la forma correcta con la incorrecta para cada cliente:

| cliente | pedidos (`COUNT DISTINCT`) | filas del join (`COUNT(*)`) | promedio por pedido | `AVG` por línea |
|---------|------:|------:|-------:|-------:|
| Bruno | 4 | 13 | 54,25 | 16,69 |
| Fabián | 3 | 8 | 133,33 | 50,00 |
| Gabriela | 5 | 7 | 28,40 | 20,29 |

- **Duplicación por el join.** Al unir con `detalles_pedido`, cada pedido aparece
  una vez por línea. `COUNT(*)` le daría 8 compras a Fabián, que pasaría el filtro
  `> 3` con solo 3 pedidos. El `SUM` sí es correcto, porque el importe vive en las
  líneas y cada línea se cuenta una sola vez.
- **`GROUP BY` incompleto.** Todas las consultas agrupan por `cliente_id, nombre,
  ciudad`, que son todas las columnas no agregadas del `SELECT`.
- **Agregados en el `WHERE`.** El filtro de activos está en `HAVING`. La tabla
  maestra no usa ningún `WHERE`, para no recortar la población.

## Resumen

| Requisito | Dónde |
|-----------|-------|
| `LEFT JOIN` que conserva a todos los clientes, con nulos en 0 | Consultas 1, 2 y 4 (`COALESCE`, `ELSE 0`); la consulta 6 muestra la diferencia con `INNER JOIN` |
| Features por categoría con agregación condicionada, sin subconsultas | Consultas 2 y 4 (`SUM(CASE WHEN ...)`) |
| `HAVING` con más de 3 compras y promedio mayor a 50 | Consulta 3 |
| Función de ventana para el ranking dentro de la ciudad | Consulta 4 (`RANK() OVER (PARTITION BY ciudad ...)`) |
| `GROUP BY` con todas las columnas no agregadas | Todas las consultas agregadas |
| Se ejecuta en SQLite y en DuckDB | `python ejecutar.py` y `python ejecutar.py --duckdb` |
