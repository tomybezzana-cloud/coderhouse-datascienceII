# Práctica 8 (Pre-entrega 2): Adquisición y Normalización con Pandas

Simula un escenario real donde los datos de ventas llegan de dos
departamentos en formatos distintos:

- **Comercial** exporta las transacciones en un **CSV**.
- **Compras** mantiene el maestro de productos en un **Excel (.xlsx)**.

El script integra ambas fuentes con `pandas`, corrige tipos, maneja nulos y
duplicados, calcula `total_venta` y exporta el dataset consolidado a
**Parquet**.

Archivos:

- [`generar_datos_fuente.py`](generar_datos_fuente.py): genera los archivos fuente de ejemplo (con semilla fija, así que siempre salen iguales) e incluye errores a propósito para que haya algo que limpiar.
- [`data/transacciones.csv`](data/transacciones.csv): transacciones (`id_transaccion`, `id_producto`, `cantidad`, `fecha`).
- [`data/productos.xlsx`](data/productos.xlsx): maestro de productos (`id_producto`, `nombre_producto`, `categoria`, `precio_unitario`), hoja `maestro_productos`.
- [`adquisicion_normalizacion.py`](adquisicion_normalizacion.py): el proceso completo de adquisición, transformación, merge, normalización y exportación.
- [`output/ventas_consolidadas.parquet`](output/ventas_consolidadas.parquet): el archivo final.
- [`requirements.txt`](requirements.txt): las librerías necesarias.

## Librerías necesarias

| Librería | Para qué se usa |
|----------|-----------------|
| `pandas` | Carga, limpieza, merge y exportación de los datos |
| `openpyxl` | Motor que usa pandas para leer y escribir `.xlsx` |
| `pyarrow` | Motor que usa pandas para escribir y leer `.parquet` |

Probado con Python 3.13, pandas 3.0.3, openpyxl 3.1.5 y pyarrow 25.0.1.

## Cómo reproducir la carga de datos

```bash
# 1. (Opcional) crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) regenerar los archivos fuente de ejemplo; ya vienen incluidos en data/
python generar_datos_fuente.py

# 4. Ejecutar el proceso de adquisición y normalización
python adquisicion_normalizacion.py
```

El paso 4 imprime por consola qué se corrigió en cada etapa y deja el
resultado en `output/ventas_consolidadas.parquet`. Para inspeccionarlo:

```python
import pandas as pd
df = pd.read_parquet("output/ventas_consolidadas.parquet")
print(df.dtypes)
print(df.head())
```

## Qué hace el script, paso a paso

### 1. Adquisición

- `pd.read_csv` lee las transacciones. `id_producto` y `fecha` se leen como
  texto a propósito, para limpiarlos de forma explícita en vez de dejar que
  pandas adivine el tipo.
- `pd.read_excel` lee el maestro de productos **dentro de un
  `with pd.ExcelFile(..., engine="openpyxl")`**, así el motor de lectura se
  cierra y el archivo se libera al terminar.

### 2. Transformación

**Transacciones (CSV):**

| Problema en la fuente | Tratamiento |
|---|---|
| 2 filas duplicadas | `drop_duplicates()` |
| `id_producto` como texto, con espacios (`" 103 "`) o vacío | `str.strip()` y luego `pd.to_numeric(..., errors="coerce")` → `int64` |
| `fecha` como texto, vacía o inválida (`"fecha_invalida"`) | `pd.to_datetime(..., format="%Y-%m-%d", errors="coerce")` → `datetime64` |
| Nulos en `id_producto`, `cantidad` o `fecha` (8 filas) | **Se eliminan.** Son el hecho registrado en sí; imputarlos sería inventar ventas. |
| `cantidad` ≤ 0 (2 filas) | Se eliminan porque no son ventas válidas |

**Productos (Excel):**

| Problema en la fuente | Tratamiento |
|---|---|
| `id_producto` guardado como **texto** en el Excel | Se convierte a `int64`, el mismo tipo que en las transacciones |
| Producto repetido (ID 103) | `drop_duplicates(subset="id_producto")`, para no duplicar ventas en el merge |
| `precio_unitario` nulo (ID 106) | **Se imputa** con la mediana de precios de su categoría |
| `nombre_producto` nulo (ID 109) | **Se imputa** con `"Producto 109 (sin nombre)"` |

En el maestro sí conviene imputar: el producto existe y tiene ventas
asociadas que se perderían si se eliminara la fila.

### 3. Merge

- Antes del merge, un `assert` comprueba que `id_producto` tenga **el mismo
  tipo** en ambas tablas (`int64`). Así se evita el error clásico de unir un
  ID string con un ID entero.
- `merge(how="left", validate="many_to_one", indicator=True)`:
  - `validate` garantiza que cada transacción matchee como máximo un producto.
  - `indicator` permite detectar transacciones de productos que no existen
    en el catálogo (ID 999). Se informan por consola y se descartan.

### 4. Normalización

Se agrega la columna calculada `total_venta = cantidad * precio_unitario`.

Antes de exportar se valida que:

- no haya nulos en los campos críticos (`id_transaccion`, `id_producto`,
  `nombre_producto`, `cantidad`, `precio_unitario`, `fecha`, `total_venta`);
- `fecha` sea de tipo datetime;
- `id_transaccion` sea único;
- todos los `total_venta` sean mayores a 0.

### 5. Exportación

`to_parquet(engine="pyarrow")` genera `output/ventas_consolidadas.parquet`.
Después el script lo vuelve a leer y comprueba con
`pd.testing.assert_frame_equal` que conserve los datos y los tipos
(datetime, category, int, float).

## Dataset final

189 transacciones válidas (de 202 filas originales) × 8 columnas:

| Columna | Tipo |
|---|---|
| `id_transaccion` | int64 |
| `fecha` | datetime64 |
| `id_producto` | int64 |
| `nombre_producto` | string |
| `categoria` | category |
| `cantidad` | int64 |
| `precio_unitario` | float64 |
| `total_venta` | float64 (calculada) |

## Checklist de la consigna

1. **Código funcional sin errores**: `python adquisicion_normalizacion.py`
   corre de punta a punta y termina con validaciones en verde.
2. **Merge entre dos fuentes de distinto formato**: CSV (transacciones) +
   XLSX (productos), unidos por `id_producto` con el mismo tipo en ambos.
3. **Columna calculada y sin nulos en campos críticos**: `total_venta`,
   y las validaciones con `assert` lo garantizan.
4. **README con pasos y librerías**: este archivo.
5. **Archivo de salida en Parquet**: `output/ventas_consolidadas.parquet`.

## Errores comunes evitados

- **Motor de Excel sin cerrar**: la lectura se hace dentro de un
  `with pd.ExcelFile(...)`, y `openpyxl` figura en `requirements.txt`.
- **Merge con tipos distintos**: el ID del Excel viene como texto y se
  convierte a `int64` antes del merge. Un `assert` lo verifica.
- **README faltante**: incluido.
