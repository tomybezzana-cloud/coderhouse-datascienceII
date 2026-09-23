# Práctica 7: TCL - Asegurar cambios con transacciones y ACID

Repositorio de transacciones seguras en SQLite: `BEGIN` / `COMMIT` /
`ROLLBACK` sobre una tabla `productos` y su tabla de auditoría
`ventas_log`, demostrando cómo SQLite protege cada principio ACID.

Archivos:

- [`schema.sql`](schema.sql) — crea `productos` y `ventas_log`, y carga los datos iniciales.
- [`caso1_transaccion_exitosa.sql`](caso1_transaccion_exitosa.sql) — Caso 1: COMMIT.
- [`caso2_boton_panico.sql`](caso2_boton_panico.sql) — Caso 2: ROLLBACK.
- [`caso3_atomicidad_fallo.sql`](caso3_atomicidad_fallo.sql) — Caso 3: fallo a mitad de transacción.
- [`ejecutar_transacciones.py`](ejecutar_transacciones.py) — corre los 4 scripts contra `practica_tcl.db` y muestra el resultado de cada `SELECT` por consola, para verificar el comportamiento real.

## Qué resuelve cada script

### Caso 1 — Transacción exitosa (`COMMIT`)

Una venta de 50 unidades del producto 1 implica dos cambios que deben viajar
juntos: descontar `stock` (`UPDATE`) y dejar registro en `ventas_log`
(`INSERT`). Se protege:

- **Atomicidad**: ambas operaciones se confirman como una sola unidad.
- **Durabilidad**: después del `COMMIT`, el cambio sobrevive aunque se
  cierre la conexión o se reinicie la base.

### Caso 2 — El botón de pánico (`ROLLBACK`)

Simula un error humano clásico: un `DELETE FROM productos` sin cláusula
`WHERE`, que borraría toda la tabla. Como todavía no se hizo `COMMIT`, un
`ROLLBACK` deshace el borrado por completo. Se protege:

- **Atomicidad**: mientras no hay `COMMIT`, ningún cambio es definitivo.
- **Consistencia**: la base vuelve exactamente al estado válido anterior.

### Caso 3 — Atomicidad ante fallos lógicos (transferencia entre depósitos)

Se simula transferir 50 unidades de stock del producto 1 (Depósito Norte,
`id = 1`) al producto 4 (Depósito Sur, `id = 4`). El primer `UPDATE` es
válido; el segundo fuerza un error real (intenta poner `NULL` en una
columna `NOT NULL`). El script sigue con el `ROLLBACK` después del error, y
eso deshace **también** el primer `UPDATE`, aunque ese sí era válido: si no
se revirtiera, el stock quedaría descontado en el Norte sin haber llegado
nunca al Sur (stock "perdido"). Esto es exactamente lo que garantiza la
**Atomicidad**: una transacción se aplica entera o no se aplica nada.

## Cómo ejecutarlo

```bash
python ejecutar_transacciones.py
```

El script imprime, para cada archivo `.sql`, cada sentencia ejecutada y el
resultado de los `SELECT` de "antes" y "después", para poder comparar el
estado de la tabla en cada paso.

## Errores comunes evitados

- Cada `BEGIN TRANSACTION` de este repositorio termina siempre en un
  `COMMIT` o un `ROLLBACK` — ninguna transacción queda "colgada".
- Los scripts se ejecutan con `isolation_level=None` en Python (equivalente
  al modo autocommit de la consola `sqlite3`), para que el propio
  `BEGIN`/`COMMIT`/`ROLLBACK` del `.sql` sea el que controla la transacción
  y no una transacción implícita del driver.
