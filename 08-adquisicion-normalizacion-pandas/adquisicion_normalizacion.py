"""
Pre-entrega: Adquisición y Normalización con Pandas.

Integra dos fuentes de datos de distinto formato:

- data/transacciones.csv  (CSV)   -> id_transaccion, id_producto, cantidad, fecha
- data/productos.xlsx     (Excel) -> id_producto, nombre_producto, categoria, precio_unitario

Pasos:
1. Adquisición: carga del CSV y del Excel.
2. Transformación: corrección de tipos, manejo de nulos y duplicados.
3. Merge por id_producto (con el mismo tipo de dato en ambas tablas).
4. Normalización: columna calculada total_venta = cantidad * precio_unitario.
5. Exportación a Parquet: output/ventas_consolidadas.parquet
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RUTA_CSV = BASE_DIR / "data" / "transacciones.csv"
RUTA_EXCEL = BASE_DIR / "data" / "productos.xlsx"
RUTA_PARQUET = BASE_DIR / "output" / "ventas_consolidadas.parquet"

COLUMNAS_CRITICAS = [
    "id_transaccion",
    "id_producto",
    "nombre_producto",
    "cantidad",
    "precio_unitario",
    "fecha",
    "total_venta",
]


def titulo(texto: str) -> None:
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


# ---------------------------------------------------------------------------
# 1. Adquisición
# ---------------------------------------------------------------------------
def cargar_transacciones(ruta: Path) -> pd.DataFrame:
    # Se lee id_producto y fecha como texto para limpiarlos de forma explícita
    # en lugar de dejar que pandas adivine el tipo.
    return pd.read_csv(ruta, dtype={"id_producto": "string", "fecha": "string"})


def cargar_productos(ruta: Path) -> pd.DataFrame:
    # El context manager cierra el motor de lectura de Excel (openpyxl) al
    # terminar, liberando el archivo. El ID está guardado como texto en el
    # Excel, así que se lee como texto y se convierte más adelante.
    with pd.ExcelFile(ruta, engine="openpyxl") as excel:
        return pd.read_excel(
            excel, sheet_name="maestro_productos", dtype={"id_producto": "string"}
        )


# ---------------------------------------------------------------------------
# 2. Transformación
# ---------------------------------------------------------------------------
def limpiar_transacciones(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    filas_iniciales = len(df)

    # Duplicados exactos (mismo registro exportado dos veces)
    df = df.drop_duplicates()
    print(f"- Duplicados eliminados: {filas_iniciales - len(df)}")

    # id_producto: texto con espacios / vacíos -> entero (Int64 admite nulos)
    df["id_producto"] = pd.to_numeric(
        df["id_producto"].str.strip(), errors="coerce"
    ).astype("Int64")

    # fecha: texto -> datetime; lo que no es una fecha válida queda como NaT
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")

    print("- Nulos por columna tras corregir tipos:")
    print(df.isna().sum().to_string())

    # Nulos: en una transacción, el producto, la cantidad y la fecha son el
    # hecho registrado en sí. Imputarlos sería inventar ventas, así que las
    # filas incompletas se eliminan.
    antes = len(df)
    df = df.dropna(subset=["id_producto", "cantidad", "fecha"])
    print(f"- Filas eliminadas por nulos en id_producto/cantidad/fecha: {antes - len(df)}")

    # Cantidades no positivas no son ventas válidas
    antes = len(df)
    df = df[df["cantidad"] > 0]
    print(f"- Filas eliminadas por cantidad <= 0: {antes - len(df)}")

    df["cantidad"] = df["cantidad"].astype("int64")
    df["id_producto"] = df["id_producto"].astype("int64")
    return df.reset_index(drop=True)


def limpiar_productos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # El Excel trae el ID como texto: se convierte al mismo tipo que en las
    # transacciones para que el merge funcione.
    df["id_producto"] = pd.to_numeric(df["id_producto"].str.strip(), errors="coerce")
    df = df.dropna(subset=["id_producto"])
    df["id_producto"] = df["id_producto"].astype("int64")

    # Un producto repetido rompería la relación "muchas transacciones -> un
    # producto" y duplicaría ventas en el merge.
    antes = len(df)
    df = df.drop_duplicates(subset="id_producto", keep="first")
    print(f"- Productos duplicados eliminados: {antes - len(df)}")

    print("- Nulos por columna:")
    print(df.isna().sum().to_string())

    # Nulos: en el maestro sí tiene sentido imputar, porque el producto existe
    # y tiene ventas asociadas que no queremos perder.
    #   * precio_unitario -> mediana de los productos de su misma categoría
    #   * nombre_producto -> etiqueta identificable a partir del ID
    mediana_categoria = df.groupby("categoria")["precio_unitario"].transform("median")
    df["precio_unitario"] = df["precio_unitario"].fillna(mediana_categoria)
    df["nombre_producto"] = df["nombre_producto"].fillna(
        "Producto " + df["id_producto"].astype(str) + " (sin nombre)"
    )

    df["precio_unitario"] = df["precio_unitario"].astype("float64")
    df["categoria"] = df["categoria"].astype("category")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Merge  +  4. Normalización
# ---------------------------------------------------------------------------
def integrar(transacciones: pd.DataFrame, productos: pd.DataFrame) -> pd.DataFrame:
    # Verificación explícita: la llave debe tener el mismo tipo en ambas tablas
    assert transacciones["id_producto"].dtype == productos["id_producto"].dtype, (
        "id_producto tiene tipos distintos en las dos fuentes"
    )

    # Merge con indicador para detectar transacciones de productos inexistentes
    # en el catálogo. validate asegura que cada transacción matchee como máximo
    # un producto.
    ventas = transacciones.merge(
        productos,
        on="id_producto",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    sin_catalogo = ventas[ventas["_merge"] == "left_only"]
    print(f"- Transacciones sin producto en el catálogo (descartadas): {len(sin_catalogo)}")
    if not sin_catalogo.empty:
        print(sin_catalogo[["id_transaccion", "id_producto"]].to_string(index=False))

    ventas = ventas[ventas["_merge"] == "both"].drop(columns="_merge")

    # Columna calculada
    ventas["total_venta"] = ventas["cantidad"] * ventas["precio_unitario"]

    columnas = [
        "id_transaccion",
        "fecha",
        "id_producto",
        "nombre_producto",
        "categoria",
        "cantidad",
        "precio_unitario",
        "total_venta",
    ]
    return ventas[columnas].sort_values(["fecha", "id_transaccion"]).reset_index(drop=True)


def validar(ventas: pd.DataFrame) -> None:
    nulos = ventas[COLUMNAS_CRITICAS].isna().sum()
    assert nulos.sum() == 0, f"Hay nulos en campos críticos:\n{nulos}"
    assert pd.api.types.is_datetime64_any_dtype(ventas["fecha"]), "fecha no es datetime"
    assert ventas["id_transaccion"].is_unique, "id_transaccion duplicado"
    assert (ventas["total_venta"] > 0).all(), "total_venta no positivo"
    print("- OK: sin nulos en campos críticos, fecha datetime, IDs únicos, totales > 0")


# ---------------------------------------------------------------------------
# 5. Exportación
# ---------------------------------------------------------------------------
def exportar(ventas: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(exist_ok=True)
    ventas.to_parquet(ruta, engine="pyarrow", index=False)

    # Relectura para comprobar que el archivo conserva datos y tipos
    releido = pd.read_parquet(ruta, engine="pyarrow")
    pd.testing.assert_frame_equal(ventas, releido)
    print(f"- Exportado: {ruta.relative_to(BASE_DIR)} ({ruta.stat().st_size:,} bytes)")
    print("- Relectura del Parquet idéntica al DataFrame original (datos y tipos)")


def main() -> None:
    titulo("1. Adquisición")
    transacciones = cargar_transacciones(RUTA_CSV)
    productos = cargar_productos(RUTA_EXCEL)
    print(f"- CSV  transacciones: {transacciones.shape[0]} filas x {transacciones.shape[1]} columnas")
    print(f"- XLSX productos:     {productos.shape[0]} filas x {productos.shape[1]} columnas")
    print("\nTipos originales (transacciones):")
    print(transacciones.dtypes.to_string())
    print("\nTipos originales (productos):")
    print(productos.dtypes.to_string())

    titulo("2. Transformación: transacciones")
    transacciones = limpiar_transacciones(transacciones)

    titulo("2. Transformación: productos")
    productos = limpiar_productos(productos)

    titulo("3-4. Merge por id_producto y columna calculada total_venta")
    ventas = integrar(transacciones, productos)

    titulo("Validación del dataset final")
    validar(ventas)
    print(f"\nDataset final: {ventas.shape[0]} filas x {ventas.shape[1]} columnas")
    print(ventas.dtypes.to_string())
    print()
    print(ventas.head(10).to_string(index=False))
    print(f"\nVenta total consolidada: $ {ventas['total_venta'].sum():,.2f}")

    titulo("5. Exportación a Parquet")
    exportar(ventas, RUTA_PARQUET)


if __name__ == "__main__":
    main()
