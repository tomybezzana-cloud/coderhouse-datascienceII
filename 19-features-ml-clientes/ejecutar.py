"""
Ejecuta features_clientes.sql e imprime el resultado de cada consulta.

Uso:
    python ejecutar.py            # SQLite de la biblioteca estándar (no requiere instalar nada)
    python ejecutar.py --duckdb   # DuckDB (pip install duckdb)
"""

import sys
from pathlib import Path

RUTA_SQL = Path(__file__).resolve().parent / "features_clientes.sql"
MARCA = "-- Consulta:"


def sentencias(sql: str) -> list[tuple[str | None, str]]:
    """Separa el script en sentencias (cada una termina en ';' a fin de línea).
    Devuelve (título, sentencia); el título sale del comentario '-- Consulta:'
    que precede a cada SELECT. Descarta los fragmentos que son solo comentarios."""
    resultado = []
    for bloque in sql.split(";\n"):
        lineas = bloque.splitlines()
        codigo = [l for l in lineas if l.strip() and not l.strip().startswith("--")]
        if not codigo:
            continue
        titulo = next((l.strip()[len(MARCA):].strip() for l in lineas
                       if l.strip().startswith(MARCA)), None)
        resultado.append((titulo, bloque.strip()))
    return resultado


def formatear(v, columna: str) -> str:
    """Los importes salen siempre con 2 decimales (SQLite devuelve 415 como
    entero y 411.5 como float; DuckDB devuelve Decimal)."""
    if v is None:
        return "-"
    es_importe = columna.startswith(("gasto", "promedio"))
    if es_importe or isinstance(v, float) or type(v).__name__ == "Decimal":
        return f"{float(v):.2f}"
    return str(v)


def mostrar(columnas: list[str], filas: list[tuple]) -> None:
    celdas = [columnas] + [[formatear(v, c) for v, c in zip(f, columnas)] for f in filas]
    anchos = [max(len(f[i]) for f in celdas) for i in range(len(columnas))]
    for n, fila in enumerate(celdas):
        print("  " + " | ".join(v.ljust(a) for v, a in zip(fila, anchos)))
        if n == 0:
            print("  " + "-+-".join("-" * a for a in anchos))


def conectar(usar_duckdb: bool):
    if usar_duckdb:
        import duckdb
        return duckdb.connect(":memory:")
    import sqlite3
    return sqlite3.connect(":memory:")


def main() -> None:
    # Para que los acentos se vean bien también en la consola de Windows
    sys.stdout.reconfigure(encoding="utf-8")
    usar_duckdb = "--duckdb" in sys.argv
    con = conectar(usar_duckdb)
    print(f"Motor: {'DuckDB' if usar_duckdb else 'SQLite'}")
    for titulo, sentencia in sentencias(RUTA_SQL.read_text(encoding="utf-8")):
        cursor = con.execute(sentencia)
        if titulo is None:  # DROP / CREATE / INSERT
            continue
        filas = cursor.fetchall()
        print(f"\n--- {titulo} ({len(filas)} filas) ---")
        mostrar([d[0] for d in cursor.description], filas)
    con.close()


if __name__ == "__main__":
    main()
