-- Caso 1: Transacción exitosa (COMMIT)
--
-- Principio ACID protegido: ATOMICIDAD + DURABILIDAD.
-- El descuento de stock (UPDATE) y su registro de auditoría (INSERT) son
-- dos operaciones que representan UN solo hecho de negocio ("se vendieron
-- 50 unidades"). Al envolverlas en una transacción, o se guardan las dos, o
-- ninguna: nunca vamos a terminar con un stock descontado sin su auditoría
-- (o viceversa). Una vez hecho el COMMIT, SQLite garantiza que el cambio es
-- durable: sobrevive aunque la base se cierre o el proceso se reinicie.

-- Estado ANTES de la venta:
SELECT id, nombre, stock FROM productos WHERE id = 1;
SELECT COUNT(*) AS movimientos_antes FROM ventas_log;

BEGIN TRANSACTION;

-- Se vendieron 50 unidades del producto 1: se descuenta del stock.
UPDATE productos
SET stock = stock - 50
WHERE id = 1;

-- Se deja registro de auditoría de ese movimiento.
INSERT INTO ventas_log (id_producto, cantidad, fecha, detalle)
VALUES (1, 50, '2026-09-23', 'Venta registrada: descuenta stock del producto 1');

COMMIT;

-- Estado DESPUÉS del COMMIT: ambos cambios deben persistir juntos.
SELECT id, nombre, stock FROM productos WHERE id = 1;
SELECT * FROM ventas_log;
