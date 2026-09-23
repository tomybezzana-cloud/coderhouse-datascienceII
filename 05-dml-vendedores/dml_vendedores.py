"""
Práctica de DML: Crear, Consultar, Actualizar y Eliminar Datos.

Simula las tareas típicas de un Analista de Datos sobre una tabla de
vendedores, usando sqlite3 (incluido en Python) para crear el archivo
practica_dml.db y ejecutar cada operación DML paso a paso.
"""

import sqlite3

conexion = sqlite3.connect("practica_dml.db")
cursor = conexion.cursor()

# ---------------------------------------------------------------------------
# 1. Preparación y Consulta (SELECT)
# ---------------------------------------------------------------------------

# Se recrea la tabla en cada corrida para que el ejercicio sea repetible.
cursor.execute("DROP TABLE IF EXISTS vendedores")
cursor.execute(
    """
    CREATE TABLE vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ventas_totales REAL NOT NULL,
        zona TEXT NOT NULL,
        fecha_ingreso TEXT NOT NULL
    )
    """
)

# Carga de registros iniciales (DDL/DML de arranque, no forma parte del reto).
cursor.executemany(
    """
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES (?, ?, ?, ?)
    """,
    [
        ("Ana García", 8500, "Norte", "2022-01-15"),
        ("Luis Martínez", 12000, "Sur", "2021-11-03"),
        ("Marta Rodríguez", 9500, "Norte", "2023-03-20"),
        ("Carlos Pérez", 15300, "Este", "2020-07-10"),
        ("Sofía Torres", 4200, "Norte", "2023-09-01"),
    ],
)
conexion.commit()

# ¿Qué vendedores tiene la zona Norte y cuánto vendieron?
print("Vendedores de la zona Norte:")
cursor.execute(
    "SELECT nombre, ventas_totales FROM vendedores WHERE zona = 'Norte'"
)
for fila in cursor.fetchall():
    print(f"  {fila[0]} -> {fila[1]}")

# ---------------------------------------------------------------------------
# 2. Expansión (INSERT)
# ---------------------------------------------------------------------------

# Alta de dos vendedores nuevos, con valores para todas las columnas.
cursor.execute(
    """
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES ('Juan Ramírez', 3000, 'Oeste', '2024-01-05')
    """
)
cursor.execute(
    """
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES ('Elena Fernández', 7600, 'Sur', '2024-02-18')
    """
)

# INSERT masivo: 3 registros en una sola sentencia. El tercero es un
# vendedor de prueba que se va a eliminar en el paso de limpieza.
cursor.execute(
    """
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES
        ('Diego Suárez', 6100, 'Este', '2024-03-10'),
        ('Paula Gómez', 11200, 'Oeste', '2024-04-22'),
        ('Vendedor Prueba', 0, 'Test', '2024-06-01')
    """
)
conexion.commit()

# ---------------------------------------------------------------------------
# 3. Mantenimiento (UPDATE)
# ---------------------------------------------------------------------------

# El vendedor id = 2 sumó una nueva venta de 500 unidades.
cursor.execute(
    "UPDATE vendedores SET ventas_totales = ventas_totales + 500 WHERE id = 2"
)

# Reto: todo vendedor con ventas_totales > 10000 pasa a zona Internacional.
cursor.execute(
    "UPDATE vendedores SET zona = 'Internacional' WHERE ventas_totales > 10000"
)
conexion.commit()

print("\nVendedores tras las actualizaciones:")
cursor.execute("SELECT id, nombre, ventas_totales, zona FROM vendedores")
for fila in cursor.fetchall():
    print(f"  {fila}")

# ---------------------------------------------------------------------------
# 4. Limpieza (DELETE)
# ---------------------------------------------------------------------------

# Se elimina el vendedor de prueba identificándolo por su id.
cursor.execute("SELECT id FROM vendedores WHERE nombre = 'Vendedor Prueba'")
id_prueba = cursor.fetchone()[0]
cursor.execute("DELETE FROM vendedores WHERE id = ?", (id_prueba,))
conexion.commit()

# Verificación: la fila ya no debería aparecer.
print(f"\nVerificación tras eliminar id = {id_prueba}:")
cursor.execute("SELECT * FROM vendedores WHERE id = ?", (id_prueba,))
resultado = cursor.fetchone()
print("  Fila encontrada:", resultado if resultado else "ninguna (eliminada correctamente)")

conexion.close()
