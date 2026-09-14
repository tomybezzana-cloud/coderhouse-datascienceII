"""
Práctica de repaso de Python básico - Data Science II
Objetivo: reforzar variables, tipos de datos, estructuras de control,
listas, diccionarios y funciones antes de usar librerías como Pandas.
"""

# ---------------------------------------------------------------
# Tarea 1: Definición de Variables
# ---------------------------------------------------------------
# Cada variable tiene un tipo de dato distinto: str, float, int y bool.
producto_nombre = "Auriculares Bluetooth"
producto_precio = 45.99
producto_stock = 120
producto_tiene_descuento = True

# f-string: permite insertar variables directamente dentro del texto
# usando llaves {}, sin tener que concatenar strings con +.
print(
    f"El producto '{producto_nombre}' cuesta ${producto_precio}, "
    f"hay {producto_stock} unidades en stock y "
    f"{'sí tiene' if producto_tiene_descuento else 'no tiene'} descuento disponible."
)

print("-" * 60)

# ---------------------------------------------------------------
# Tarea 2: Lógica de Negocio (Bucle + Condicional)
# ---------------------------------------------------------------
# Lista con al menos 5 precios de ejemplo.
precios = [50.0, 120.5, 99.99, 200.0, 75.25]

# Recorremos la lista con un for y clasificamos cada precio.
for precio in precios:
    if precio > 100:
        categoria = "Caro"
    else:
        categoria = "Económico"
    print(f"Precio ${precio} -> {categoria}")

print("-" * 60)

# ---------------------------------------------------------------
# Tarea 3: Estructura de Datos Compleja (Diccionario)
# ---------------------------------------------------------------
# Diccionario "almacen": clave = nombre del producto, valor = stock.
almacen = {
    "Auriculares Bluetooth": 120,
    "Teclado mecánico": 45,
    "Mouse inalámbrico": 80,
}

# Agregamos un nuevo producto al diccionario.
almacen["Monitor 24 pulgadas"] = 30

# Consultamos el stock de un producto específico.
producto_a_consultar = "Teclado mecánico"
print(f"Stock de '{producto_a_consultar}': {almacen[producto_a_consultar]} unidades")
print(f"Almacén completo: {almacen}")

print("-" * 60)

# ---------------------------------------------------------------
# Tarea 4: Modularización con Funciones
# ---------------------------------------------------------------
def resumen_estadistico(numeros):
    """Recibe una lista de números y devuelve un diccionario con
    la suma total, el promedio y la cantidad de elementos."""
    suma_total = sum(numeros)
    cantidad_elementos = len(numeros)
    promedio = suma_total / cantidad_elementos

    return {
        "suma_total": suma_total,
        "promedio": promedio,
        "cantidad_elementos": cantidad_elementos,
    }


ventas_ejemplo = [150, 200, 99.99, 300, 45.5]
resultado = resumen_estadistico(ventas_ejemplo)
print(f"Resumen estadístico de {ventas_ejemplo}:")
print(resultado)
