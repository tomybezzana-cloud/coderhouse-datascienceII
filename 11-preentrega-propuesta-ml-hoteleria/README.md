# Práctica 11 (Pre-entrega 3): Propuesta de proyecto de ML: cancelaciones hoteleras

Propuesta técnica (máximo 2 páginas) para la fase inicial del ciclo de vida
de un proyecto de Machine Learning: definición del problema, fuente de datos
real, diccionario de variables y justificación del formato.

Archivos:

- [`Propuesta_ML_Cancelaciones_Hoteleras_TomasBezzana.pdf`](Propuesta_ML_Cancelaciones_Hoteleras_TomasBezzana.pdf): el entregable (2 páginas).
- [`generar_pdf.py`](generar_pdf.py): genera el PDF con `reportlab` (`python generar_pdf.py`).

## Resumen de la propuesta

| Aspecto | Definición |
|---|---|
| Problema | Las cancelaciones dejan habitaciones vacías que ya no se pueden vender. En el dataset, el 37% de las reservas se cancela. |
| Objetivo | Predecir, al momento de reservar, si la reserva va a ser cancelada |
| Target | `is_canceled` (1 = cancelada, 0 = no) |
| Tipo de ML | **Supervisado, clasificación binaria** |
| Dataset | [Hotel Booking Demand (Kaggle)](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand): 119.390 reservas × 32 variables, dos hoteles de Portugal, julio 2015 a agosto 2017 |
| Origen académico | Antonio, de Almeida y Nunes (2019), *Data in Brief* 22: [doi.org/10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126) |
| Diccionario | 9 variables: el target y 8 features (numéricas discretas y continuas, categóricas nominales y una ordinal) |
| Formato | CSV de ~17 MB: el formato óptimo para este volumen. Después de limpiar, se guarda en Parquet |

Las cifras del documento (tasa de cancelación, rangos, nulos) salen de
explorar el CSV con pandas. El enlace de Kaggle se verificó (responde HTTP 200).

## Checklist de la consigna

1. **Problema y tipo de ML identificados:** predicción de cancelaciones, aprendizaje supervisado (clasificación binaria).
2. **Enlace funcional a un dataset real:** Kaggle, con la cita del paper original.
3. **Diccionario con al menos 5 variables, con nombre y tipo:** incluye 9.
4. **Adquisición coherente con el objetivo:** el dataset trae el target etiquetado y variables conocidas al reservar, y se excluyen las que filtran el desenlace (`reservation_status`).
5. **Formato PDF:** sí, en 2 páginas.
