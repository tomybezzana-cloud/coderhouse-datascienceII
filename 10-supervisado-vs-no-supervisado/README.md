# Práctica 10: Aprendizaje supervisado y no supervisado: el arte de elegir

Diagnóstico de 4 casos de clientes para decidir, antes de elegir un
algoritmo, qué tipo de problema de Machine Learning es cada uno.

Archivos:

- [`Analisis_Problemas_ML_TomasBezzana.pdf`](Analisis_Problemas_ML_TomasBezzana.pdf): el entregable.
- [`generar_pdf.py`](generar_pdf.py): genera el PDF con `reportlab` (`pip install reportlab`, luego `python generar_pdf.py`). Usa la fuente Arial de Windows.

## Criterio de decisión

1. **¿Los datos históricos tienen una respuesta conocida (etiqueta *Y*)?**
   Si no, el aprendizaje es **no supervisado** (por ejemplo, clustering). Si sí,
   es **supervisado**.
2. **Si es supervisado, ¿qué es *Y*?** Si es una **categoría**, es
   **clasificación**. Si es un **número continuo**, es **regresión**.

## Resumen

| Caso | Tipo | Tarea | Variable objetivo (*Y*) | Palabra clave |
|---|---|---|---|---|
| A · App de música | No supervisado | Clustering | **No existe**: las listas temáticas todavía no existen, el algoritmo descubre los grupos | "agrupar", "nuevas listas" |
| B · Banco | Supervisado | Clasificación binaria | Paga / No paga | "no pague", "historial" |
| C · Logística | Supervisado | Regresión | Tiempo de llegada en minutos (continuo) | "tiempo exacto (en minutos)" |
| D · Hospital | Supervisado | Clasificación binaria | Diabetes / Sano | "fueron diagnosticados con diabetes o sanos" |

El PDF desarrolla, para cada caso, las 4 dimensiones pedidas: tipo de
aprendizaje, tarea, variables (*Y* y al menos dos *X*) y justificación.

## Las dos trampas de la consigna

- **Caso A:** no tiene variable objetivo. En aprendizaje no supervisado no
  hay etiquetas previas; el nombre de cada playlist se pone *después* de ver
  qué canciones quedaron agrupadas.
- **Caso B:** que diga "probabilidad" no lo convierte en regresión. El
  modelo estima la probabilidad de pertenecer a la clase "no paga" y un
  umbral decide la categoría final. Por eso la regresión logística, a pesar
  del nombre, es un algoritmo de clasificación.
