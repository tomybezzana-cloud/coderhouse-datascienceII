# Práctica 15: SQL aplicado al análisis exploratorio

Consultas SQL sobre la tabla `ventas_retail` para responder cuatro preguntas
de negocio típicas de la exploración inicial de un proyecto de Data Science:
selección con alias, filtrado con ordenamiento, Top N con `LIMIT` y
agregación con `GROUP BY` + `HAVING`.

Archivos:

- [`Consultas_SQL_Ventas_Retail_Bezzana_Tomas.pdf`](Consultas_SQL_Ventas_Retail_Bezzana_Tomas.pdf):
  **el entregable** (3 páginas). Tiene las 4 consultas comentadas, el
  resultado de cada una y el checklist de criterios de aceptación.
- [`consultas_ejercicio_sql.md`](consultas_ejercicio_sql.md): el mismo
  contenido en Markdown. Es la fuente: el PDF y la prueba se generan a partir
  de este archivo.
- [`generar_pdf.py`](generar_pdf.py): arma el PDF desde el `.md` con
  `reportlab` (`python generar_pdf.py`).
- [`probar_consultas.py`](probar_consultas.py): lee las consultas
  directamente del `.md`, las ejecuta en SQLite (en memoria) sobre 24 ventas
  de ejemplo y verifica que devuelvan lo esperado.

## Consultas

| # | Pregunta | Cláusulas clave |
|---|---|---|
| 1 | Productos y su precio, con la columna renombrada a `p_u_usd` | `SELECT DISTINCT`, `AS` |
| 2 | Ventas de la región `'Norte'` con más de 10 unidades, de la más reciente a la más antigua | `WHERE ... AND ...`, `ORDER BY fecha DESC` |
| 3 | Las 5 ventas con el precio unitario más alto | `ORDER BY ... DESC`, `LIMIT 5` |
| 4 | Unidades totales y precio promedio por categoría, solo las que superan 500 unidades | `SUM`, `AVG`, `GROUP BY`, `HAVING` |

Los datos de ejemplo están armados para probar los casos límite: una venta
del Norte con **exactamente 10** unidades y una categoría con **exactamente
500** unidades. Las dos tienen que quedar afuera, porque las condiciones son
`>` y no `>=`.

## Cómo probarlo

```bash
python probar_consultas.py
```

No requiere instalar nada (`sqlite3` viene con Python). Imprime el resultado
de cada consulta y al final `OK` si coincide con lo esperado.

---

Tomás Bezzana
