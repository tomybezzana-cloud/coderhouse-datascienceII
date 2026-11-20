"""
Ejecuta features_churn.sql con DuckDB e imprime el resultado de cada consulta.
Autor: Tomás Bezzana

Uso:
    python ejecutar.py

Si data/usuarios.csv o data/pedidos.csv no existen, los genera antes con
generar_datos.py.
"""

import os
import sys
from pathlib import Path

import duckdb

CARPETA = Path(__file__).resolve().parent
RUTA_SQL = CARPETA / "features_churn.sql"
MARCA = "-- Consulta:"


def sentencias(sql: str) -> list[tuple[str | None, str]]:
    """Separa el script en sentencias (cada una termina en ';' a fin de línea).
    El título de cada resultado sale del comentario '-- Consulta:' que la precede."""
    resultado = []
    for bloque in sql.split(";\n"):
        lineas = bloque.splitlines()
        if not [l for l in lineas if l.strip() and not l.strip().startswith("--")]:
            continue
        titulo = next((l.strip()[len(MARCA):].strip() for l in lineas
                       if l.strip().startswith(MARCA)), None)
        resultado.append((titulo, bloque.strip()))
    return resultado


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(CARPETA)  # las rutas del .sql (data/...) son relativas a esta carpeta

    if not (Path("data/usuarios.csv").exists() and Path("data/pedidos.csv").exists()):
        import generar_datos
        generar_datos.main()

    con = duckdb.connect(":memory:")
    for titulo, sentencia in sentencias(RUTA_SQL.read_text(encoding="utf-8")):
        if titulo is None:  # CREATE / COPY
            con.execute(sentencia)
            continue
        print(f"\n--- {titulo} ---")
        con.sql(sentencia).show(max_width=250)
    con.close()
    print("\nDataset exportado: data/features_churn.csv")


if __name__ == "__main__":
    main()
