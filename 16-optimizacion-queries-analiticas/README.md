# Práctica 16: Ejecución eficiente de queries analíticas

Documento comparativo entre una consulta SQL "ingenua" y su versión
optimizada, para obtener el promedio de ventas de Electrónica en 2023 sobre
una tabla `ventas_globales` de 50 columnas y 10 millones de filas.

Archivos:

- [`Optimizacion_Queries_Analiticas_Bezzana_Tomas.pdf`](Optimizacion_Queries_Analiticas_Bezzana_Tomas.pdf):
  **el entregable** (4 páginas).
- [`optimizacion_queries.md`](optimizacion_queries.md): el mismo contenido en
  Markdown. Es la fuente del PDF.
- [`medir_consultas.py`](medir_consultas.py): genera la tabla en SQLite y
  mide las dos versiones (plan de ejecución, filas recorridas, tiempos,
  lectura en Parquet y RAM en pandas). De ahí salen los números del documento.
- [`generar_pdf.py`](generar_pdf.py): arma el PDF desde el `.md` con `reportlab`.

## Resumen

| | Ineficiente | Optimizada |
|---|---|---|
| Columnas | `SELECT *` (50) | `monto`, `categoria`, `fecha` |
| Filtro de fecha | `YEAR(fecha) = 2023` (no sargable) | `fecha >= '2023-01-01' AND fecha <= '2023-12-31'` (sargable) |
| Estructura | Subconsulta innecesaria | Una sola agregación |
| Uso del índice `(categoria, fecha)` | Solo por categoría | Categoría + rango de fechas |
| Filas recorridas (1M) | 124.885 | 25.034 |
| Con índice cubriente | 34,6 ms | 1,4 ms (25x) |
| Bytes leídos en Parquet | 220,5 MB | 7,7 MB (29x menos) |
| RAM en pandas (estimada, 10M) | ~1,6 GB (todo 2023) a ~8 GB (tabla completa) | 140 bytes |

## Cómo reproducir las mediciones

```bash
pip install pandas pyarrow
python medir_consultas.py            # 1 millón de filas (~1 min, ~750 MB en disco)
python medir_consultas.py 10000000   # la escala real de la consigna (~7,5 GB en disco)
python generar_pdf.py                # regenera el PDF desde el .md
```

La base `ventas_globales.db` queda en esta carpeta y no se sube al repo
(`*.db` está en el `.gitignore`). Como los datos se generan al azar, cada
corrida da números un poco distintos, pero con las mismas proporciones.

---

Tomás Bezzana
