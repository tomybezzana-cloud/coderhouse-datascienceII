"""
Ciclo de vida de Machine Learning - Data Science II
Caso: predecir si un pedido de e-commerce será devuelto, para alertar al
equipo de soporte antes de realizar el envío.

A partir de una única definición del diagrama (etapas, flechas y bucles)
genera dos archivos:

- ciclo_vida_ml_devoluciones.png    -> imagen lista para ver en GitHub
- ciclo_vida_ml_devoluciones.drawio -> el mismo diagrama, editable en
                                       draw.io / app.diagrams.net
"""

import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

BASE_DIR = Path(__file__).resolve().parent
RUTA_PNG = BASE_DIR / "ciclo_vida_ml_devoluciones.png"
RUTA_DRAWIO = BASE_DIR / "ciclo_vida_ml_devoluciones.drawio"

# Lienzo en "unidades" (pulgadas en matplotlib, x60 px en draw.io)
ANCHO, ALTO = 26, 18
PX = 60

COLOR_TEXTO = "#1b2733"
COLOR_BORDE = "#33475b"
COLOR_FLUJO = "#33475b"
COLOR_ITERACION = "#c0392b"
COLOR_PRODUCCION = "#1e8449"

BOX_W, BOX_H, HEADER_H = 7.2, 5.4, 0.6

# ---------------------------------------------------------------------------
# Contenido del diagrama
# Líneas: "• " viñeta, "  " continuación indentada, "! " subtítulo en negrita
# ---------------------------------------------------------------------------
ETAPAS = [
    {
        "id": "definicion",
        "titulo": "1. DEFINICIÓN DEL PROBLEMA",
        "x": 1.0, "y": 9.6, "color": "#5b6abf",
        "lineas": [
            "! Pregunta de negocio",
            "• ¿Este pedido va a ser devuelto? Se responde ANTES del envío.",
            "! Variable objetivo (target)",
            "• devuelto = 1 si el cliente devuelve el pedido dentro de",
            "  los 30 días; devuelto = 0 si no.",
            "! Tipo de tarea: CLASIFICACIÓN BINARIA",
            "! Objetivo de negocio medible",
            "• Bajar la tasa de devolución del 15% al 12% en 6 meses.",
            "! Acción que dispara el modelo",
            "• Alerta a soporte para contactar al cliente antes de",
            "  despachar (confirmar talle, color, dirección).",
        ],
    },
    {
        "id": "adquisicion",
        "titulo": "2. ADQUISICIÓN DE DATOS (SQL)",
        "x": 9.4, "y": 9.6, "color": "#2e86c1",
        "lineas": [
            "• pedidos: fecha, monto, % descuento, medio de pago, canal",
            "• detalle_pedido: productos, talles, cantidades por pedido",
            "• usuarios: antigüedad, nº de compras previas, zona",
            "• productos: categoría, precio, marca, guía de talles",
            "• devoluciones: historial y motivo → genera la etiqueta",
            "• envios: zona de destino, transportista, plazo prometido",
            "• resenas: calificaciones y quejas del producto",
            "! Regla anti-fuga (data leakage)",
            "• Solo se usan datos que existen ANTES de despachar.",
            "  Ej.: el 'motivo de devolución' NO puede ser una feature.",
        ],
    },
    {
        "id": "preparacion",
        "titulo": "3. PREPARACIÓN DE DATOS",
        "x": 17.8, "y": 9.6, "color": "#17a589",
        "lineas": [
            "• Limpieza: nulos, duplicados, tipos de dato, outliers.",
            "• Features: % de devolución del cliente y del producto,",
            "  mismo producto en varios talles, 1ª compra, % descuento.",
            "• Clase desbalanceada (15% devueltos): verificar que Train",
            "  y Test mantengan esa proporción; usar class_weight.",
            "! División de datos: corte TEMPORAL (12 meses)",
            "• Se entrena con el pasado y se prueba con el 'futuro',",
            "  igual que en producción. El Test se aparta y no se toca.",
        ],
        "barra_split": True,
    },
    {
        "id": "modelado",
        "titulo": "4. MODELADO",
        "x": 17.8, "y": 2.0, "color": "#d68910",
        "lineas": [
            "! Empezar por un baseline",
            "• Baseline 1: 'nadie devuelve' → 85% de accuracy pero",
            "  0% de devoluciones detectadas. Muestra el piso a superar.",
            "• Baseline 2: regla simple: alertar si el cliente ya",
            "  devolvió 2 o más pedidos.",
            "! Iterar hacia la complejidad",
            "• Regresión logística → árbol de decisión →",
            "  random forest / gradient boosting.",
            "• Hiperparámetros con validación cruzada SOLO sobre Train.",
            "• El modelo devuelve una probabilidad; el umbral de",
            "  alerta se elige en la evaluación.",
        ],
    },
    {
        "id": "evaluacion",
        "titulo": "5. EVALUACIÓN (sobre el Test Set, una sola vez)",
        "x": 9.4, "y": 2.0, "color": "#c0392b",
        "lineas": [
            "! Prioridad: atrapar devolutores, sin saturar a soporte",
            "• Un falso negativo cuesta un envío de ida y vuelta.",
            "• Un falso positivo cuesta un mensaje amable al cliente.",
            "  → Se prioriza RECALL, con un piso de PRECISIÓN.",
            "! Métrica de éxito",
            "• Detectar ≥ 75% de las devoluciones (recall)",
            "• con precisión ≥ 40%: de cada 10 alertas, al menos 4",
            "  son devoluciones reales (al azar serían 1,5).",
            "• Accuracy NO sirve: el baseline ya da 85%.",
            "! Validación de negocio",
            "• Ahorro logístico estimado > costo de contactar clientes.",
        ],
    },
    {
        "id": "produccion",
        "titulo": "6. PRODUCCIÓN Y MONITOREO",
        "x": 1.0, "y": 2.0, "color": "#7d3c98",
        "lineas": [
            "! Despliegue",
            "• Se ejecuta cuando se confirma el pago, antes de despachar.",
            "• Probabilidad > umbral → ticket de alerta para soporte.",
            "! Monitoreo",
            "• Recall y precisión reales (la etiqueta llega a los 30 días).",
            "• Tasa de devolución general vs. objetivo del 12%.",
            "• Drift: temporadas (Hot Sale, Navidad), nuevos productos,",
            "  cambios en la política de devoluciones.",
            "! Mantenimiento",
            "• Reentrenamiento mensual con las devoluciones nuevas.",
        ],
    },
]

BANNER = {
    "x": 1.0, "y": 15.5, "w": 24.0, "h": 1.1,
    "titulo": "Tipo de problema: CLASIFICACIÓN BINARIA (¿se devuelve? sí / no)",
    "texto": (
        "Es clasificación y no regresión porque la salida es una categoría "
        "(devuelto / no devuelto), no un número continuo. El modelo estima la "
        "probabilidad de devolución y un umbral decide si se envía la alerta."
    ),
}

# Flechas: tipo "flujo" (camino principal), "iteracion" (vuelve desde
# Evaluación) o "produccion" (bucle que cierra el ciclo desde Producción).
FLECHAS = [
    {"tipo": "flujo", "puntos": [(8.2, 12.3), (9.4, 12.3)]},
    {"tipo": "flujo", "puntos": [(16.6, 12.3), (17.8, 12.3)]},
    {"tipo": "flujo", "puntos": [(23.5, 9.6), (23.5, 7.4)]},
    {"tipo": "flujo", "puntos": [(17.8, 4.7), (16.6, 4.7)]},
    {"tipo": "flujo", "puntos": [(9.4, 4.7), (8.2, 4.7)]},
    {
        "tipo": "iteracion",
        "puntos": [(14.5, 7.4), (19.5, 9.6)],
        "etiqueta": "¿No llega a la meta? → volver a Preparación:\nnuevas features, rebalancear clases",
        "pos": (17.0, 8.5),
    },
    {
        "tipo": "iteracion",
        "puntos": [(15.5, 2.0), (15.5, 1.4), (21.4, 1.4), (21.4, 2.0)],
        "etiqueta": "Probar otro algoritmo / ajustar el umbral",
        "pos": (18.45, 1.4),
    },
    {
        "tipo": "produccion",
        "puntos": [(6.5, 7.4), (11.0, 9.6)],
        "etiqueta": "Llegan devoluciones nuevas (etiquetas)\n→ reentrenar con datos actualizados",
        "pos": (8.75, 8.5),
    },
    {
        "tipo": "produccion",
        "puntos": [(2.2, 7.4), (2.2, 9.6)],
        "etiqueta": "Cambia el negocio\n→ redefinir la pregunta",
        "pos": (3.9, 8.5),
    },
]

ESTILO_FLECHA = {
    "flujo": {"color": COLOR_FLUJO, "linestyle": "-", "lw": 2.4},
    "iteracion": {"color": COLOR_ITERACION, "linestyle": "--", "lw": 2.2},
    "produccion": {"color": COLOR_PRODUCCION, "linestyle": "--", "lw": 2.2},
}

LEYENDA = [
    ("flujo", "Flujo principal del proyecto"),
    ("iteracion", "Iteración: el modelo no alcanza la meta en la evaluación"),
    ("produccion", "Bucle de producción: el ciclo vuelve a empezar"),
]


def lineas_envueltas(lineas, ancho=68):
    """Envuelve cada línea larga respetando viñetas e indentación."""
    for linea in lineas:
        if linea.startswith("! "):
            yield linea[2:], True
            continue
        sangria = "  " if linea.startswith(("• ", "  ")) else ""
        for parte in textwrap.wrap(linea, ancho, subsequent_indent=sangria) or [""]:
            yield parte, False


def split_rects(etapa):
    """Rectángulos Train / Test dentro de la etapa de Preparación."""
    x0, y0 = etapa["x"] + 0.3, etapa["y"] + 0.3
    ancho, alto = BOX_W - 0.6, 0.75
    train = (x0, y0, ancho * 0.8, alto)
    test = (x0 + ancho * 0.8, y0, ancho * 0.2, alto)
    return train, test


# ---------------------------------------------------------------------------
# PNG con matplotlib
# ---------------------------------------------------------------------------
def dibujar_png():
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    ax.set_xlim(0, ANCHO)
    ax.set_ylim(0, ALTO)
    ax.axis("off")

    ax.text(ANCHO / 2, 17.45, "Ciclo de vida de ML: predicción de devoluciones en e-commerce",
            ha="center", va="center", fontsize=24, fontweight="bold", color=COLOR_TEXTO)
    ax.text(ANCHO / 2, 16.95,
            "Contexto: el 15% de los productos vendidos se devuelve. "
            "Objetivo: alertar a soporte antes del envío.",
            ha="center", va="center", fontsize=13, color="#5a6b7a")

    b = BANNER
    ax.add_patch(FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"],
                                boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="#fef5e7", edgecolor="#d68910", linewidth=2))
    ax.text(b["x"] + 0.3, b["y"] + b["h"] - 0.3, b["titulo"], ha="left", va="center",
            fontsize=14, fontweight="bold", color="#9c640c")
    ax.text(b["x"] + 0.3, b["y"] + 0.3, b["texto"], ha="left", va="center",
            fontsize=11, color=COLOR_TEXTO)

    for e in ETAPAS:
        ax.add_patch(FancyBboxPatch((e["x"], e["y"]), BOX_W, BOX_H,
                                    boxstyle="round,pad=0,rounding_size=0.15",
                                    facecolor="white", edgecolor=e["color"], linewidth=2.2, zorder=2))
        ax.add_patch(Rectangle((e["x"], e["y"] + BOX_H - HEADER_H), BOX_W, HEADER_H,
                               facecolor=e["color"], edgecolor=e["color"], zorder=3))
        ax.text(e["x"] + 0.25, e["y"] + BOX_H - HEADER_H / 2, e["titulo"], ha="left", va="center",
                fontsize=13, fontweight="bold", color="white", zorder=4)

        y = e["y"] + BOX_H - HEADER_H - 0.3
        for texto, negrita in lineas_envueltas(e["lineas"]):
            ax.text(e["x"] + 0.25, y, texto, ha="left", va="center", fontsize=10.5,
                    fontweight="bold" if negrita else "normal",
                    color=e["color"] if negrita else COLOR_TEXTO, zorder=4)
            y -= 0.27

        if e.get("barra_split"):
            train, test = split_rects(e)
            ax.add_patch(Rectangle(train[:2], *train[2:], facecolor="#d1f2eb",
                                   edgecolor="#17a589", linewidth=1.5, zorder=3))
            ax.add_patch(Rectangle(test[:2], *test[2:], facecolor="#fadbd8",
                                   edgecolor="#c0392b", linewidth=1.5, zorder=3))
            ax.text(train[0] + train[2] / 2, train[1] + train[3] / 2,
                    "TRAIN 80%  ·  ene–sep\nentrenar + validación cruzada",
                    ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0e6655", zorder=4)
            ax.text(test[0] + test[2] / 2, test[1] + test[3] / 2, "TEST 20%\noct–dic",
                    ha="center", va="center", fontsize=9.5, fontweight="bold", color="#922b21", zorder=4)

    for f in FLECHAS:
        estilo = ESTILO_FLECHA[f["tipo"]]
        pts = f["puntos"]
        for i in range(len(pts) - 1):
            ultimo = i == len(pts) - 2
            ax.add_patch(FancyArrowPatch(
                pts[i], pts[i + 1],
                arrowstyle="-|>,head_length=0.7,head_width=0.4" if ultimo else "-",
                mutation_scale=22, shrinkA=0, shrinkB=0, zorder=5, **estilo,
            ))
        if f.get("etiqueta"):
            ax.text(*f["pos"], f["etiqueta"], ha="center", va="center", fontsize=10,
                    fontweight="bold", color=estilo["color"], zorder=6,
                    bbox={"boxstyle": "round,pad=0.25", "facecolor": "white",
                          "edgecolor": estilo["color"], "linewidth": 1})

    x = 1.0
    for tipo, texto in LEYENDA:
        estilo = ESTILO_FLECHA[tipo]
        ax.add_patch(FancyArrowPatch((x, 0.5), (x + 1.0, 0.5), arrowstyle="-|>",
                                     mutation_scale=16, **estilo))
        ax.text(x + 1.2, 0.5, texto, ha="left", va="center", fontsize=11, color=COLOR_TEXTO)
        x += 7.6

    fig.savefig(RUTA_PNG, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# .drawio (XML de draw.io)
# ---------------------------------------------------------------------------
def px(x, y):
    """Convierte unidades del lienzo (origen abajo) a píxeles de draw.io (origen arriba)."""
    return round(x * PX), round((ALTO - y) * PX)


def html(texto):
    return (texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br>"))


class Drawio:
    def __init__(self):
        self.mxfile = ET.Element("mxfile", host="app.diagrams.net")
        diagram = ET.SubElement(self.mxfile, "diagram", name="Ciclo de vida ML", id="ciclo-ml")
        model = ET.SubElement(diagram, "mxGraphModel", grid="1", gridSize="10", page="1",
                              pageWidth=str(ANCHO * PX), pageHeight=str(ALTO * PX))
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.n = 1

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def caja(self, x, y, w, h, valor, estilo):
        """x, y: esquina inferior izquierda en unidades del lienzo."""
        left, top = px(x, y + h)
        celda = ET.SubElement(self.root, "mxCell", id=self._id(), value=valor,
                              style=estilo, vertex="1", parent="1")
        ET.SubElement(celda, "mxGeometry", x=str(left), y=str(top),
                      width=str(round(w * PX)), height=str(round(h * PX)), **{"as": "geometry"})

    def flecha(self, puntos, valor, estilo):
        celda = ET.SubElement(self.root, "mxCell", id=self._id(), value=valor,
                              style=estilo, edge="1", parent="1")
        geo = ET.SubElement(celda, "mxGeometry", relative="1", **{"as": "geometry"})
        sx, sy = px(*puntos[0])
        tx, ty = px(*puntos[-1])
        ET.SubElement(geo, "mxPoint", x=str(sx), y=str(sy), **{"as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", x=str(tx), y=str(ty), **{"as": "targetPoint"})
        if len(puntos) > 2:
            arr = ET.SubElement(geo, "Array", **{"as": "points"})
            for p in puntos[1:-1]:
                x, y = px(*p)
                ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))

    def guardar(self, ruta):
        ET.indent(self.mxfile)
        ET.ElementTree(self.mxfile).write(ruta, encoding="utf-8", xml_declaration=False)


def generar_drawio():
    d = Drawio()
    base = "html=1;whiteSpace=wrap;"

    d.caja(1.0, 16.7, 24.0, 1.1,
           "<b style='font-size:24px'>Ciclo de vida de ML: predicción de devoluciones en e-commerce</b><br>"
           "<span style='font-size:13px;color:#5a6b7a'>Contexto: el 15% de los productos vendidos se devuelve. "
           "Objetivo: alertar a soporte antes del envío.</span>",
           base + "text;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;")

    b = BANNER
    d.caja(b["x"], b["y"], b["w"], b["h"],
           f"<b style='font-size:15px;color:#9c640c'>{html(b['titulo'])}</b><br>{html(b['texto'])}",
           base + "rounded=1;arcSize=10;align=left;verticalAlign=middle;spacingLeft=14;"
           "fillColor=#fef5e7;strokeColor=#d68910;strokeWidth=2;fontSize=12;fontColor=#1b2733;")

    for e in ETAPAS:
        cuerpo = []
        for linea in e["lineas"]:
            if linea.startswith("! "):
                cuerpo.append(f"<b style='color:{e['color']}'>{html(linea[2:])}</b>")
            elif linea.startswith("  ") and cuerpo:
                cuerpo[-1] += " " + html(linea.strip())
            else:
                cuerpo.append(html(linea))
        d.caja(e["x"], e["y"], BOX_W, BOX_H, "<br>".join(cuerpo),
               base + f"rounded=1;arcSize=4;align=left;verticalAlign=top;spacingLeft=10;spacingRight=8;"
               f"spacingTop={HEADER_H * PX + 6};fillColor=#ffffff;strokeColor={e['color']};"
               "strokeWidth=2;fontSize=12;fontColor=#1b2733;")
        d.caja(e["x"], e["y"] + BOX_H - HEADER_H, BOX_W, HEADER_H, f"<b>{html(e['titulo'])}</b>",
               base + f"rounded=0;align=left;verticalAlign=middle;spacingLeft=10;fillColor={e['color']};"
               f"strokeColor={e['color']};fontColor=#ffffff;fontSize=14;")
        if e.get("barra_split"):
            train, test = split_rects(e)
            d.caja(*train, "<b>TRAIN 80% · ene–sep</b><br>entrenar + validación cruzada",
                   base + "align=center;fillColor=#d1f2eb;strokeColor=#17a589;fontColor=#0e6655;fontSize=11;")
            d.caja(*test, "<b>TEST 20%<br>oct–dic</b>",
                   base + "align=center;fillColor=#fadbd8;strokeColor=#c0392b;fontColor=#922b21;fontSize=11;")

    for f in FLECHAS:
        estilo = ESTILO_FLECHA[f["tipo"]]
        guiones = "dashed=1;dashPattern=8 6;" if estilo["linestyle"] == "--" else ""
        d.flecha(f["puntos"], f"<b>{html(f.get('etiqueta', ''))}</b>",
                 base + f"edgeStyle=none;endArrow=block;endFill=1;strokeWidth=2.5;{guiones}"
                 f"strokeColor={estilo['color']};fontColor={estilo['color']};fontSize=12;"
                 f"labelBackgroundColor=#ffffff;labelBorderColor={estilo['color']};")

    x = 1.0
    for tipo, texto in LEYENDA:
        estilo = ESTILO_FLECHA[tipo]
        guiones = "dashed=1;dashPattern=8 6;" if estilo["linestyle"] == "--" else ""
        d.flecha([(x, 0.5), (x + 1.0, 0.5)], "",
                 base + f"endArrow=block;endFill=1;strokeWidth=2.5;{guiones}strokeColor={estilo['color']};")
        d.caja(x + 1.1, 0.3, 6.2, 0.4, html(texto),
               base + "text;align=left;verticalAlign=middle;strokeColor=none;fillColor=none;fontSize=13;")
        x += 7.6

    d.guardar(RUTA_DRAWIO)


if __name__ == "__main__":
    dibujar_png()
    generar_drawio()
    print(f"Generado: {RUTA_PNG.name}")
    print(f"Generado: {RUTA_DRAWIO.name}")
