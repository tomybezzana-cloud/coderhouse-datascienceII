# Ejecución eficiente de queries analíticas: `ventas_globales`

Documento comparativo entre una consulta SQL "ingenua" y su versión
optimizada, con el análisis de cómo las procesa el motor y cuánto impacta en
tiempo, lectura de disco y memoria RAM.

## Escenario

Tabla `ventas_globales`: **50 columnas y 10 millones de filas**, con ventas de
2020 a 2024 en 8 categorías. Solo 4 columnas importan para esta pregunta:

| Columna | Tipo | Uso en la consulta |
|---|---|---|
| `id_venta` | INTEGER (clave primaria) | No se usa |
| `fecha` | DATE | Filtro por año 2023 |
| `categoria` | TEXT | Filtro por `'Electrónica'` |
| `monto` | DECIMAL | Se promedia |
| `atributo_01` ... `atributo_46` | INTEGER / REAL / TEXT | No se usan (cliente, logística, marketing...) |

La tabla tiene un índice sobre `(categoria, fecha)`, el índice natural para
consultas que filtran por categoría y período.

**Pregunta de negocio:** ¿cuál es el monto promedio de las ventas de
Electrónica en 2023?

---

## Versión ineficiente

```sql
-- Versión ineficiente: tres problemas a propósito.
-- (1) SELECT * en la subconsulta: pide las 50 columnas aunque solo se usa monto.
-- (2) YEAR(fecha) = 2023: aplica una función a la columna de cada fila, así
--     el motor no puede usar el índice para ir directo a 2023.
-- (3) Subconsulta innecesaria: arma una tabla intermedia (todo 2023, todas las
--     categorías y columnas) para recién después filtrar Electrónica.
SELECT AVG(t.monto) AS promedio_monto
FROM (
    SELECT *
    FROM ventas_globales
    WHERE YEAR(fecha) = 2023
) AS t
WHERE t.categoria = 'Electrónica';
```

## Versión optimizada

```sql
-- Versión optimizada:
-- - Solo toca las columnas que necesita: monto, categoria y fecha.
-- - Filtra por un rango directo sobre la columna (sargable): el índice
--   (categoria, fecha) lleva al motor directo a Electrónica de 2023.
-- - Una sola agregación, sin tabla intermedia: los filtros se aplican lo
--   antes posible (filtrado temprano) y AVG recorre solo las filas útiles.
SELECT AVG(monto) AS promedio_monto
FROM ventas_globales
WHERE categoria = 'Electrónica'
  AND fecha >= '2023-01-01'
  AND fecha <= '2023-12-31';
```

> `YEAR()` es la función de MySQL y SQL Server; en PostgreSQL sería
> `EXTRACT(YEAR FROM fecha)` y en SQLite `strftime('%Y', fecha)`. Las tres
> tienen el mismo problema. Si `fecha` fuera un TIMESTAMP con hora (y no un
> DATE), conviene cerrar el rango con `fecha < '2024-01-01'`: con
> `<= '2023-12-31'` quedarían afuera las ventas del 31/12 posteriores a las
> 00:00.

Las dos consultas devuelven **exactamente el mismo resultado**. Lo que
cambia es cuánto trabajo le cuesta al motor llegar a él.

---

## Análisis del plan de ejecución (EXPLAIN)

**Qué haría el `EXPLAIN` de cada una:**

| | Versión ineficiente | Versión optimizada |
|---|---|---|
| Acceso a la tabla | Sin índice para la fecha: o recorre la tabla completa (*full scan*, 10M filas) o, como mucho, usa el índice solo por `categoria` | *Index range scan*: busca en el índice el tramo exacto `categoria = 'Electrónica'` y fecha entre el 01/01 y el 31/12/2023 |
| Filas procesadas | Todas las filas candidatas: para cada una calcula `YEAR(fecha)` y recién ahí descarta | Solo las de Electrónica 2023 (~250.000 de 10M) |
| Columnas leídas | Las 50, si la subconsulta se materializa como tabla intermedia | 3 (`monto`, `categoria`, `fecha`) |
| Pasos | Subconsulta → tabla intermedia → filtro → agregación | Búsqueda en índice → agregación |

- **¿Cuál hace más escaneo de columnas?** La ineficiente. `SELECT *` obliga a
  leer y mover las 50 columnas, aunque solo se use una. En un motor
  **columnar** (BigQuery, Snowflake, Redshift, Parquet), donde cada columna
  se guarda por separado, eso significa leer 50 archivos en lugar de 3. En
  BigQuery, además, se cobra por bytes leídos.
- **¿Cuál procesa menos filas?** La optimizada. El filtro por rango es
  ***sargable*** (*Search ARGument ABLE*): compara la columna "tal cual"
  contra valores fijos, así que el motor puede buscar en el índice el tramo
  exacto. `YEAR(fecha) = 2023` **no es sargable**: el índice está ordenado
  por `fecha`, no por `YEAR(fecha)`, así que el motor tiene que calcular la
  función en cada fila candidata para saber si sirve.

### Lo que se midió

Se probaron las dos consultas en SQLite con una tabla de las mismas
características (50 columnas, índice `(categoria, fecha)`) y **1 millón de
filas**. Los valores de RAM se extrapolan a 10 millones multiplicando por 10,
porque crecen en forma lineal con la cantidad de filas.

Plan que devolvió `EXPLAIN QUERY PLAN`:

```sql
-- Ineficiente: el índice solo se usa para la categoría
SEARCH ventas_globales USING INDEX idx_categoria_fecha (categoria=?)

-- Optimizada: el índice se usa para la categoría Y el rango de fechas
SEARCH ventas_globales USING INDEX idx_categoria_fecha (categoria=? AND fecha>? AND fecha<?)
```

(SQLite resume cualquier rango como `fecha>? AND fecha<?` en el plan, aunque
el filtro use `>=` y `<=`. Lo que importa es que la fecha aparece dentro del
índice en la optimizada y no en la ineficiente.)

| Medición (1M filas) | Ineficiente | Optimizada | Diferencia |
|---|---:|---:|---:|
| Entradas del índice recorridas | 124.885 | 25.034 | 5x menos |
| Tiempo, índice `(categoria, fecha)` | 190 ms | 168 ms | 1,1x |
| Tiempo, índice cubriente `(categoria, fecha, monto)` | 34,6 ms | 1,4 ms | **25x** |
| Lectura en formato columnar (Parquet) | 220,5 MB / 444 ms | 7,7 MB / 20 ms | **29x menos bytes** |

Cómo leer estos números:

- La ineficiente recorre las ventas de Electrónica **de los 5 años** (125 mil)
  para quedarse con las de 2023 (25 mil). La optimizada va directo a esas 25
  mil.
- Con el índice simple, la diferencia de tiempo es chica: las dos tienen que
  "saltar" del índice a la fila completa (las 50 columnas) 25 mil veces para
  leer el `monto`, y esos saltos son lo más caro.
- Con un **índice cubriente** (que ya incluye `monto`), ya no hace falta ir a
  la tabla y queda a la vista el costo real de no ser sargable: 25 veces más
  lenta. Un índice así solo sirve si la consulta pide pocas columnas; con
  `SELECT *` nunca alcanzaría.
- En el formato columnar, pedir las 50 columnas significa leer 29 veces más
  datos del disco para obtener **las mismas 25 mil filas**.

> **Lo que el optimizador sí arregló:** SQLite "aplanó" la subconsulta de la
> versión ineficiente (la reescribió sin tabla intermedia y descartó las
> columnas que no se usan). Muchos motores modernos lo hacen, pero no
> siempre: no es seguro con `DISTINCT`, `LIMIT` o CTEs materializadas, ni en
> motores más viejos. Lo que **ningún** optimizador arregla es la función
> sobre la fecha: el plan muestra que el rango de fechas no se usó.

---

## Impacto en la memoria RAM

En Data Science la consulta casi nunca termina en el motor: el resultado se
carga en pandas. La forma típica en que `SELECT *` llega a la RAM es "traigo
todo 2023 y filtro en el notebook":

| Qué se trae a pandas | Filas × columnas (10M) | RAM medida (1M filas) | RAM estimada (10M filas) |
|---|---|---:|---:|
| `SELECT *` de todo 2023, filtrando en pandas | ~2.000.000 × 50 | 161 MB | **~1,6 GB** |
| `SELECT *` de la tabla completa | 10.000.000 × 50 | ~806 MB | **~8 GB** |
| Solo `monto, categoria, fecha` ya filtradas | ~250.000 × 3 | 1,2 MB | ~11,5 MB |
| Solo el promedio (versión optimizada) | 1 × 1 | 140 bytes | 140 bytes |

Una notebook con 8 GB de RAM o un entorno gratuito de Google Colab (~12 GB)
no aguanta traer la tabla completa: al filtrar o unir, pandas crea copias
intermedias que pueden duplicar la memoria del DataFrame, y el kernel se cae
con un *MemoryError*. La versión optimizada mueve 140 bytes.

---

## Conclusión

Un Data Scientist es quien más consultas escribe sobre tablas grandes y, a
la vez, el que menos suele mirar cómo se ejecutan. Antes de entrenar un
modelo, la extracción se repite decenas de veces (explorar, probar
variables, rehacer el dataset de entrenamiento). Si cada vez se piden las 50
columnas de 10 millones de filas con filtros no sargables, el costo se
multiplica: minutos de espera en vez de segundos, bytes facturados en la
nube y, sobre todo, notebooks que se quedan sin memoria antes de llegar al
modelo. Pedir solo las columnas necesarias, filtrar con rangos directos que
aprovechen los índices y agregar en el motor (filtrado temprano) hace que el
trabajo pesado lo haga la base de datos, que está diseñada para eso, y que a
Python llegue solo lo que el modelo va a usar.

Además, hay un beneficio que va más allá del rendimiento: una consulta
explícita es una **definición clara de las features**. `SELECT *` hace que
el dataset de entrenamiento dependa de lo que tenga la tabla en ese momento:
si alguien agrega o renombra una columna, el pipeline cambia sin avisar, y
pueden colarse columnas que filtran información del target (*data leakage*).
Elegir las columnas una por una y filtrar con criterios explícitos hace que
el proceso sea reproducible, más barato y más fácil de revisar. Son
decisiones de minutos que evitan horas de depuración cuando el modelo pase a
producción.

---

## Criterios de aceptación

| Criterio | Dónde se cumple |
|---|---|
| Incluye ambas versiones de la consulta | "Versión ineficiente" y "Versión optimizada" |
| Explica por qué `SELECT *` es perjudicial | Escaneo de columnas, formato columnar (29x más bytes), impide el índice cubriente, RAM (~1,6 GB a ~8 GB) y riesgo de *leakage* |
| Menciona "filtrado temprano" / "sargable queries" | Análisis del plan de ejecución: rango sargable vs. `YEAR(fecha)` |
| Un único archivo | Este documento (PDF) |
| Compara el impacto en la RAM | Sección "Impacto en la memoria RAM" |
| La versión optimizada no pide tablas completas | Devuelve 1 fila y lee solo 3 columnas |

---

Tomás Bezzana
