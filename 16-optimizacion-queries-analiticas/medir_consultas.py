"""
Práctica 16: Ejecución eficiente de queries analíticas.

Arma una tabla ventas_globales de 50 columnas en SQLite, con un índice sobre
(categoria, fecha), y compara la versión ineficiente y la optimizada de la
consulta "promedio de monto de Electrónica en 2023":

1. Plan de ejecución (EXPLAIN QUERY PLAN) de cada una.
2. Filas que cada una tiene que leer y tiempo de ejecución.
3. RAM que ocupa en pandas lo que cada enfoque trae de la base.

La consigna habla de 10 millones de filas; por defecto se generan 1 millón
para que corra en un par de minutos en una notebook, y la RAM se extrapola
multiplicando por 10 (crece en forma lineal con las filas).

Uso:
    python medir_consultas.py              # 1.000.000 de filas
    python medir_consultas.py 10000000     # escala real de la consigna
"""

import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RUTA_DB = BASE_DIR / "ventas_globales.db"  # ignorado por el .gitignore (*.db)
FILAS_REALES = 10_000_000

CATEGORIAS = ["Electrónica", "Hogar", "Deportes", "Juguetes",
              "Moda", "Alimentos", "Libros", "Belleza"]
PAISES = ["Argentina", "Brasil", "Chile", "México", "España", "Colombia", "Perú", "Uruguay"]

# 4 columnas del escenario + 46 de "relleno" que tiene cualquier tabla de
# ventas real (cliente, logística, marketing...). Se alternan enteros,
# decimales y texto para que el ancho de fila sea realista.
COLUMNAS_EXTRA = [f"atributo_{n:02d}" for n in range(1, 47)]


def tipo_extra(n: int) -> str:
    return ("INTEGER", "REAL", "TEXT")[n % 3]


def valor_extra(n: int) -> str:
    """Expresión SQL que genera un valor de ejemplo para la columna extra n."""
    return (
        "abs(random()) % 100000",
        "round(abs(random()) % 1000000 / 100.0, 2)",
        "'valor_texto_de_ejemplo_' || (abs(random()) % 1000)",
    )[n % 3]


def crear_tabla(conexion: sqlite3.Connection, filas: int) -> None:
    columnas_sql = ",\n".join(
        f"    {c} {tipo_extra(n)}" for n, c in enumerate(COLUMNAS_EXTRA)
    )
    conexion.executescript(f"""
        DROP TABLE IF EXISTS ventas_globales;
        CREATE TABLE ventas_globales (
            id_venta  INTEGER PRIMARY KEY,
            fecha     TEXT,      -- 'AAAA-MM-DD', 2020-01-01 a 2024-12-30
            categoria TEXT,
            monto     REAL,
        {columnas_sql}
        );
    """)

    categorias = "CASE abs(random()) % 8 " + " ".join(
        f"WHEN {i} THEN '{c}'" for i, c in enumerate(CATEGORIAS)) + " END"
    extras = ", ".join(valor_extra(n) for n in range(len(COLUMNAS_EXTRA)))
    # Las filas se generan dentro de SQLite con un CTE recursivo: mucho más
    # rápido que armarlas en Python e insertarlas una por una.
    conexion.execute(f"""
        INSERT INTO ventas_globales
        WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {filas})
        SELECT
            i,
            date('2020-01-01', '+' || (abs(random()) % 1825) || ' days'),
            {categorias},
            round(10 + abs(random()) % 200000 / 100.0, 2),
            {extras}
        FROM n;
    """)
    conexion.execute("CREATE INDEX idx_categoria_fecha ON ventas_globales (categoria, fecha);")
    conexion.execute("ANALYZE;")
    conexion.commit()


# SQLite no tiene YEAR(); strftime('%Y', fecha) es su equivalente y tiene el
# mismo problema: es una función aplicada sobre la columna.
CONSULTA_INEFICIENTE = """
SELECT AVG(t.monto) AS promedio_monto
FROM (
    SELECT *
    FROM ventas_globales
    WHERE CAST(strftime('%Y', fecha) AS INTEGER) = 2023
) AS t
WHERE t.categoria = 'Electrónica';
"""

CONSULTA_OPTIMIZADA = """
SELECT AVG(monto) AS promedio_monto
FROM ventas_globales
WHERE categoria = 'Electrónica'
  AND fecha >= '2023-01-01'
  AND fecha <= '2023-12-31';
"""

# Lo que suele pasar en la práctica en un notebook: traer la tabla "por las
# dudas" y filtrar en pandas. Es la forma en que SELECT * llega a la RAM.
TRAER_TODO = "SELECT * FROM ventas_globales WHERE CAST(strftime('%Y', fecha) AS INTEGER) = 2023;"
TRAER_3_COLUMNAS = """
SELECT monto, categoria, fecha
FROM ventas_globales
WHERE categoria = 'Electrónica' AND fecha >= '2023-01-01' AND fecha <= '2023-12-31';
"""


def plan(conexion: sqlite3.Connection, sql: str) -> list[str]:
    return [fila[3] for fila in conexion.execute("EXPLAIN QUERY PLAN " + sql)]


def cronometrar(conexion: sqlite3.Connection, sql: str, repeticiones: int = 3):
    """Mejor tiempo de varias corridas (la primera calienta la caché)."""
    tiempos, resultado = [], None
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = conexion.execute(sql).fetchone()[0]
        tiempos.append(time.perf_counter() - inicio)
    return resultado, min(tiempos)


def filas_leidas(conexion: sqlite3.Connection) -> tuple[int, int]:
    """Filas que cada versión tiene que recorrer según su plan.

    La ineficiente usa el índice solo por categoría (la función sobre la fecha
    le impide usarlo para el año), así que recorre Electrónica de los 5 años.
    La optimizada usa el índice por categoría y rango de fechas.
    """
    todas_electronica = conexion.execute(
        "SELECT COUNT(*) FROM ventas_globales WHERE categoria = 'Electrónica'").fetchone()[0]
    solo_2023 = conexion.execute(
        "SELECT COUNT(*) FROM ventas_globales WHERE categoria = 'Electrónica' "
        "AND fecha >= '2023-01-01' AND fecha <= '2023-12-31'").fetchone()[0]
    return todas_electronica, solo_2023


def memoria_pandas(conexion: sqlite3.Connection, sql: str) -> tuple[int, int, float]:
    df = pd.read_sql(sql, conexion)
    return len(df), df.shape[1], df.memory_usage(deep=True).sum() / 1e6


def medir_columnar(conexion: sqlite3.Connection) -> None:
    """Exporta la tabla a Parquet y compara cuánto hay que leer del disco.

    En un formato columnar cada columna se guarda por separado, así que el
    motor lee solo los bloques de las columnas pedidas. Es como funcionan
    BigQuery, Snowflake, Redshift o un data lake en Parquet.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    ruta = BASE_DIR / "ventas_globales.parquet"  # ignorado por el .gitignore
    pq.write_table(
        pa.Table.from_pandas(pd.read_sql("SELECT * FROM ventas_globales", conexion),
                                preserve_index=False),
        ruta, row_group_size=100_000,
    )
    meta = pq.ParquetFile(ruta).metadata

    def bytes_de(columnas):
        return sum(
            meta.row_group(g).column(c).total_compressed_size
            for g in range(meta.num_row_groups)
            for c in range(meta.num_columns)
            if meta.schema.column(c).name in columnas
        )

    todas = [meta.schema.column(c).name for c in range(meta.num_columns)]
    filtro = [("categoria", "=", "Electrónica"),
              ("fecha", ">=", "2023-01-01"), ("fecha", "<=", "2023-12-31")]
    for nombre, columnas in [("SELECT * (50 columnas)", todas),
                             ("monto, categoria, fecha", ["monto", "categoria", "fecha"])]:
        inicio = time.perf_counter()
        tabla = pq.read_table(ruta, columns=columnas, filters=filtro)
        tiempo = time.perf_counter() - inicio
        print(f"{nombre}: {bytes_de(columnas) / 1e6:,.1f} MB a leer, "
              f"{tiempo * 1000:,.0f} ms, {tabla.num_rows:,} filas resultantes")
    ruta.unlink()


def main() -> None:
    filas = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    escala = FILAS_REALES / filas

    conexion = sqlite3.connect(RUTA_DB)
    print(f"Generando ventas_globales: {filas:,} filas x {4 + len(COLUMNAS_EXTRA)} columnas...")
    inicio = time.perf_counter()
    crear_tabla(conexion, filas)
    print(f"  listo en {time.perf_counter() - inicio:.0f} s "
          f"({RUTA_DB.stat().st_size / 1e6:,.0f} MB en disco)")

    print("\n=== Plan de ejecución (EXPLAIN QUERY PLAN) ===")
    for nombre, sql in [("Ineficiente", CONSULTA_INEFICIENTE), ("Optimizada", CONSULTA_OPTIMIZADA)]:
        print(f"{nombre}:")
        for paso in plan(conexion, sql):
            print(f"  {paso}")

    print("\n=== Filas recorridas y tiempo ===")
    leidas_inef, leidas_opt = filas_leidas(conexion)
    res_inef, t_inef = cronometrar(conexion, CONSULTA_INEFICIENTE)
    res_opt, t_opt = cronometrar(conexion, CONSULTA_OPTIMIZADA)
    print(f"Ineficiente: {leidas_inef:,} filas recorridas, {t_inef * 1000:,.0f} ms, promedio = {res_inef:.2f}")
    print(f"Optimizada:  {leidas_opt:,} filas recorridas, {t_opt * 1000:,.0f} ms, promedio = {res_opt:.2f}")
    print(f"Mismo resultado: {abs(res_inef - res_opt) < 1e-9}  |  "
          f"{leidas_inef / leidas_opt:.1f}x menos filas, {t_inef / t_opt:.1f}x más rápida")

    print("\n=== Con índice cubriente (categoria, fecha, monto) ===")
    conexion.execute("CREATE INDEX idx_cubriente ON ventas_globales (categoria, fecha, monto);")
    conexion.execute("ANALYZE;")
    for nombre, sql in [("Ineficiente", CONSULTA_INEFICIENTE), ("Optimizada", CONSULTA_OPTIMIZADA)]:
        resultado, tiempo = cronometrar(conexion, sql)
        print(f"{nombre}: {tiempo * 1000:,.1f} ms | {' / '.join(plan(conexion, sql))}")
    conexion.execute("DROP INDEX idx_cubriente;")

    print("\n=== Motor columnar (Parquet): bytes leídos según columnas pedidas ===")
    medir_columnar(conexion)

    print(f"\n=== RAM en pandas (medida con {filas:,} filas; x{escala:g} para 10M) ===")
    for nombre, sql in [("SELECT * del año 2023 (filtrar en pandas)", TRAER_TODO),
                        ("3 columnas, ya filtradas en SQL", TRAER_3_COLUMNAS),
                        ("Solo el promedio (agregado en SQL)", CONSULTA_OPTIMIZADA)]:
        n, cols, mb = memoria_pandas(conexion, sql)
        print(f"{nombre}: {n:,} filas x {cols} col -> {mb:,.3f} MB "
              f"(~{mb * escala:,.1f} MB con 10M filas)" if n > 1 else
              f"{nombre}: {n} fila x {cols} col -> {mb * 1e6:,.0f} bytes")

    conexion.close()


if __name__ == "__main__":
    main()
