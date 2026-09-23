-- Caso 3: Atomicidad ante fallos lógicos (transferencia entre depósitos)
--
-- Principio ACID protegido: ATOMICIDAD.
-- Se simula transferir 50 unidades del producto 1 (Depósito Norte) al
-- producto 4 (Depósito Sur): son dos UPDATE que solo tienen sentido juntos.
-- Si el segundo falla, el primero TIENE que deshacerse también, porque si
-- no el stock "desaparecería" de un depósito sin llegar nunca al otro.

-- Estado ANTES de la transferencia:
SELECT id, nombre, stock FROM productos WHERE id IN (1, 4);

BEGIN TRANSACTION;

-- Paso 1 (válido): se descuenta stock del Depósito Norte.
UPDATE productos
SET stock = stock - 50
WHERE id = 1;

-- Paso 2 (fuerza un error lógico): intenta dejar el stock del Depósito Sur
-- en NULL, lo que viola la restricción NOT NULL de la columna stock.
-- SQLite rechaza esta sentencia con un error de integridad; a diferencia de
-- una operación aislada, el UPDATE del Paso 1 todavía no fue confirmado, así
-- que se puede revertir.
UPDATE productos
SET stock = NULL
WHERE id = 4;

-- Como el Paso 2 falló, se deshace TODA la transacción (incluido el Paso 1,
-- que era válido) para no dejar el stock inconsistente entre depósitos.
ROLLBACK;

-- Estado DESPUÉS del ROLLBACK: el producto 1 debe conservar su stock
-- original, como si la transferencia nunca hubiera empezado.
SELECT id, nombre, stock FROM productos WHERE id IN (1, 4);
