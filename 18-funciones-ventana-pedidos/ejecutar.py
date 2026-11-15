"""
Ejecuta funciones_ventana.sql con el sqlite3 de la biblioteca estándar de
Python (no requiere instalar nada) e imprime el resultado de cada consulta.

Uso:
    python ejecutar.py
"""

import sqlite3
import sys
from pathlib import Path

RUTA_SQL = Path(__file__).resolve().parent / "funciones_ventana.sql"


def sentencias(sql: str) -> list[str]:
    """Separa el script en sentencias (cada una termina en ';' a fin de línea)
    y descarta los fragmentos que son solo comentarios."""
    resultado = []
    for bloque in sql.split(";\n"):
        codigo = [l for l in bloque.splitlines() if l.strip() and not l.strip().startswith("--")]
        if codigo:
            resultado.append(bloque.strip())
    return resultado


def mostrar(columnas: list[str], filas: list[tuple]) -> None:
    celdas = [columnas] + [["-" if v is None else str(v) for v in f] for f in filas]
    anchos = [max(len(f[i]) for f in celdas) for i in range(len(columnas))]
    for n, fila in enumerate(celdas):
        print("  " + " | ".join(v.ljust(a) for v, a in zip(fila, anchos)))
        if n == 0:
            print("  " + "-+-".join("-" * a for a in anchos))


def main() -> None:
    # Para que "Electrónica" se vea bien también en la consola de Windows
    sys.stdout.reconfigure(encoding="utf-8")
    con = sqlite3.connect(":memory:")
    filas_tabla = None
    n_consulta = 0
    for sentencia in sentencias(RUTA_SQL.read_text(encoding="utf-8")):
        cursor = con.execute(sentencia)
        if cursor.description is None:  # DROP / CREATE / INSERT
            continue
        if filas_tabla is None:
            filas_tabla = con.execute("SELECT count(*) FROM pedidos").fetchone()[0]
        n_consulta += 1
        filas = cursor.fetchall()
        print(f"\n--- Consulta {n_consulta}: {len(filas)} filas "
              f"(la tabla tiene {filas_tabla}) ---")
        mostrar([d[0] for d in cursor.description], filas)
    con.close()


if __name__ == "__main__":
    main()
