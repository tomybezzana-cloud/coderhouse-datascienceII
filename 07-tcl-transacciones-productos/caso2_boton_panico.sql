-- Caso 2: El botón de pánico (ROLLBACK)
--
-- Principio ACID protegido: ATOMICIDAD (y con eso, la Consistencia de los
-- datos). Mientras una transacción no hace COMMIT, ningún cambio dentro de
-- ella es definitivo. Eso permite deshacer por completo un error humano
-- -como un DELETE sin cláusula WHERE- con un simple ROLLBACK, como si nunca
-- hubiera pasado.

-- Estado ANTES del error accidental:
SELECT COUNT(*) AS productos_antes FROM productos;

BEGIN TRANSACTION;

-- Error humano: DELETE sin WHERE, borra TODOS los productos de la tabla.
DELETE FROM productos;

-- Si consultáramos acá (todavía dentro de la transacción), ya veríamos 0
-- filas: el borrado ya se aplicó, pero aún no está confirmado.
SELECT COUNT(*) AS productos_durante_transaccion FROM productos;

-- Como no se hizo COMMIT, el desastre se puede deshacer por completo:
ROLLBACK;

-- Estado DESPUÉS del ROLLBACK: los datos deben seguir intactos, como si el
-- DELETE nunca se hubiera ejecutado.
SELECT COUNT(*) AS productos_despues FROM productos;
SELECT * FROM productos;
