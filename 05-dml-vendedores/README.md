# Práctica 5: DML - Crear, Consultar, Actualizar y Eliminar Datos

Archivo: [`dml_vendedores.py`](dml_vendedores.py)

Ejercicio de operaciones DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) sobre
una tabla `vendedores` en SQLite, simulando el mantenimiento diario de un
dataset que haría un Analista de Datos. Usa `sqlite3` (incluido en Python)
para crear el archivo `practica_dml.db`, cargarlo con datos de ejemplo y
ejecutar cada operación.

Columnas de `vendedores`: `id`, `nombre`, `ventas_totales`, `zona`,
`fecha_ingreso`.

## Qué resuelve cada bloque del script

1. **Preparación y Consulta (`SELECT`)**: crea la tabla `vendedores` con 5
   registros iniciales y consulta nombre y `ventas_totales` de los
   vendedores de la zona `'Norte'`, para saber quién vende ahí.
2. **Expansión (`INSERT`)**: da de alta dos vendedores nuevos con un
   `INSERT` por registro, y agrega 3 vendedores más en una sola sentencia
   (`INSERT` masivo), incluyendo un "Vendedor Prueba" que se usa más
   adelante para probar el borrado.
3. **Mantenimiento (`UPDATE`)**:
   - Suma 500 a las `ventas_totales` del vendedor `id = 2` por una nueva
     venta.
   - Cambia la `zona` a `'Internacional'` para todos los vendedores con más
     de 10.000 en `ventas_totales`.
4. **Limpieza (`DELETE`)**: busca el id del "Vendedor Prueba", lo elimina
   con `DELETE ... WHERE id = ?` y hace un `SELECT` final para confirmar
   que la fila ya no existe.

Cada `UPDATE` y `DELETE` del script incluye una cláusula `WHERE` para no
afectar filas de más.

## Cómo ejecutarlo

```bash
python dml_vendedores.py
```

Al correrlo se genera (o regenera) el archivo `practica_dml.db` en esta
misma carpeta.
