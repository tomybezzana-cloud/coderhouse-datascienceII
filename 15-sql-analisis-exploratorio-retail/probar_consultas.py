"""
Práctica 15: SQL aplicado al análisis exploratorio (tabla ventas_retail).

Las consultas del entregable están en consultas_ejercicio_sql.md. Este script
las lee directamente de ese archivo (los bloques ```sql que empiezan con
"-- Consulta"), crea la tabla en una base SQLite en memoria con datos de
ejemplo y ejecuta cada una, para comprobar que corren y que devuelven lo
esperado. Así el .md y lo que se prueba nunca quedan desincronizados.

Uso:
    python probar_consultas.py
"""

import re
import sqlite3
from pathlib import Path

RUTA_MD = Path(__file__).resolve().parent / "consultas_ejercicio_sql.md"

ESQUEMA = """
CREATE TABLE ventas_retail (
    id_transaccion  INTEGER PRIMARY KEY,
    fecha           DATE,
    producto        TEXT,
    categoria       TEXT,
    cantidad        INTEGER,
    precio_unitario DECIMAL(10, 2),
    region          TEXT
);
"""

# Datos de ejemplo pensados para poner a prueba los bordes de cada consulta:
# - Región Norte con cantidad 10 exacta (id 12): debe quedar AFUERA de "> 10".
# - Deportes suma exactamente 500 unidades: debe quedar AFUERA de "> 500".
# - Electrónica (520) y Hogar (640) superan 500; Juguetes (310) no.
# - "Cafetera" se vende dos veces al mismo precio (ids 9 y 13): DISTINCT la
#   muestra una sola vez. "Auriculares" y "Smartwatch" cambian de precio, así
#   que aparecen dos veces cada uno.
VENTAS = [
    (1, "2026-01-05", "Auriculares Bluetooth", "Electrónica", 120, 45.90, "Norte"),
    (2, "2026-01-18", "Smartwatch", "Electrónica", 35, 189.99, "Sur"),
    (3, "2026-02-02", "Parlante portátil", "Electrónica", 60, 79.50, "Norte"),
    (4, "2026-02-20", "Tablet 10 pulgadas", "Electrónica", 8, 349.00, "Norte"),
    (5, "2026-03-03", "Auriculares Bluetooth", "Electrónica", 150, 44.50, "Este"),
    (6, "2026-03-15", "Monitor 27 pulgadas", "Electrónica", 12, 289.00, "Norte"),
    (7, "2026-04-01", "Smartwatch", "Electrónica", 40, 179.99, "Oeste"),
    (8, "2026-04-22", "Cámara de seguridad", "Electrónica", 95, 62.00, "Sur"),
    (9, "2026-01-09", "Cafetera", "Hogar", 70, 95.00, "Sur"),
    (10, "2026-01-27", "Juego de sábanas", "Hogar", 150, 32.50, "Norte"),
    (11, "2026-02-11", "Lámpara LED", "Hogar", 200, 18.75, "Este"),
    (12, "2026-03-08", "Aspiradora robot", "Hogar", 10, 420.00, "Norte"),
    (13, "2026-03-29", "Cafetera", "Hogar", 90, 95.00, "Oeste"),
    (14, "2026-04-14", "Freidora de aire", "Hogar", 120, 129.90, "Norte"),
    (15, "2026-01-14", "Pelota de fútbol", "Deportes", 180, 22.00, "Este"),
    (16, "2026-02-06", "Bicicleta urbana", "Deportes", 6, 650.00, "Norte"),
    (17, "2026-02-25", "Mancuernas 5 kg", "Deportes", 140, 28.40, "Sur"),
    (18, "2026-03-19", "Colchoneta de yoga", "Deportes", 110, 19.90, "Norte"),
    (19, "2026-04-09", "Zapatillas running", "Deportes", 64, 110.00, "Oeste"),
    (20, "2026-01-22", "Rompecabezas 1000 piezas", "Juguetes", 75, 15.50, "Norte"),
    (21, "2026-02-15", "Bloques de construcción", "Juguetes", 40, 59.90, "Este"),
    (22, "2026-03-11", "Muñeca articulada", "Juguetes", 9, 24.00, "Norte"),
    (23, "2026-03-30", "Auto a control remoto", "Juguetes", 66, 48.00, "Sur"),
    (24, "2026-04-18", "Juego de mesa", "Juguetes", 120, 34.90, "Norte"),
]

# Lo que cada consulta tiene que devolver con estos datos (para validarlas).
ESPERADO = {
    1: lambda filas: len(filas) == 23,  # 24 ventas, una Cafetera repetida
    2: lambda filas: [f[0] for f in filas] == [24, 14, 18, 6, 3, 10, 20, 1],
    3: lambda filas: [f[0] for f in filas] == [16, 12, 4, 6, 2],
    4: lambda filas: [f[0] for f in filas] == ["Hogar", "Electrónica"],
}


def leer_consultas(ruta: Path) -> list[str]:
    """Devuelve los bloques ```sql del .md que empiezan con '-- Consulta'."""
    bloques = re.findall(r"```sql\n(.*?)```", ruta.read_text(encoding="utf-8"), re.S)
    return [b.strip() for b in bloques if b.lstrip().startswith("-- Consulta")]


def mostrar(cursor: sqlite3.Cursor, filas: list[tuple]) -> None:
    """Imprime el resultado como una tabla de texto alineada."""
    columnas = [d[0] for d in cursor.description]
    celdas = [columnas] + [["" if v is None else str(v) for v in f] for f in filas]
    anchos = [max(len(fila[i]) for fila in celdas) for i in range(len(columnas))]
    for n, fila in enumerate(celdas):
        print(" | ".join(v.ljust(a) for v, a in zip(fila, anchos)))
        if n == 0:
            print("-+-".join("-" * a for a in anchos))


def main() -> None:
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute(ESQUEMA)
    cursor.executemany("INSERT INTO ventas_retail VALUES (?, ?, ?, ?, ?, ?, ?);", VENTAS)

    consultas = leer_consultas(RUTA_MD)
    for numero, sql in enumerate(consultas, start=1):
        print(f"\n=== Consulta {numero} ===")
        filas = cursor.execute(sql).fetchall()
        mostrar(cursor, filas)
        estado = "OK" if ESPERADO[numero](filas) else "NO COINCIDE CON LO ESPERADO"
        print(f"({len(filas)} filas) -> {estado}")

    conexion.close()


if __name__ == "__main__":
    main()
