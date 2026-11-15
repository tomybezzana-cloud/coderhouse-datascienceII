"""
Ejecución eficiente de queries analíticas.

Genera Optimizacion_Queries_Analiticas_Bezzana_Tomas.pdf a partir de
optimizacion_queries.md, así el PDF y el .md siempre tienen el mismo
contenido. Interpreta solo lo que usa ese archivo: títulos (#, ##, ###), párrafos,
bloques ```sql, tablas, citas (>), listas (-), separadores (---) y, dentro
del texto, **negrita**, `código` y [enlaces](...).
"""

import re
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_MD = BASE_DIR / "optimizacion_queries.md"
RUTA_PDF = BASE_DIR / "Optimizacion_Queries_Analiticas_Bezzana_Tomas.pdf"

AUTOR = "Tomás Bezzana"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Arial (incluida en Windows) para que los acentos y la ñ se vean bien
FUENTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", FUENTES / "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FUENTES / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FUENTES / "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", FUENTES / "arialbi.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")
# Consolas para el SQL, así la indentación queda alineada
pdfmetrics.registerFont(TTFont("Consolas", FUENTES / "consola.ttf"))
pdfmetrics.registerFont(TTFont("Consolas-Bold", FUENTES / "consolab.ttf"))
pdfmetrics.registerFontFamily("Consolas", normal="Consolas", bold="Consolas-Bold",
                              italic="Consolas", boldItalic="Consolas-Bold")

AZUL = colors.HexColor("#2e4a7d")
GRIS_TEXTO = colors.HexColor("#1b2733")
GRIS_SUAVE = colors.HexColor("#5a6b7a")
VERDE_COMENTARIO = colors.HexColor("#3d7a4a")
FONDO_CODIGO = colors.HexColor("#f7f9fb")
FONDO_FILA = colors.HexColor("#eef3f9")
FONDO_NOTA = colors.HexColor("#fdf5e6")
NARANJA = colors.HexColor("#b9770e")
BORDE = colors.HexColor("#c5d1e0")

ESTILOS = {
    "titulo": ParagraphStyle("titulo", fontName="Arial-Bold", fontSize=18, leading=22,
                             textColor=AZUL, spaceAfter=4),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Arial", fontSize=10, leading=14,
                                textColor=GRIS_SUAVE, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=13, leading=17,
                         textColor=AZUL, spaceBefore=6, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName="Arial-Bold", fontSize=11, leading=14,
                         textColor=GRIS_TEXTO, spaceBefore=4, spaceAfter=5),
    "cuerpo": ParagraphStyle("cuerpo", fontName="Arial", fontSize=10, leading=14,
                             textColor=GRIS_TEXTO, spaceAfter=6),
    "vineta": ParagraphStyle("vineta", fontName="Arial", fontSize=10, leading=14,
                             textColor=GRIS_TEXTO, leftIndent=14, bulletIndent=4,
                             spaceAfter=3),
    "nota": ParagraphStyle("nota", fontName="Arial", fontSize=9.5, leading=13,
                           textColor=GRIS_TEXTO),
    "sql": ParagraphStyle("sql", fontName="Consolas", fontSize=8.8, leading=12,
                          textColor=GRIS_TEXTO),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=8.8, leading=11.5,
                            textColor=GRIS_TEXTO),
    "celda_der": ParagraphStyle("celda_der", fontName="Arial", fontSize=8.8, leading=11.5,
                                textColor=GRIS_TEXTO, alignment=TA_RIGHT),
    "encabezado": ParagraphStyle("encabezado", fontName="Arial-Bold", fontSize=8.8,
                                 leading=11.5, textColor=colors.white),
    "encabezado_der": ParagraphStyle("encabezado_der", fontName="Arial-Bold", fontSize=8.8,
                                     leading=11.5, textColor=colors.white,
                                     alignment=TA_RIGHT),
}

ANCHO_UTIL = A4[0] - 4 * cm


def en_linea(texto: str) -> str:
    """Pasa el formato en línea de Markdown al marcado de reportlab."""
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)  # enlace -> solo el texto
    texto = re.sub(r"`([^`]+)`", r'<font name="Consolas" color="#2e4a7d">\1</font>', texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<i>\1</i>", texto)
    return texto


def bloque_sql(lineas: list[str]) -> Table:
    """SQL en monoespaciada, con los comentarios -- en verde."""
    filas = []
    for linea in lineas:
        estilo = ESTILOS["sql"]
        if linea.lstrip().startswith("--"):
            estilo = ParagraphStyle("sql_com", parent=estilo, textColor=VERDE_COMENTARIO)
        filas.append(Preformatted(linea or " ", estilo))
    tabla = Table([[f] for f in filas], colWidths=[ANCHO_UTIL])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO_CODIGO),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, AZUL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    return tabla


def ancho_texto(celda: str) -> float:
    """Ancho en puntos de una celda, midiendo el `código` en Consolas."""
    ancho = 0.0
    for n, parte in enumerate(celda.split("`")):
        fuente = "Consolas" if n % 2 else "Arial-Bold"  # negrita: cubre el encabezado
        ancho += pdfmetrics.stringWidth(parte.replace("**", ""), fuente, 8.8)
    return ancho


def tabla_md(lineas: list[str]) -> Table:
    """Tabla Markdown (con fila de alineación |---|---:|) a Table de reportlab."""
    def celdas(linea):
        return [c.strip() for c in linea.strip().strip("|").split("|")]

    encabezado, alineacion, *cuerpo = [celdas(l) for l in lineas]
    a_derecha = [a.endswith(":") and not a.startswith(":") for a in alineacion]

    datos = [[Paragraph(en_linea(c), ESTILOS["encabezado_der" if der else "encabezado"])
              for c, der in zip(encabezado, a_derecha)]]
    for fila in cuerpo:
        datos.append([Paragraph(en_linea(c), ESTILOS["celda_der" if der else "celda"])
                      for c, der in zip(fila, a_derecha)])

    # Cada columna arranca con el ancho de su texto más largo (para que fechas
    # y números no se corten). Si sobra lugar se reparte. Si falta, las
    # columnas que entran en su parte proporcional conservan su ancho y el
    # resto del espacio se reparte entre las de texto largo, que van en
    # varias líneas.
    anchos = [max(ancho_texto(f[i]) for f in [encabezado] + cuerpo) + 14
              for i in range(len(encabezado))]
    if sum(anchos) <= ANCHO_UTIL:
        anchos = [a * ANCHO_UTIL / sum(anchos) for a in anchos]
    else:
        largas = set(range(len(anchos)))
        while True:
            libre = ANCHO_UTIL - sum(a for i, a in enumerate(anchos) if i not in largas)
            parte = libre / len(largas)
            cortas = {i for i in largas if anchos[i] <= parte}
            if not cortas:
                break
            largas -= cortas
        total_largas = sum(anchos[i] for i in largas)
        for i in largas:
            anchos[i] = libre * anchos[i] / total_largas

    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_FILA]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tabla


def nota(texto: str) -> Table:
    """Cita (> ...) como recuadro de nota."""
    tabla = Table([[Paragraph(en_linea(texto), ESTILOS["nota"])]], colWidths=[ANCHO_UTIL])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO_NOTA),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NARANJA),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla


def convertir(md: str) -> list:
    """Recorre el .md línea por línea y arma la lista de elementos del PDF."""
    lineas = md.splitlines()
    elementos = []
    parrafo = []
    i = 0

    def cerrar_parrafo():
        if parrafo:
            elementos.append(Paragraph(en_linea(" ".join(parrafo)), ESTILOS["cuerpo"]))
            parrafo.clear()

    while i < len(lineas):
        linea = lineas[i]
        if linea.startswith("```"):
            cerrar_parrafo()
            j = i + 1
            while not lineas[j].startswith("```"):
                j += 1
            elementos += [bloque_sql(lineas[i + 1:j]), Spacer(1, 8)]
            i = j + 1
            continue
        if linea.startswith("|"):
            cerrar_parrafo()
            j = i
            while j < len(lineas) and lineas[j].startswith("|"):
                j += 1
            elementos += [tabla_md(lineas[i:j]), Spacer(1, 8)]
            i = j
            continue
        if linea.startswith("> "):
            cerrar_parrafo()
            texto = []
            while i < len(lineas) and lineas[i].startswith(">"):
                texto.append(lineas[i].lstrip("> "))
                i += 1
            elementos += [nota(" ".join(texto)), Spacer(1, 8)]
            continue
        if linea.startswith("- "):
            cerrar_parrafo()
            texto = [linea[2:]]
            i += 1
            while i < len(lineas) and lineas[i].startswith("  "):
                texto.append(lineas[i].strip())
                i += 1
            elementos.append(Paragraph(en_linea(" ".join(texto)), ESTILOS["vineta"],
                                       bulletText="•"))
            continue

        if linea.startswith("# "):
            cerrar_parrafo()
            hoy = date.today()
            elementos += [
                Paragraph(en_linea(linea[2:]), ESTILOS["titulo"]),
                Paragraph(f"{AUTOR} · Data Science II (Coderhouse) · "
                          f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}",
                          ESTILOS["subtitulo"]),
            ]
        elif linea.startswith("### "):
            cerrar_parrafo()
            elementos.append(Paragraph(en_linea(linea[4:]), ESTILOS["h3"]))
        elif linea.startswith("## "):
            cerrar_parrafo()
            elementos.append(Paragraph(en_linea(linea[3:]), ESTILOS["h2"]))
        elif linea.strip() == "---":
            cerrar_parrafo()
            elementos.append(HRFlowable(width="100%", thickness=0.6, color=BORDE,
                                        spaceBefore=4, spaceAfter=8))
        elif linea.strip() == AUTOR:
            cerrar_parrafo()  # la firma ya está en el subtítulo
        elif not linea.strip():
            cerrar_parrafo()
        else:
            parrafo.append(linea.strip())
        i += 1
    cerrar_parrafo()

    # El separador final (antes de la firma) sobra
    while isinstance(elementos[-1], HRFlowable):
        elementos.pop()

    # Que un título o un "Resultado:" no queden solos al pie de una página, y
    # que las tablas no se partan entre dos páginas
    # (sin anidar KeepTogether: anidados, reportlab salta de página de más)
    agrupados = []
    for el in elementos:
        previo = agrupados[-1] if agrupados else None
        presenta_lo_siguiente = isinstance(previo, Paragraph) and (
            previo.style.name in ("h2", "h3") or previo.text.rstrip().endswith(":")
        )
        if presenta_lo_siguiente:
            agrupados[-1] = KeepTogether([previo, el])
        elif isinstance(el, Table):
            agrupados.append(KeepTogether([el]))
        else:
            agrupados.append(el)
    return agrupados


def numerar_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(GRIS_SUAVE)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main() -> None:
    doc = SimpleDocTemplate(
        str(RUTA_PDF), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="Ejecución eficiente de queries analíticas", author=AUTOR,
    )
    doc.build(convertir(RUTA_MD.read_text(encoding="utf-8")),
              onFirstPage=numerar_pagina, onLaterPages=numerar_pagina)
    print(f"PDF generado: {RUTA_PDF}")


if __name__ == "__main__":
    main()
