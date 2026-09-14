"""
Práctica de repaso de SQL - Data Science II
Objetivo: practicar extracción y manipulación de datos en una sola tabla,
simulando la exploración inicial que hace un Data Scientist antes de modelar.

Usamos sqlite3 (viene incluido en Python, no requiere instalar nada) para
crear una tabla en memoria y ejecutar las consultas SQL pedidas.
"""

import sqlite3

# ---------------------------------------------------------------
# Configuración: creamos la base de datos en memoria y la tabla
# ---------------------------------------------------------------
conexion = sqlite3.connect(":memory:")
cursor = conexion.cursor()

cursor.execute(
    """
    CREATE TABLE ventas_tecnologia (
        id_venta INTEGER PRIMARY KEY,
        producto TEXT,
        categoria TEXT,
        precio_unitario REAL,
        cantidad INTEGER,
        fecha TEXT,
        pais TEXT
    );
    """
)

# Datos de ejemplo. Dos filas (10 y 13) simulan el error típico de
# ingeniería: se olvidaron de cargar la categoría (queda NULL).
ventas = [
    (1, "Notebook Lenovo", "Notebooks", 850.00, 5, "2024-01-10", "Colombia"),
    (2, "Notebook HP", "Notebooks", 780.00, 3, "2024-01-15", "Argentina"),
    (3, "Celular Samsung A54", "Celulares", 600.00, 10, "2024-02-01", "Colombia"),
    (4, "Celular Motorola G84", "Celulares", 450.00, 8, "2024-02-05", "México"),
    (5, "Mouse Logitech", "Accesorios", 25.00, 50, "2024-01-20", "Chile"),
    (6, "Teclado Redragon", "Accesorios", 40.00, 30, "2024-01-22", "Colombia"),
    (7, "Monitor LG 24''", "Monitores", 220.00, 15, "2024-03-01", "Argentina"),
    (8, "Monitor Samsung 27''", "Monitores", 310.00, 12, "2024-03-05", "Colombia"),
    (9, "Notebook Dell", "Notebooks", 920.00, 4, "2024-03-10", "México"),
    (10, "Auriculares Sony", None, 60.00, 20, "2024-01-28", "Chile"),
    (11, "Celular iPhone 13", "Celulares", 999.00, 6, "2024-02-15", "Colombia"),
    (12, "Cargador USB-C", "Accesorios", 15.00, 100, "2024-01-25", "Argentina"),
    (13, "Webcam Logitech", None, 55.00, 25, "2024-02-20", "México"),
    (14, "Monitor AOC 22''", "Monitores", 180.00, 10, "2024-03-12", "Chile"),
    (15, "Notebook Asus", "Notebooks", 700.00, 7, "2024-03-15", "Colombia"),
]

cursor.executemany(
    "INSERT INTO ventas_tecnologia VALUES (?, ?, ?, ?, ?, ?, ?);", ventas
)
conexion.commit()


def ejecutar(titulo, query):
    """Corre una query y muestra el título y los resultados en consola."""
    print(f"\n=== {titulo} ===")
    cursor.execute(query)
    columnas = [d[0] for d in cursor.description]
    print(columnas)
    for fila in cursor.fetchall():
        print(fila)


# ---------------------------------------------------------------
# Pregunta de negocio: ¿qué productos vendemos y a qué precio,
# ordenados alfabéticamente? (Selección simple)
# ---------------------------------------------------------------
query_seleccion_simple = """
    SELECT producto, precio_unitario
    FROM ventas_tecnologia
    ORDER BY producto ASC;
"""
ejecutar("Productos y precios (orden alfabético)", query_seleccion_simple)

# ---------------------------------------------------------------
# Pregunta de negocio: ¿cuáles son las ventas de alto valor
# (precio_unitario > 500) realizadas en Colombia? (Filtrado crítico)
# ---------------------------------------------------------------
query_filtrado_critico = """
    SELECT *
    FROM ventas_tecnologia
    WHERE pais = 'Colombia' AND precio_unitario > 500;
"""
ejecutar("Ventas en Colombia con precio_unitario > 500", query_filtrado_critico)

# ---------------------------------------------------------------
# Pregunta de negocio: ¿hay ventas con la categoría sin cargar
# (NULL), producto de un olvido del equipo de ingeniería?
# ---------------------------------------------------------------
query_busqueda_nulos = """
    SELECT *
    FROM ventas_tecnologia
    WHERE categoria IS NULL;
"""
ejecutar("Ventas con categoría faltante (NULL)", query_busqueda_nulos)

# ---------------------------------------------------------------
# Pregunta de negocio: ¿cuánto ingreso total generó cada categoría
# de producto? (Agregación con alias)
# ---------------------------------------------------------------
query_ingresos_por_categoria = """
    SELECT categoria, SUM(cantidad * precio_unitario) AS ingresos_totales
    FROM ventas_tecnologia
    GROUP BY categoria;
"""
ejecutar("Ingresos totales por categoría", query_ingresos_por_categoria)

# ---------------------------------------------------------------
# Pregunta de negocio: ¿qué categorías son las "de élite", es decir,
# generaron más de $10.000 en ingresos totales? (Filtro con HAVING)
# ---------------------------------------------------------------
query_filtro_elite = """
    SELECT categoria, SUM(cantidad * precio_unitario) AS ingresos_totales
    FROM ventas_tecnologia
    GROUP BY categoria
    HAVING SUM(cantidad * precio_unitario) > 10000;
"""
ejecutar("Categorías con ingresos totales > $10.000", query_filtro_elite)

conexion.close()
