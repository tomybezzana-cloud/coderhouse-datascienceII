"""
Aprendizaje Supervisado y No Supervisado: el arte de elegir.

Genera Analisis_Problemas_ML_TomasBezzana.pdf con el análisis técnico de los
4 casos de clientes: tipo de aprendizaje, tarea de ML, variables (Y y X) y
justificación.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_PDF = BASE_DIR / "Analisis_Problemas_ML_TomasBezzana.pdf"

AUTOR = "Tomás Bezzana"
FECHA = "2 de octubre de 2026"

# Arial (incluida en Windows) para que los acentos y la ñ se vean bien
FUENTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", FUENTES / "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FUENTES / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FUENTES / "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", FUENTES / "arialbi.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")

AZUL = colors.HexColor("#2e4a7d")
GRIS_TEXTO = colors.HexColor("#1b2733")
GRIS_SUAVE = colors.HexColor("#5a6b7a")
FONDO_ETIQUETA = colors.HexColor("#eef3f9")
BORDE = colors.HexColor("#c5d1e0")
COLOR_SUPERVISADO = colors.HexColor("#1e8449")
COLOR_NO_SUPERVISADO = colors.HexColor("#7d3c98")

ESTILOS = {
    "titulo": ParagraphStyle("titulo", fontName="Arial-Bold", fontSize=19, leading=23,
                             textColor=AZUL, spaceAfter=4),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Arial", fontSize=10.5, leading=14,
                                textColor=GRIS_SUAVE, spaceAfter=14),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=13.5, leading=17,
                         textColor=AZUL, spaceBefore=10, spaceAfter=6),
    "cuerpo": ParagraphStyle("cuerpo", fontName="Arial", fontSize=10, leading=14,
                             textColor=GRIS_TEXTO, spaceAfter=6),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=9.5, leading=13,
                            textColor=GRIS_TEXTO),
    "celda_centro": ParagraphStyle("celda_centro", fontName="Arial", fontSize=9.5, leading=13,
                                   textColor=GRIS_TEXTO, alignment=TA_CENTER),
    "etiqueta": ParagraphStyle("etiqueta", fontName="Arial-Bold", fontSize=9.5, leading=13,
                               textColor=AZUL),
    "encabezado": ParagraphStyle("encabezado", fontName="Arial-Bold", fontSize=11.5, leading=15,
                                 textColor=colors.white),
    "encabezado_tabla": ParagraphStyle("encabezado_tabla", fontName="Arial-Bold", fontSize=9.5,
                                       leading=13, textColor=colors.white, alignment=TA_CENTER),
    "escenario": ParagraphStyle("escenario", fontName="Arial-Italic", fontSize=9.5, leading=13,
                                textColor=GRIS_SUAVE),
}

# ---------------------------------------------------------------------------
# Contenido del análisis
# ---------------------------------------------------------------------------
CASOS = [
    {
        "letra": "A",
        "cliente": "App de música",
        "escenario": (
            "Una app de música quiere agrupar canciones de su catálogo basándose en el ritmo y "
            "los instrumentos utilizados, para crear nuevas listas de reproducción temáticas "
            "automáticas."
        ),
        "supervisado": False,
        "tipo": "<b>No supervisado.</b> Solo se cuenta con las características de cada canción; "
                "no hay una respuesta correcta conocida de antemano para aprender de ella.",
        "tarea": "<b>Clustering</b> (agrupamiento). Por ejemplo, con K-Means o un clustering "
                 "jerárquico sobre las características de audio.",
        "y": "<b>No existe.</b> Las listas temáticas todavía no existen: nadie etiquetó a qué "
             "playlist pertenece cada canción. Son los grupos los que el algoritmo tiene que "
             "<i>descubrir</i> según la similitud entre canciones. El nombre de cada lista "
             "(\"para entrenar\", \"acústico tranquilo\") se pone <i>después</i>, al mirar qué "
             "canciones quedaron juntas.",
        "x": [
            "Tempo o ritmo en BPM (pulsos por minuto).",
            "Instrumentos presentes: guitarra, piano, sintetizador, batería, etc.",
            "Energía, tonalidad (mayor / menor) y si es acústica o electrónica.",
        ],
        "justificacion": "La palabra clave es <b>\"agrupar\"</b>, reforzada por <b>\"nuevas\"</b> "
                         "listas. No se pide predecir una etiqueta ya conocida, sino encontrar "
                         "estructura en datos que no tienen etiqueta. Eso es, por definición, "
                         "aprendizaje no supervisado de tipo clustering.",
    },
    {
        "letra": "B",
        "cliente": "Banco",
        "escenario": (
            "Un banco quiere predecir la probabilidad de que un cliente no pague su préstamo, "
            "basándose en su historial crediticio de los últimos 5 años."
        ),
        "supervisado": True,
        "tipo": "<b>Supervisado.</b> El historial de 5 años incluye préstamos ya terminados, "
                "donde se sabe si el cliente pagó o no: son ejemplos con la respuesta conocida.",
        "tarea": "<b>Clasificación binaria.</b> Por ejemplo, con regresión logística o random "
                 "forest.",
        "y": "<b>Incumplimiento del préstamo: Paga (0) / No paga (1).</b> Es un estado con dos "
             "categorías posibles, no un número continuo.",
        "x": [
            "Cantidad de pagos atrasados en los últimos 5 años.",
            "Ingresos mensuales y relación deuda / ingreso.",
            "Monto y plazo del préstamo solicitado.",
            "Puntaje crediticio y antigüedad laboral.",
        ],
        "justificacion": "La pista definitiva es <b>\"no pague\"</b>: el banco busca un estado "
                         "(paga / no paga). <b>\"Historial\"</b> confirma que hay casos pasados "
                         "etiquetados. Aunque se hable de <b>\"probabilidad\"</b>, no es regresión: "
                         "el modelo estima la probabilidad de pertenecer a la clase \"no paga\" y "
                         "con un umbral decide la categoría final (aprobar o rechazar). Por eso la "
                         "regresión logística, a pesar del nombre, es un algoritmo de clasificación.",
    },
    {
        "letra": "C",
        "cliente": "Empresa de logística",
        "escenario": (
            "Una empresa de logística quiere estimar el tiempo exacto de llegada (en minutos) de "
            "sus camiones de reparto considerando el tráfico y la distancia."
        ),
        "supervisado": True,
        "tipo": "<b>Supervisado.</b> De cada viaje histórico se registró cuánto tardó en realidad, "
                "así que los datos ya tienen la respuesta.",
        "tarea": "<b>Regresión.</b> Por ejemplo, con regresión lineal o gradient boosting.",
        "y": "<b>Tiempo de llegada en minutos.</b> Es un valor numérico continuo: puede ser "
             "37, 42,5 o 118 minutos.",
        "x": [
            "Distancia del recorrido (km).",
            "Nivel de tráfico en la ruta.",
            "Hora del día y día de la semana.",
            "Cantidad de paradas, clima y tipo de camión.",
        ],
        "justificacion": "La pista definitiva es <b>\"tiempo exacto (en minutos)\"</b>. Es regresión "
                         "porque el tiempo es un valor <b>continuo</b>: no hay un conjunto cerrado de "
                         "categorías, cualquier cantidad de minutos es posible. El verbo "
                         "<b>\"estimar\"</b> una cantidad lo confirma.",
    },
    {
        "letra": "D",
        "cliente": "Hospital",
        "escenario": (
            "Un hospital tiene miles de registros clínicos de pacientes antiguos que fueron "
            "diagnosticados con diabetes o sanos; quieren un sistema que ayude a los médicos a "
            "identificar nuevos pacientes en riesgo."
        ),
        "supervisado": True,
        "tipo": "<b>Supervisado.</b> Cada registro antiguo ya tiene su diagnóstico confirmado por "
                "un médico, que funciona como etiqueta.",
        "tarea": "<b>Clasificación binaria.</b> Por ejemplo, con regresión logística o árbol de "
                 "decisión, que además son fáciles de explicar a un médico.",
        "y": "<b>Diagnóstico: Diabetes / Sano.</b> Dos categorías posibles.",
        "x": [
            "Glucosa en ayunas y hemoglobina glicosilada (HbA1c).",
            "Índice de masa corporal (IMC) y edad.",
            "Presión arterial y antecedentes familiares de diabetes.",
        ],
        "justificacion": "La pista definitiva es <b>\"fueron diagnosticados con diabetes o "
                         "sanos\"</b>: los datos históricos ya vienen etiquetados con dos clases. "
                         "Se quiere aprender ese patrón para <b>\"identificar nuevos pacientes\"</b>, "
                         "o sea asignarles una de esas categorías. Como es un apoyo al médico, "
                         "conviene priorizar no dejar pasar pacientes enfermos (alto recall).",
    },
]


# ---------------------------------------------------------------------------
# Armado del documento
# ---------------------------------------------------------------------------
ANCHO_UTIL = A4[0] - 4 * cm


def tabla_resumen():
    e = ESTILOS
    filas = [[Paragraph(t, e["encabezado_tabla"]) for t in
              ("Caso", "Tipo de aprendizaje", "Tarea de ML", "Variable objetivo (<i>Y</i>)")]]
    for c in CASOS:
        tipo = "Supervisado" if c["supervisado"] else "No supervisado"
        color = COLOR_SUPERVISADO if c["supervisado"] else COLOR_NO_SUPERVISADO
        tarea = c["tarea"].split("</b>")[0].replace("<b>", "").rstrip(".")
        y = c["y"].split("</b>")[0].replace("<b>", "").rstrip(".")
        filas.append([
            Paragraph(f"<b>{c['letra']}</b> · {c['cliente']}", e["celda"]),
            Paragraph(f"<font color='{color.hexval()}'><b>{tipo}</b></font>", e["celda_centro"]),
            Paragraph(tarea, e["celda_centro"]),
            Paragraph(y, e["celda"]),
        ])
    t = Table(filas, colWidths=[3.6 * cm, 3.4 * cm, 3.4 * cm, ANCHO_UTIL - 10.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_ETIQUETA]),
        ("GRID", (0, 0), (-1, -1), 0.6, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def bloque_caso(c):
    e = ESTILOS
    color = COLOR_SUPERVISADO if c["supervisado"] else COLOR_NO_SUPERVISADO
    lista_x = "<br/>".join(f"• {x}" for x in c["x"])
    filas = [
        [Paragraph(f"Caso {c['letra']}: {c['cliente']}", e["encabezado"]), ""],
        [Paragraph(f"\"{c['escenario']}\"", e["escenario"]), ""],
        [Paragraph("1. Tipo de aprendizaje", e["etiqueta"]), Paragraph(c["tipo"], e["celda"])],
        [Paragraph("2. Tarea de ML", e["etiqueta"]), Paragraph(c["tarea"], e["celda"])],
        [Paragraph("3. Variables", e["etiqueta"]),
         Paragraph(f"<b>Variable objetivo (<i>Y</i>):</b> {c['y']}<br/><br/>"
                   f"<b>Características (<i>X</i>):</b><br/>{lista_x}", e["celda"])],
        [Paragraph("4. Justificación", e["etiqueta"]), Paragraph(c["justificacion"], e["celda"])],
    ]
    t = Table(filas, colWidths=[3.6 * cm, ANCHO_UTIL - 3.6 * cm])
    t.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("SPAN", (0, 1), (-1, 1)),
        ("BACKGROUND", (0, 0), (-1, 0), color),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f7f9fb")),
        ("BACKGROUND", (0, 2), (0, -1), FONDO_ETIQUETA),
        ("BOX", (0, 0), (-1, -1), 1, color),
        ("LINEBELOW", (0, 1), (-1, -2), 0.6, BORDE),
        ("LINEAFTER", (0, 2), (0, -1), 0.6, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 14)])


def pie_de_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8.5)
    canvas.setFillColor(GRIS_SUAVE)
    canvas.drawString(2 * cm, 1.2 * cm, f"Análisis de problemas de ML · {AUTOR}")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main():
    e = ESTILOS
    doc = SimpleDocTemplate(
        str(RUTA_PDF), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
        title="Análisis de Problemas de ML", author=AUTOR,
        subject="Aprendizaje supervisado y no supervisado: el arte de elegir",
    )

    story = [
        Paragraph("Análisis de Problemas de Machine Learning", e["titulo"]),
        Paragraph(f"Aprendizaje supervisado y no supervisado: el arte de elegir<br/>"
                  f"{AUTOR} · Data Science II (Coderhouse) · {FECHA}", e["subtitulo"]),
        Paragraph("Criterio de decisión", e["h1"]),
        Paragraph(
            "Antes de elegir un algoritmo hay que diagnosticar el problema con dos preguntas, en "
            "este orden:", e["cuerpo"]),
        Paragraph(
            "<b>1. ¿Los datos históricos tienen una respuesta conocida (etiqueta <i>Y</i>)?</b> "
            "Si no la tienen, el aprendizaje es <b>no supervisado</b>: el objetivo es descubrir "
            "estructura, por ejemplo grupos (<b>clustering</b>). Si la tienen, es "
            "<b>supervisado</b>.", e["cuerpo"]),
        Paragraph(
            "<b>2. Si es supervisado, ¿qué naturaleza tiene <i>Y</i>?</b> Si es una "
            "<b>categoría</b> (sí / no, sano / enfermo), es <b>clasificación</b>. Si es un "
            "<b>número continuo</b> (minutos, pesos, kilos), es <b>regresión</b>.", e["cuerpo"]),
        Paragraph("Resumen de los 4 casos", e["h1"]),
        tabla_resumen(),
        Spacer(1, 6),
    ]
    bloques = [bloque_caso(c) for c in CASOS]
    # El título va pegado al primer caso para que no quede huérfano al pie de página
    story.append(KeepTogether([Paragraph("Análisis detallado por caso", e["h1"]), bloques[0]]))
    story += bloques[1:]

    doc.build(story, onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
    print(f"Generado: {RUTA_PDF.name}")


if __name__ == "__main__":
    main()
