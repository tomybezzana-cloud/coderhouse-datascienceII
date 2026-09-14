# Práctica 2: Análisis SQL sobre una tabla de ventas

Archivo: [`analisis_ventas.py`](analisis_ventas.py)

Ejercicio de extracción y manipulación de datos con SQL sobre una sola tabla
(`ventas_tecnologia`), simulando la exploración inicial que hace un Data
Scientist antes de modelar. Usa `sqlite3` (incluido en Python) para crear la
tabla en memoria, cargar datos de ejemplo y ejecutar las consultas.

Columnas de `ventas_tecnologia`: `id_venta`, `producto`, `categoria`,
`precio_unitario`, `cantidad`, `fecha`, `pais`.

## Consultas incluidas

1. **Selección simple**: productos y precios, ordenados alfabéticamente.
2. **Filtrado crítico**: ventas en Colombia con `precio_unitario > 500`.
3. **Búsqueda de nulos**: ventas donde `categoria` quedó sin cargar (`NULL`).
4. **Agregación**: ingresos totales (`cantidad * precio_unitario`) por
   categoría, usando el alias `ingresos_totales`.
5. **Filtro de élite (`HAVING`)**: categorías con `ingresos_totales > 10000`.

Cada consulta está precedida por un comentario que explica qué pregunta de
negocio resuelve.

## Cómo ejecutarlo

```bash
python analisis_ventas.py
```
