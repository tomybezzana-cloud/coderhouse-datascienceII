# Práctica 13: Procesamiento Vectorial para Datos de ML

Ejercicios de razonamiento y cálculo manual para pasar datos del mundo real
a vectores y hacer a mano las operaciones que un modelo de Machine Learning
hace "detrás de escena".

Archivos:

- [`Representacion_Vectorial_Bezzana_Tomas.pdf`](Representacion_Vectorial_Bezzana_Tomas.pdf): el entregable.
- [`generar_pdf.py`](generar_pdf.py): genera el PDF con `reportlab` (`pip install reportlab`, luego `python generar_pdf.py`). Usa las fuentes Arial y Consolas de Windows.

## Resultados

**Tarea 1: usuarios como vectores** `U = [Rock, Pop, Jazz]`

| Usuario | Vector |
|---|---|
| A | `[10, 2, 0]` |
| B | `[1, 12, 1]` |
| C | `[8, 3, 1]` |

**Tarea 2: operaciones**

| Operación | Cuenta | Resultado |
|---|---|---|
| Suma A + C | `[10+8, 2+3, 0+1]` | `[18, 5, 1]` |
| Escalado 2 · B | `[2·1, 2·12, 2·1]` | `[2, 24, 2]` |
| Producto punto A · C | `10·8 + 2·3 + 0·1` | `86` |

Como referencia, el PDF compara también A · B = 34 y B · C = 45, y suma la
similitud coseno (A · C ≈ 0,98), que no depende de cuántas horas escucha cada
usuario.

**Tarea 3: Bag of Words**

Vocabulario: `[Amo, el, café, Odio, té]`

| Frase | Vector |
|---|---|
| "Amo el café" | `[1, 1, 1, 0, 0]` |
| "Odio el café" | `[0, 1, 1, 1, 0]` |
| "Amo el té" | `[1, 1, 0, 0, 1]` |

## La trampa de la Tarea 3

La consigna da por hecho que la frase 1 se parece más numéricamente a la 3
que a la 2. **Con vectores de presencia no es así: empatan.** F1 · F2 = 2 y
F1 · F3 = 2, y lo mismo pasa con la distancia euclidiana (√2) y la similitud
coseno (2/3). Cada par comparte 2 palabras.

La 1 y la 3 *parecen* más parecidas porque una persona lee el significado
("Amo" vs. "Odio" da vuelta la frase; "café" vs. "té" es un detalle). Bag of
Words le da el mismo peso a todas las palabras y no lo ve. El PDF explica
esa limitación y cómo se resuelve (pesos de sentimiento o embeddings).

## Tarea 4

Las funciones vectorizadas (NumPy, Polars) son más rápidas que un `for`
porque evitan el costo del intérprete en cada fila: procesan la columna
entera en código compilado, con memoria contigua, SIMD y, en Polars,
paralelismo entre núcleos.
