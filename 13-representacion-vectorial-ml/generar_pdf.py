"""
Procesamiento Vectorial para Datos de ML.

Genera Representacion_Vectorial_Bezzana_Tomas.pdf con las 4 tareas: usuarios de
streaming como vectores, operaciones (suma, escalado, producto punto),
vectorización de texto con Bag of Words y la conclusión sobre funciones
vectorizadas.
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
RUTA_PDF = BASE_DIR / "Representacion_Vectorial_Bezzana_Tomas.pdf"

AUTOR = "Tomás Bezzana"
FECHA = "25 de octubre de 2026"

# Arial (incluida en Windows) para que los acentos y la ñ se vean bien
FUENTES = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", FUENTES / "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FUENTES / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FUENTES / "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", FUENTES / "arialbi.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")
# Consolas para las cuentas, así los números quedan alineados
pdfmetrics.registerFont(TTFont("Consolas", FUENTES / "consola.ttf"))
pdfmetrics.registerFont(TTFont("Consolas-Bold", FUENTES / "consolab.ttf"))
pdfmetrics.registerFontFamily("Consolas", normal="Consolas", bold="Consolas-Bold",
                              italic="Consolas", boldItalic="Consolas-Bold")

AZUL = colors.HexColor("#2e4a7d")
GRIS_TEXTO = colors.HexColor("#1b2733")
GRIS_SUAVE = colors.HexColor("#5a6b7a")
FONDO_ETIQUETA = colors.HexColor("#eef3f9")
FONDO_CUENTA = colors.HexColor("#f7f9fb")
BORDE = colors.HexColor("#c5d1e0")
VERDE = colors.HexColor("#1e8449")
NARANJA = colors.HexColor("#b9770e")
FONDO_NARANJA = colors.HexColor("#fdf5e6")

ESTILOS = {
    "titulo": ParagraphStyle("titulo", fontName="Arial-Bold", fontSize=19, leading=23,
                             textColor=AZUL, spaceAfter=4),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Arial", fontSize=10.5, leading=14,
                                textColor=GRIS_SUAVE, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=13.5, leading=17,
                         textColor=AZUL, spaceBefore=12, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11, leading=14,
                         textColor=GRIS_TEXTO, spaceBefore=8, spaceAfter=4),
    "cuerpo": ParagraphStyle("cuerpo", fontName="Arial", fontSize=10, leading=14,
                             textColor=GRIS_TEXTO, spaceAfter=6),
    "cuenta": ParagraphStyle("cuenta", fontName="Consolas", fontSize=9.5, leading=14,
                             textColor=GRIS_TEXTO),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=9.5, leading=13,
                            textColor=GRIS_TEXTO),
    "celda_centro": ParagraphStyle("celda_centro", fontName="Arial", fontSize=9.5, leading=13,
                                   textColor=GRIS_TEXTO, alignment=TA_CENTER),
    "celda_mono": ParagraphStyle("celda_mono", fontName="Consolas", fontSize=9.5, leading=13,
                                 textColor=GRIS_TEXTO, alignment=TA_CENTER),
    "encabezado_tabla": ParagraphStyle("encabezado_tabla", fontName="Arial-Bold", fontSize=9.5,
                                       leading=13, textColor=colors.white, alignment=TA_CENTER),
}

ANCHO_UTIL = A4[0] - 4 * cm

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
GENEROS = ["Rock", "Pop", "Jazz"]
USUARIOS = {"A": [10, 2, 0], "B": [1, 12, 1], "C": [8, 3, 1]}

VOCABULARIO = ["Amo", "el", "café", "Odio", "té"]
FRASES = ["Amo el café", "Odio el café", "Amo el té"]


def vector_presencia(frase):
    palabras = frase.split()
    return [1 if p in palabras else 0 for p in VOCABULARIO]


def producto_punto(u, v):
    return sum(a * b for a, b in zip(u, v))


def fmt(v):
    return "[" + ", ".join(str(x) for x in v) + "]"


# ---------------------------------------------------------------------------
# Componentes
# ---------------------------------------------------------------------------
def tabla(filas, anchos, columnas_mono, resaltar=None):
    """Tabla con encabezado azul. resaltar: lista de (fila, color de fondo)."""
    e = ESTILOS
    contenido = [[Paragraph(str(c), e["encabezado_tabla"]) for c in filas[0]]]
    for fila in filas[1:]:
        contenido.append([
            Paragraph(str(c), e["celda_mono"] if i in columnas_mono else e["celda"])
            for i, c in enumerate(fila)
        ])
    t = Table(contenido, colWidths=anchos)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_ETIQUETA]),
        ("GRID", (0, 0), (-1, -1), 0.6, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for fila, color in resaltar or []:
        estilo.append(("BACKGROUND", (0, fila), (-1, fila), color))
    t.setStyle(TableStyle(estilo))
    return t


def caja(lineas, color=BORDE, fondo=FONDO_CUENTA, estilo="cuenta"):
    """Recuadro para cuentas paso a paso o notas destacadas."""
    # Paragraph colapsa los espacios, así que la sangría se pasa a &nbsp;
    lineas = [
        "&nbsp;" * (len(l) - len(l.lstrip(" "))) + l.lstrip(" ") for l in lineas
    ]
    t = Table([[Paragraph("<br/>".join(lineas), ESTILOS[estilo])]], colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("BOX", (0, 0), (-1, -1), 0.8, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def resultado(texto):
    return f"<font color='{VERDE.hexval()}'><b>{texto}</b></font>"


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------
def tarea_1():
    e = ESTILOS
    filas = [["Usuario", *[f"{g} (h)" for g in GENEROS], "Vector U = [Rock, Pop, Jazz]"]]
    for nombre, v in USUARIOS.items():
        filas.append([f"<b>Usuario {nombre}</b>", *v, f"<b>U<sub>{nombre}</sub> = {fmt(v)}</b>"])
    return [
        Paragraph("Tarea 1: De la realidad al vector", e["h1"]),
        Paragraph(
            "Cada usuario se representa como un vector de 3 dimensiones. El <b>orden de los "
            "componentes es fijo</b> y es el mismo para todos: la posición 1 siempre es Rock, la 2 "
            "Pop y la 3 Jazz. Esto es lo que permite compararlos y operar entre ellos: si el orden "
            "cambiara de un usuario a otro, sumaríamos horas de Rock con horas de Pop.", e["cuerpo"]),
        tabla(filas, [2.6 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, ANCHO_UTIL - 8.9 * cm],
              columnas_mono={1, 2, 3, 4}),
        Spacer(1, 6),
        Paragraph(
            "A simple vista ya se ve que A y C son oyentes principalmente de Rock, mientras que B "
            "escucha casi solo Pop. Las operaciones de la Tarea 2 permiten medir esto con números.",
            e["cuerpo"]),
    ]


def tarea_2():
    e = ESTILOS
    A, B, C = USUARIOS["A"], USUARIOS["B"], USUARIOS["C"]
    suma = [a + c for a, c in zip(A, C)]
    escalado = [2 * b for b in B]
    punto_ac = producto_punto(A, C)
    punto_ab = producto_punto(A, B)
    punto_bc = producto_punto(B, C)

    return [
        Paragraph("Tarea 2: Operaciones matemáticas", e["h1"]),

        Paragraph("a) Suma de intereses: perfil de grupo A + C", e["h2"]),
        Paragraph("Se suman los componentes que están en la misma posición (género con género):",
                  e["cuerpo"]),
        caja([
            f"U<sub>A</sub> + U<sub>C</sub> = {fmt(A)} + {fmt(C)}",
            f"        = [{A[0]} + {C[0]}, {A[1]} + {C[1]}, {A[2]} + {C[2]}]",
            f"        = {resultado(fmt(suma))}",
        ]),
        Spacer(1, 4),
        Paragraph(
            f"El grupo escucha en total {suma[0]} h de Rock, {suma[1]} h de Pop y {suma[2]} h de "
            "Jazz. El perfil conserva la preferencia por el Rock que tienen los dos usuarios.",
            e["cuerpo"]),

        Paragraph("b) Escalado: el usuario B duplica su tiempo de escucha", e["h2"]),
        Paragraph("Se multiplica cada componente por el escalar 2:", e["cuerpo"]),
        caja([
            f"2 · U<sub>B</sub> = 2 · {fmt(B)}",
            f"       = [2·{B[0]}, 2·{B[1]}, 2·{B[2]}]",
            f"       = {resultado(fmt(escalado))}",
        ]),
        Spacer(1, 4),
        Paragraph(
            "El vector se hace el doble de largo pero <b>apunta en la misma dirección</b>: B escucha "
            "más horas, pero sus gustos (la proporción entre géneros) no cambian. Siguen siendo "
            "1/14 Rock, 12/14 Pop y 1/14 Jazz.", e["cuerpo"]),

        KeepTogether([
            Paragraph("c) Producto punto (similitud) entre A y C", e["h2"]),
            Paragraph("Se multiplican los componentes de la misma posición y se suman los "
                      "resultados:", e["cuerpo"]),
            caja([
                f"U<sub>A</sub> · U<sub>C</sub> = (Rock·Rock) + (Pop·Pop) + (Jazz·Jazz)",
                f"        = ({A[0]}·{C[0]}) + ({A[1]}·{C[1]}) + ({A[2]}·{C[2]})",
                f"        = {A[0] * C[0]} + {A[1] * C[1]} + {A[2] * C[2]}",
                f"        = {resultado(punto_ac)}",
            ]),
        ]),
        Spacer(1, 4),
        Paragraph(
            "El resultado es un solo número (un escalar), no un vector. Es alto porque los dos "
            "usuarios tienen valores grandes <b>en el mismo género</b> (Rock): ese término solo aporta "
            f"{A[0] * C[0]} de los {punto_ac}.", e["cuerpo"]),
        Paragraph(
            "Para tener una referencia, comparando con los otros pares con la misma cuenta:",
            e["cuerpo"]),
        tabla(
            [["Par", "Producto punto", "Similitud coseno", "Lectura"],
             ["<b>A · C</b>", punto_ac, "0,98", "Gustos casi idénticos (ambos Rock)"],
             ["B · C", punto_bc, "0,43", "Poco parecidos"],
             ["A · B", punto_ab, "0,28", "Muy distintos (Rock vs. Pop)"]],
            [2.4 * cm, 3 * cm, 3.2 * cm, ANCHO_UTIL - 8.6 * cm],
            columnas_mono={1, 2},
            resaltar=[(1, colors.HexColor("#e9f7ef"))],
        ),
        Spacer(1, 6),
        Paragraph(
            "Un detalle: el producto punto crece si los usuarios escuchan más horas, aunque sus "
            "gustos no cambien (con 2·U<sub>B</sub> el producto punto con A se duplica). Por eso los "
            "sistemas de recomendación suelen usar la <b>similitud coseno</b>, que es el producto "
            "punto dividido por el largo de ambos vectores: solo mide si apuntan en la misma dirección "
            "y, como las horas nunca son negativas, va de 0 (nada en común) a 1 (mismos gustos). Para A y C: 86 / (√104 · √74) ≈ 0,98.", e["cuerpo"]),
    ]


def tarea_3():
    e = ESTILOS
    vectores = [vector_presencia(f) for f in FRASES]
    v1, v2, v3 = vectores
    p12, p13 = producto_punto(v1, v2), producto_punto(v1, v3)

    filas = [["Frase", *VOCABULARIO, "Vector"]]
    for i, (frase, v) in enumerate(zip(FRASES, vectores), start=1):
        filas.append([f"<b>{i}.</b> \"{frase}\"", *v, f"<b>{fmt(v)}</b>"])

    return [
        Paragraph("Tarea 3: Vectorización de texto (Bag of Words)", e["h1"]),

        Paragraph("Paso 2: Vocabulario único", e["h2"]),
        Paragraph(
            "Se recorren las tres frases y se anota cada palabra la primera vez que aparece, sin "
            "repetir. El vocabulario tiene 5 palabras, así que cada frase va a ser un vector de 5 "
            "dimensiones:", e["cuerpo"]),
        caja([f"Vocabulario = [{', '.join(VOCABULARIO)}]"]),

        Paragraph("Paso 3: Vectores de presencia", e["h2"]),
        Paragraph(
            "Para cada frase se marca <b>1</b> si la palabra del vocabulario aparece y <b>0</b> si "
            "no. Es la lógica de <i>Bag of Words</i> (\"bolsa de palabras\"): solo importa qué "
            "palabras hay, no en qué orden están.", e["cuerpo"]),
        tabla(filas, [3.8 * cm] + [1.5 * cm] * 5 + [ANCHO_UTIL - 11.3 * cm],
              columnas_mono={1, 2, 3, 4, 5, 6}),
        Spacer(1, 6),

        KeepTogether([
            Paragraph("¿Son más parecidas la frase 1 y la 3 que la 1 y la 2?", e["h2"]),
            Paragraph(
                "Se calcula el producto punto, que en vectores de presencia cuenta cuántas palabras "
                "comparten dos frases:", e["cuerpo"]),
            caja([
                f"F1 · F2 = {fmt(v1)} · {fmt(v2)}",
                f"        = 0 + 1 + 1 + 0 + 0 = {resultado(p12)}   (comparten \"el\" y \"café\")",
                "",
                f"F1 · F3 = {fmt(v1)} · {fmt(v3)}",
                f"        = 1 + 1 + 0 + 0 + 0 = {resultado(p13)}   (comparten \"Amo\" y \"el\")",
            ]),
        ]),
        Spacer(1, 6),
        caja([
            "<b>Resultado: numéricamente están empatadas.</b> Con vectores de presencia, la frase 1 "
            "se parece <b>exactamente lo mismo</b> a la 2 que a la 3. No es solo el producto punto: "
            "la distancia euclidiana es √2 en los dos casos y la similitud coseno es 2/3 en los "
            "dos casos. Cada par comparte 2 palabras y difiere en 2.",
        ], color=NARANJA, fondo=FONDO_NARANJA, estilo="cuerpo"),
        Spacer(1, 8),
        Paragraph(
            "Entonces, ¿por qué <i>parece</i> que la 1 y la 3 son más parecidas? Porque una persona "
            "lee el <b>significado</b>: \"Amo el café\" y \"Amo el té\" expresan lo mismo (alguien "
            "a quien le gusta una bebida), mientras que \"Odio el café\" dice lo contrario de la "
            "frase 1. Para nosotros, cambiar <i>Amo</i> por <i>Odio</i> da vuelta la frase, y cambiar "
            "<i>café</i> por <i>té</i> es un detalle.", e["cuerpo"]),
        Paragraph(
            "Bag of Words no ve esa diferencia: le da <b>el mismo peso a todas las palabras</b> y "
            "trata a cada una como una dimensión independiente. Para el modelo, \"Amo\" y \"Odio\" "
            "están tan lejos entre sí como \"café\" y \"té\". Y como la frase 1 comparte el "
            "sentimiento con la 3 pero el objeto con la 2, el resultado es un empate.", e["cuerpo"]),
        Paragraph(
            "La conclusión es justamente esa <b>limitación de Bag of Words</b>: cuenta palabras pero "
            "no entiende el significado ni la importancia de cada una. Ni siquiera sacar la palabra "
            "\"el\" (que está en todas) rompe el empate. Para que la 1 y la 3 queden más cerca hace "
            "falta darle más peso a las palabras de sentimiento (por ejemplo, un modelo de "
            "clasificación de sentimiento aprende pesos altos para \"Amo\" y \"Odio\") o usar "
            "<b>embeddings</b>, donde cada palabra es un vector aprendido y las palabras de "
            "significado parecido (\"café\" y \"té\") quedan cerca entre sí.", e["cuerpo"]),
    ]


def tarea_4():
    e = ESTILOS
    return [
        Paragraph("Tarea 4: Conclusión teórica", e["h1"]),
        Paragraph("¿Por qué preferimos funciones vectorizadas en lugar de un bucle for?", e["h2"]),
        Paragraph(
            "En un pipeline profesional preferimos las funciones vectorizadas de NumPy o Polars "
            "porque son mucho más <b>eficientes computacionalmente</b>. Un bucle <i>for</i> en "
            "Python procesa las filas de a una, y en cada vuelta el intérprete tiene que averiguar el "
            "tipo de cada valor, buscar la operación correspondiente y crear un objeto nuevo para el "
            "resultado; ese costo fijo se repite millones de veces. Una operación vectorizada, en "
            "cambio, le pasa la columna entera a código ya compilado (C en NumPy, Rust en Polars), "
            "que recorre los datos guardados uno al lado del otro en memoria, con un tipo único y "
            "conocido de antemano. Eso aprovecha la caché del procesador y las instrucciones "
            "<b>SIMD</b>, que operan sobre varios números a la vez, y en el caso de Polars además "
            "reparte el trabajo entre todos los núcleos (<b>paralelismo</b>) y optimiza la consulta "
            "completa antes de ejecutarla. El resultado suele ser entre 10 y 100 veces más rápido "
            "(o más), lo que marca la diferencia cuando el volumen de datos crece y el proceso tiene "
            "que correr todos los días. Como beneficio extra, el código queda más corto y legible: "
            "<font face='Consolas'>df[\"total\"] = df[\"precio\"] * df[\"cantidad\"]</font> expresa "
            "la misma operación matemática que vimos en la Tarea 2, aplicada a toda la columna de una "
            "sola vez, y deja menos lugar para errores que un bucle con índices.", e["cuerpo"]),
    ]


# ---------------------------------------------------------------------------
# Armado del documento
# ---------------------------------------------------------------------------
def pie_de_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8.5)
    canvas.setFillColor(GRIS_SUAVE)
    canvas.drawString(2 * cm, 1.2 * cm, f"Representación vectorial · {AUTOR}")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main():
    e = ESTILOS
    doc = SimpleDocTemplate(
        str(RUTA_PDF), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
        title="Representación Vectorial", author=AUTOR,
        subject="Procesamiento vectorial para datos de ML",
    )
    story = [
        Paragraph("Representación Vectorial", e["titulo"]),
        Paragraph(f"Procesamiento vectorial para datos de Machine Learning<br/>"
                  f"{AUTOR} · Data Science II (Coderhouse) · {FECHA}", e["subtitulo"]),
        *tarea_1(),
        *tarea_2(),
        *tarea_3(),
        *tarea_4(),
    ]
    doc.build(story, onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
    print(f"Generado: {RUTA_PDF.name}")


if __name__ == "__main__":
    main()
