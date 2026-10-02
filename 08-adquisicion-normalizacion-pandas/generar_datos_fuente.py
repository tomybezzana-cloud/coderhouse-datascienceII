"""
Genera los archivos fuente de ejemplo para la pre-entrega:

- data/transacciones.csv  -> transacciones de ventas (departamento comercial)
- data/productos.xlsx     -> maestro de productos (departamento de compras)

Los datos se generan con una semilla fija (reproducibles) y se les agregan
"suciedades" típicas de un escenario real a propósito, para que el script de
adquisición tenga algo que corregir:

- IDs de producto guardados como texto, con espacios y vacíos.
- Cantidades nulas y no positivas.
- Fechas vacías o con texto inválido.
- Filas duplicadas.
- En el Excel: el ID guardado como texto (no como número), un precio y un
  nombre faltantes, y un producto repetido.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SEMILLA = 42


def generar_productos() -> pd.DataFrame:
    productos = pd.DataFrame(
        {
            "id_producto": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            "nombre_producto": [
                "Notebook 14\"",
                "Mouse inalámbrico",
                "Teclado mecánico",
                "Monitor 24\"",
                "Auriculares Bluetooth",
                "Webcam HD",
                "Disco SSD 1TB",
                "Memoria RAM 16GB",
                "Hub USB-C",
                "Silla ergonómica",
            ],
            "categoria": [
                "Computación",
                "Periféricos",
                "Periféricos",
                "Monitores",
                "Audio",
                "Periféricos",
                "Componentes",
                "Componentes",
                "Periféricos",
                "Mobiliario",
            ],
            "precio_unitario": [
                850000.0, 25000.0, 95000.0, 320000.0, 60000.0,
                45000.0, 110000.0, 75000.0, 30000.0, 410000.0,
            ],
        }
    )

    # Suciedades del maestro de productos
    productos.loc[productos["id_producto"] == 106, "precio_unitario"] = np.nan
    productos.loc[productos["id_producto"] == 109, "nombre_producto"] = np.nan
    # Producto cargado dos veces por error
    productos = pd.concat([productos, productos.iloc[[2]]], ignore_index=True)
    # El departamento de compras guarda el ID como texto en el Excel
    productos["id_producto"] = productos["id_producto"].astype(str)
    return productos


def generar_transacciones() -> pd.DataFrame:
    rng = np.random.default_rng(SEMILLA)
    n = 200

    ids = rng.choice(np.arange(101, 111), size=n)
    cantidades = rng.integers(1, 6, size=n).astype(float)
    fechas = pd.to_datetime("2026-01-01") + pd.to_timedelta(
        rng.integers(0, 180, size=n), unit="D"
    )

    transacciones = pd.DataFrame(
        {
            "id_transaccion": np.arange(1, n + 1),
            "id_producto": ids.astype(str),
            "cantidad": cantidades,
            "fecha": fechas.strftime("%Y-%m-%d"),
        }
    )

    # Suciedades de las transacciones
    transacciones.loc[[5, 17, 42], "id_producto"] = [" 103 ", "104 ", " 101"]
    transacciones.loc[[60, 61], "id_producto"] = ""          # sin producto
    transacciones.loc[75, "id_producto"] = "999"              # producto inexistente
    transacciones.loc[[10, 88, 150], "cantidad"] = np.nan     # cantidad faltante
    transacciones.loc[[30], "cantidad"] = 0                   # cantidad no válida
    transacciones.loc[[120], "cantidad"] = -2                 # devolución mal cargada
    transacciones.loc[[25, 99], "fecha"] = ""                 # fecha faltante
    transacciones.loc[[140], "fecha"] = "fecha_invalida"      # fecha corrupta

    # Dos transacciones duplicadas (mismo registro exportado dos veces)
    transacciones = pd.concat(
        [transacciones, transacciones.iloc[[3, 50]]], ignore_index=True
    )
    return transacciones


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    productos = generar_productos()
    with pd.ExcelWriter(DATA_DIR / "productos.xlsx", engine="openpyxl") as writer:
        productos.to_excel(writer, sheet_name="maestro_productos", index=False)

    transacciones = generar_transacciones()
    transacciones.to_csv(DATA_DIR / "transacciones.csv", index=False)

    print(f"Generado: {DATA_DIR / 'productos.xlsx'} ({len(productos)} filas)")
    print(f"Generado: {DATA_DIR / 'transacciones.csv'} ({len(transacciones)} filas)")


if __name__ == "__main__":
    main()
