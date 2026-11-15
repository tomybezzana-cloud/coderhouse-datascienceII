# Funciones de ventana: analizar cada fila sin perder contexto

**Autor:** Tomás Bezzana

Análisis de una tabla de pedidos (`pedido_id`, `cliente_id`, `fecha`, `importe`,
`categoria`) con funciones de ventana: métricas de grupo calculadas **al lado de
cada fila**, sin colapsar el resultado como haría un `GROUP BY`.

## Archivos

| Archivo | Qué contiene |
|---------|--------------|
| [`funciones_ventana.sql`](funciones_ventana.sql) | Script completo: crea la tabla, carga 20 pedidos de prueba y ejecuta las consultas, todas comentadas |
| [`ejecutar.py`](ejecutar.py) | Corre el script con el `sqlite3` que trae Python e imprime cada resultado |

## Cómo ejecutarlo

El `.sql` es autocontenido y funciona igual en SQLite (3.25 o superior) y en DuckDB:

```bash
python ejecutar.py                      # no requiere instalar nada
sqlite3 :memory: < funciones_ventana.sql
duckdb < funciones_ventana.sql
```

También se puede abrir en DBeaver o en <https://sqliteonline.com> y ejecutar entero.

## Datos de prueba

20 pedidos de 5 clientes (101 a 105) entre enero y mayo de 2025, en 3 categorías:
Electrónica (7 pedidos, $4900), Hogar (6, $945) y Libros (7, $290,50). Total:
$6135,50. Los pedidos 8 y 9 son del mismo día (2025-02-14) a propósito, para ver
cómo se comporta el acumulado con fechas repetidas.

## Consultas

Las tres consultas pedidas devuelven **20 filas**, igual que la tabla original.
Ninguna usa `GROUP BY`.

### 1. Promedio histórico de cada cliente

```sql
AVG(importe) OVER (PARTITION BY cliente_id) AS promedio_cliente
```

Cada pedido conserva sus columnas y suma el promedio de gasto de su cliente y el
desvío respecto de ese promedio. Por ejemplo, el cliente 104 gasta en promedio
$460: su pedido de $1200 queda +$740 por encima, y el de $30 queda −$430 por debajo.

**Por qué `PARTITION BY cliente_id`:** la pregunta es si un pedido está fuera del
rango normal *de ese cliente*, así que cada fila se tiene que comparar solo con
los pedidos de quien la hizo. `PARTITION BY` arma esos grupos: la ventana de cada
fila son los pedidos de su mismo cliente. Con `OVER ()` vacío el promedio sería
el de toda la empresa ($306,78 en las 20 filas) y no serviría para el objetivo:
un pedido de $420 es normal para el cliente 101 (promedio $279) pero sería
llamativo para un cliente que gasta $50. No lleva `ORDER BY` porque se busca el
promedio histórico completo, no uno que vaya creciendo pedido a pedido.

### 2. Ventas acumuladas de la empresa

```sql
SUM(importe) OVER (
    ORDER BY fecha, pedido_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) AS ventas_acumuladas
```

| fecha | importe | ventas_acumuladas |
|-------|--------:|------------------:|
| 2025-01-05 | 500 | 500 |
| 2025-01-08 | 45,50 | 545,50 |
| 2025-01-12 | 120 | 665,50 |
| … | … | … |
| 2025-02-14 | 60 | 1980,50 |
| 2025-02-14 | 90 | 2070,50 |
| … | … | … |
| 2025-05-11 | 210 | 6135,50 |

No hay `PARTITION BY` porque se acumula la empresa entera. `ORDER BY fecha` es lo
que convierte la suma en un total corrido: cada fila suma desde el primer pedido
hasta ella misma.

**Qué pasa si se quita el `ORDER BY`:** `SUM(importe) OVER ()` deja de tener un
"hasta esta fila", porque sin orden no hay filas anteriores ni posteriores. La
ventana pasa a ser la tabla completa y las 20 filas muestran el mismo número,
$6135,50, que es el total general. Se pierde el acumulado: la consulta 2b del
script pone las dos columnas lado a lado para verlo.

**Detalle con fechas repetidas:** si se escribe solo `ORDER BY fecha`, el marco
por defecto es `RANGE`, que trata las filas con la misma fecha como una sola
posición. Los dos pedidos del 2025-02-14 reciben entonces el mismo acumulado
($2070,50) en lugar de $1980,50 y $2070,50. Por eso la consulta agrega
`pedido_id` para desempatar y declara el marco `ROWS` explícitamente, que avanza
fila por fila. Esto también se ve en la consulta 2b (columna `rango_por_fecha`).

### 3. Contribución de cada pedido a su categoría

```sql
ROUND(importe * 100.0 / SUM(importe) OVER (PARTITION BY categoria), 2) AS pct_categoria
```

`SUM(...) OVER (PARTITION BY categoria)` pone el total de la categoría en cada
pedido, y dividir el importe por ese total da su peso. Se usa `100.0` y no `100`
para evitar la división entera. Algunos resultados:

| pedido_id | categoria | importe | total_categoria | pct_categoria |
|----------:|-----------|--------:|----------------:|--------------:|
| 10 | Electrónica | 1200 | 4900 | 24,49 % |
| 1 | Electrónica | 500 | 4900 | 10,20 % |
| 13 | Hogar | 300 | 945 | 31,75 % |
| 8 | Libros | 60 | 290,50 | 20,65 % |

Dentro de cada categoría los porcentajes suman 100.

### Extra: filtrar por una columna de ventana

`WHERE importe > promedio_cliente` falla, porque el `WHERE` se evalúa antes que
las funciones de ventana y en ese paso la columna todavía no existe. El script
resuelve el caso con una CTE: primero calcula el promedio por cliente y después
filtra afuera. Así encuentra los 6 pedidos que superan en más de un 50 % el
promedio de su cliente (1, 6, 10, 14, 16 y 18).

## Resumen de cláusulas

| Consulta | `OVER()` | `PARTITION BY` | `ORDER BY` |
|----------|:--------:|----------------|------------|
| 1. Promedio por cliente | Sí | `cliente_id`: comparar con el propio cliente | No: promedio histórico completo |
| 2. Ventas acumuladas | Sí | No: toda la empresa | `fecha, pedido_id`: total corrido |
| 3. % de la categoría | Sí | `categoria`: total de su categoría | No: total completo |
