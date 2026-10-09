"""
Pre-entrega: Ciclo de vida de un proyecto de Machine Learning.

Genera Propuesta_ML_Cancelaciones_Hoteleras_TomasBezzana.pdf: propuesta técnica
(máximo 2 páginas) para predecir cancelaciones de reservas hoteleras con el
dataset "Hotel Booking Demand" de Kaggle.

Las cifras del documento (filas, columnas, tasa de cancelación, rangos) se
obtuvieron explorando el CSV original con pandas.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE_DIR = Path(__file__).resolve().parent
RUTA_PDF = BASE_DIR / "Propuesta_ML_Cancelaciones_Hoteleras_TomasBezzana.pdf"

AUTOR = "Tomás Bezzana"
URL_KAGGLE = "https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand"
URL_PAPER = "https://doi.org/10.1016/j.dib.2018.11.126"

FUENTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Calibri", FUENTES / "calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold", FUENTES / "calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Italic", FUENTES / "calibrii.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", FUENTES / "calibriz.ttf"))
pdfmetrics.registerFontFamily("Calibri", normal="Calibri", bold="Calibri-Bold",
                              italic="Calibri-Italic", boldItalic="Calibri-BoldItalic")

NEGRO = colors.HexColor("#222222")
TITULOS = colors.HexColor("#2f5496")  # el azul de los títulos por defecto de Word
GRIS_TABLA = colors.HexColor("#d9d9d9")
BORDE = colors.HexColor("#999999")

E = {
    "titulo": ParagraphStyle("titulo", fontName="Calibri-Bold", fontSize=17, leading=21,
                             textColor=TITULOS, spaceAfter=2),
    "autor": ParagraphStyle("autor", fontName="Calibri", fontSize=11, leading=14,
                            textColor=NEGRO, spaceAfter=8),
    "h1": ParagraphStyle("h1", fontName="Calibri-Bold", fontSize=13, leading=16,
                         textColor=TITULOS, spaceBefore=8, spaceAfter=3),
    "cuerpo": ParagraphStyle("cuerpo", fontName="Calibri", fontSize=10.5, leading=13.3,
                             textColor=NEGRO, spaceAfter=5),
    "celda": ParagraphStyle("celda", fontName="Calibri", fontSize=9.8, leading=12,
                            textColor=NEGRO),
    "celda_b": ParagraphStyle("celda_b", fontName="Calibri-Bold", fontSize=9.8, leading=12,
                              textColor=NEGRO),
}


def p(texto, estilo="cuerpo"):
    return Paragraph(texto, E[estilo])


def link(url):
    return f"<link href='{url}' color='#0563c1'><u>{url}</u></link>"


# Diccionario de datos: (variable, tipo, descripción, valores)
DICCIONARIO = [
    ("is_canceled", "Categórica (binaria)",
     "Variable objetivo. Indica si la reserva se canceló.",
     "1 = cancelada, 0 = no cancelada. El 37% son 1."),
    ("lead_time", "Numérica (entera)",
     "Días que pasaron entre que se hizo la reserva y la fecha de llegada.",
     "De 0 a 737 días, la mitad está por debajo de 69."),
    ("hotel", "Categórica",
     "En cuál de los dos hoteles es la reserva.",
     "City Hotel o Resort Hotel."),
    ("arrival_date_month", "Ordinal",
     "Mes de llegada. Sirve para ver si hay épocas del año con más cancelaciones.",
     "De January a December."),
    ("deposit_type", "Categórica",
     "Si el cliente dejó depósito y de qué tipo.",
     "No Deposit, Non Refund o Refundable."),
    ("previous_cancellations", "Numérica (entera)",
     "Cuántas reservas había cancelado antes el mismo cliente.",
     "De 0 a 26."),
    ("market_segment", "Categórica",
     "Por dónde llegó la reserva.",
     "Agencia online, agencia tradicional, grupos, directo, empresas, etc."),
    ("adr", "Numérica (decimal)",
     "Precio promedio por noche, en euros.",
     "La mediana es de 94,6 euros."),
    ("total_of_special_requests", "Numérica (entera)",
     "Cantidad de pedidos especiales que hizo el cliente (tipo de cama, piso, etc.).",
     "De 0 a 5."),
]


def tabla_diccionario():
    filas = [[p(t, "celda_b") for t in ("Variable", "Tipo", "Descripción", "Valores")]]
    for var, tipo, desc, valores in DICCIONARIO:
        filas.append([p(var, "celda"), p(tipo, "celda"), p(desc, "celda"), p(valores, "celda")])
    ancho = A4[0] - 4.0 * cm
    t = Table(filas, colWidths=[4.0 * cm, 2.9 * cm, ancho - 11.5 * cm, 4.6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRIS_TABLA),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Calibri", 10)
    canvas.setFillColor(NEGRO)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, str(doc.page))
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        str(RUTA_PDF), pagesize=A4,
        leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
        title="Propuesta de proyecto - Cancelaciones de reservas de hotel", author=AUTOR,
    )

    story = [
        p("Predicción de cancelaciones en reservas de hotel", "titulo"),
        p(f"{AUTOR} - Data Science II (Coderhouse) - Pre-entrega", "autor"),

        p("1. El problema", "h1"),
        p("Cuando un huésped cancela una reserva cerca de la fecha, el hotel se queda con una "
          "habitación vacía que muchas veces ya no llega a vender. Para cubrirse, muchos hoteles "
          "hacen overbooking o le piden depósito a todos por igual, pero las dos cosas tienen su "
          "costo: si calculan mal pueden quedarse sin lugar para un huésped, y pedirle depósito a "
          "todo el mundo hace que algunos clientes terminen reservando en otro lado. En los datos "
          "que elegí, el 37% de las reservas terminaron canceladas, así que el problema no es "
          "menor."),

        p("2. Objetivo y tipo de aprendizaje", "h1"),
        p("Lo que quiero predecir es si una reserva se va a cancelar o no, usando la información "
          "que se tiene en el momento en que se hace. La variable objetivo es <i>is_canceled</i>, "
          "que vale 1 si la reserva se canceló y 0 si no."),
        p("Es un problema de aprendizaje supervisado, porque en los datos históricos ya se sabe "
          "qué reservas se cancelaron y cuáles no, y el modelo puede aprender de esos ejemplos. "
          "Dentro del aprendizaje supervisado es una clasificación binaria, ya que la respuesta "
          "es sí o no y no un valor numérico."),
        p("Mi hipótesis es que las reservas hechas con mucha anticipación, sin depósito o de "
          "clientes que ya cancelaron alguna vez tienen más chances de cancelarse que las que se "
          "hacen pocos días antes o con depósito."),
        p("Me parece que tiene sentido usar Machine Learning porque la cancelación depende de "
          "varias cosas a la vez (la anticipación, el canal por el que se reservó, la época del "
          "año, el precio) y eso es difícil de resolver con un par de reglas armadas a mano. "
          "Además hay muchos ejemplos para entrenar. Si el modelo funciona, el hotel podría pedir "
          "depósito solo a las reservas con más riesgo o ajustar mejor el overbooking. Como "
          "referencia, un modelo que diga siempre \"no cancela\" ya acertaría el 63% de las "
          "veces, así que el modelo tiene que superar bien ese número para que valga la pena."),

        p("3. Fuente de datos", "h1"),
        p(f"Voy a usar el dataset Hotel Booking Demand, que está publicado en Kaggle:<br/>"
          f"{link(URL_KAGGLE)}"),
        p(f"Los datos vienen de un artículo de Antonio, de Almeida y Nunes publicado en 2019 en la "
          f"revista Data in Brief ({link(URL_PAPER)}). Son reservas reales de dos hoteles de "
          f"Portugal, un hotel de ciudad en Lisboa y un resort en el Algarve, con fechas de llegada "
          f"entre julio de 2015 y agosto de 2017. En total son 119.390 reservas y 32 columnas, en "
          f"un solo archivo CSV (hotel_bookings.csv) de unos 17 MB. Los datos de los clientes "
          f"vienen anonimizados."),

        KeepTogether([
            p("4. Diccionario de datos", "h1"),
            p("De las 32 columnas elegí estas 9 para arrancar. Todas son datos que el hotel ya "
              "tiene cuando se hace la reserva."),
            tabla_diccionario(),
        ]),
        Spacer(1, 6),
        p("Revisando el archivo encontré algunos datos faltantes: la columna <i>company</i> está "
          "vacía en casi todas las filas (94%), <i>agent</i> en un 14%, y <i>country</i> y "
          "<i>children</i> tienen unos pocos nulos. También hay valores raros en <i>adr</i>, como "
          "una tarifa negativa y otra de 5.400 euros, que voy a tener que revisar cuando limpie "
          "los datos."),

        p("5. Por qué elegí estos datos", "h1"),
        p("Elegí este dataset porque ya trae la columna de cancelación, que es justo lo que quiero "
          "predecir, y además tiene información que el hotel conoce al momento de la reserva. Son "
          "datos reales y hay suficientes reservas como para separar una parte para entrenar y "
          "otra para probar el modelo, dejando las fechas más recientes para la prueba."),
        p("Hay dos columnas que no voy a usar: <i>reservation_status</i> y "
          "<i>reservation_status_date</i>. Las dos indican cómo terminó la reserva (por ejemplo "
          "\"Canceled\"), así que incluirlas sería darle la respuesta al modelo. También voy a "
          "revisar <i>assigned_room_type</i> y <i>booking_changes</i>, porque pueden cambiar "
          "después de que se hizo la reserva."),
        p("Como limitación, son solo dos hoteles de Portugal y los datos son de antes de la "
          "pandemia, así que los resultados no se podrían aplicar directamente a otros hoteles "
          "sin probarlos antes con sus propios datos."),

        p("6. Formato del archivo", "h1"),
        p("El archivo viene en CSV y me parece el formato adecuado para este tamaño. Son unos "
          "17 MB, que se cargan sin problema con pandas en cualquier computadora, y como los datos "
          "son una tabla simple con una fila por reserva, no hace falta nada más complejo. Un JSON "
          "ocuparía más espacio porque repite el nombre de cada columna en todos los registros, y "
          "no suma nada porque los datos no tienen estructura anidada. Una base de datos SQL "
          "tendría sentido si el proyecto pasara a producción y los datos llegaran directamente "
          "del sistema de reservas del hotel, con mucho más volumen. Una vez que limpie los datos, "
          "pienso guardar la versión final en Parquet, que ocupa menos y mantiene los tipos de "
          "cada columna."),
    ]

    doc.build(story, onFirstPage=pie, onLaterPages=pie)
    print(f"Generado: {RUTA_PDF.name}")


if __name__ == "__main__":
    main()
