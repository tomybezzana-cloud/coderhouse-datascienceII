"""
Práctica de diseño de sistema de adquisición de datos (DAQ) - Data Science II
Objetivo: diseñar teóricamente el flujo de adquisición de un sensor de
vibración en las palas de un aerogenerador, desde el fenómeno físico hasta
el archivo/base de datos final, identificando parámetros técnicos y riesgos
de calidad de dato antes de llegar al modelo de Machine Learning.

Genera dos archivos:
  - diagrama_daq_aerogenerador.png -> solo el diagrama de flujo (imagen)
  - diseno_daq_aerogenerador.pdf   -> diagrama + parámetros técnicos y
                                       análisis de riesgos (2 páginas)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle
from matplotlib.backends.backend_pdf import PdfPages

COLOR_BLOQUE = "#dbe9f6"
COLOR_ADC = "#fde9c8"
COLOR_BORDE = "#33475b"
COLOR_TEXTO = "#1b2733"
COLOR_RIESGO = "#c0392b"
COLOR_PANEL_HEAD = "#33475b"
COLOR_PANEL_BODY = "#eef3f7"


def draw_block(ax, cx, cy, w, h, titulo, lineas, color=COLOR_BLOQUE):
    """Dibuja un bloque del flujo DAQ: título en negrita + líneas de detalle."""
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=COLOR_BORDE, facecolor=color, zorder=3,
    )
    ax.add_patch(box)
    ax.text(cx, cy + h / 2 - 0.26, titulo, ha="center", va="top",
             fontsize=9.6, fontweight="bold", color=COLOR_TEXTO, zorder=4)
    ax.plot([cx - w / 2 + 0.12, cx + w / 2 - 0.12],
             [cy + h / 2 - 0.46, cy + h / 2 - 0.46],
             color=COLOR_BORDE, linewidth=0.7, zorder=4)
    y = cy + h / 2 - 0.68
    for linea in lineas:
        ax.text(cx, y, linea, ha="center", va="top", fontsize=7.6,
                 color=COLOR_TEXTO, zorder=4)
        y -= 0.26


def draw_arrow(ax, p1, p2):
    ax.annotate(
        "", xy=p2, xytext=p1,
        arrowprops=dict(arrowstyle="-|>", color=COLOR_BORDE, lw=1.6,
                         mutation_scale=16),
        zorder=2,
    )


def draw_riesgo(ax, x, box_bottom_y, texto):
    """Marca un punto de riesgo apuntando desde el borde inferior de la caja
    hacia un círculo y una etiqueta ubicados en el espacio libre debajo del
    diagrama, sin superponerse con ningún bloque."""
    circle_cy = box_bottom_y - 1.05
    ax.annotate(
        "", xy=(x, circle_cy + 0.35), xytext=(x, box_bottom_y),
        arrowprops=dict(arrowstyle="-", color=COLOR_RIESGO, lw=1.3,
                         linestyle="--"),
        zorder=5,
    )
    ax.add_patch(Ellipse((x, circle_cy), width=0.4, height=0.7, fill=False,
                          edgecolor=COLOR_RIESGO, linewidth=1.8,
                          linestyle="--", zorder=5))
    ax.text(x, circle_cy - 0.45, texto, ha="center", va="top",
             fontsize=7.8, fontweight="bold", color=COLOR_RIESGO, zorder=5)


def construir_diagrama():
    fig, ax = plt.subplots(figsize=(15, 6.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title(
        "Flujo de adquisición de datos (DAQ) · Sensor de vibración en pala de aerogenerador",
        fontsize=13.5, fontweight="bold", color=COLOR_TEXTO, pad=14,
    )

    cy = 4.5
    w, h = 2.15, 1.75
    xs = [1.4, 3.85, 6.3, 8.75, 11.2, 13.6]

    draw_block(
        ax, xs[0], cy, w, h, "FENÓMENO FÍSICO",
        ["Vibración mecánica", "de la pala", "(~200 Hz + armónicos)"],
    )
    draw_block(
        ax, xs[1], cy, w, h, "SENSOR / TRANSDUCTOR",
        ["Acelerómetro", "piezoeléctrico / MEMS", "vibración → voltaje"],
    )
    draw_block(
        ax, xs[2], cy, w, h, "ACONDICIONAMIENTO",
        ["Amplificación +", "filtro anti-aliasing", "(pasa-bajos)"],
    )
    draw_block(
        ax, xs[3], cy, w, h, "ADC\n(digitalización)",
        ["fs ≥ 2 kHz", "16-24 bits", "aquí se digitaliza"],
        color=COLOR_ADC,
    )
    draw_block(
        ax, xs[4], cy, w, h, "PROCESAMIENTO /\nTRANSMISIÓN",
        ["Microcontrolador /", "gateway edge", "dentro de la nacelle"],
    )
    draw_block(
        ax, xs[5], cy, w, h, "ALMACENAMIENTO\nFINAL",
        ["Archivo CSV /", "Base de datos", "(SCADA, local o nube)"],
    )

    for i in range(len(xs) - 1):
        draw_arrow(ax, (xs[i] + w / 2, cy), (xs[i + 1] - w / 2, cy))

    box_bottom = cy - h / 2

    # Riesgo 1: cableado analógico entre el sensor y el acondicionamiento
    mid_1 = (xs[1] + xs[2]) / 2
    draw_riesgo(
        ax, mid_1, box_bottom,
        "RIESGO 1:\ninterferencia electromagnética\nen el cableado analógico",
    )

    # Riesgo 2: en el propio ADC (aliasing / cuantización)
    draw_riesgo(
        ax, xs[3], box_bottom,
        "RIESGO 2:\naliasing o cuantización\ngruesa en el ADC",
    )

    ax.text(
        7.5, 0.15,
        "El ADC (digitalización) ocurre dentro de la góndola (nacelle), lo más cerca posible del sensor,\n"
        "para minimizar la longitud del cable analógico expuesto a ruido antes de convertir la señal a digital.",
        ha="center", va="bottom", fontsize=8.6, color=COLOR_TEXTO,
    )

    fig.tight_layout()
    return fig


def medir_altura_texto(fig, ax, text_obj):
    """Devuelve la altura real (en coordenadas de datos) que ocupa un texto
    ya renderizado, consultando el renderer de matplotlib. Esto evita tener
    que adivinar un espaciado fijo por línea (que se rompe apenas un párrafo
    tiene más o menos líneas de las esperadas)."""
    fig.canvas.draw()
    bbox = text_obj.get_window_extent(renderer=fig.canvas.get_renderer())
    (_, y0), (_, y1) = ax.transData.inverted().transform([(0, bbox.y0), (0, bbox.y1)])
    return abs(y1 - y0)


def draw_panel(fig, ax, x, y_top, w, titulo, items):
    """Panel de texto con encabezado oscuro (mismo estilo visual que las
    tablas de la práctica 3), para parámetros técnicos y riesgos. Calcula
    la altura del cuerpo dinámicamente según el texto real, para que nunca
    se superponga. Devuelve el borde inferior del panel."""
    header_h = 0.5
    top_body = y_top - header_h
    ty = top_body - 0.3

    for linea in items:
        negrita = linea.startswith("**")
        texto = linea.replace("**", "")
        text_obj = ax.text(x + 0.25, ty, texto, ha="left", va="top", fontsize=9.3,
                             fontweight="bold" if negrita else "normal",
                             color=COLOR_TEXTO, zorder=4)
        alto = medir_altura_texto(fig, ax, text_obj)
        ty -= alto + (0.12 if negrita else 0.32)

    bottom_body = ty + 0.12

    ax.add_patch(Rectangle((x, bottom_body), w, top_body - bottom_body,
                            linewidth=1.4, edgecolor=COLOR_BORDE,
                            facecolor=COLOR_PANEL_BODY, zorder=1))
    ax.add_patch(Rectangle((x, top_body), w, header_h, linewidth=1.4,
                            edgecolor=COLOR_BORDE, facecolor=COLOR_PANEL_HEAD,
                            zorder=1))
    ax.text(x + w / 2, top_body + header_h / 2, titulo, ha="center", va="center",
             fontsize=11, fontweight="bold", color="white", zorder=4)

    return bottom_body


def construir_pagina_parametros():
    fig, ax = plt.subplots(figsize=(13, 13))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 13)
    ax.axis("off")
    ax.set_title(
        "Parámetros técnicos y análisis de riesgos",
        fontsize=14, fontweight="bold", color=COLOR_TEXTO, pad=14,
    )

    y_cursor = draw_panel(
        fig, ax, x=0.5, y_top=12.3, w=12,
        titulo="Parámetros técnicos",
        items=[
            "**Frecuencia de muestreo: ≥ 2000 Hz (recomendado)**",
            "Por Nyquist, el mínimo teórico es 2× 200 Hz = 400 Hz para no perder\n"
            "información (evitar aliasing). Pero en monitoreo de condición estructural\n"
            "se recomienda un margen de 5-10× la frecuencia de interés, porque las\n"
            "fallas incipientes (grietas) generan armónicos en frecuencias más altas\n"
            "que la fundamental, y porque el análisis en ML se hace en el dominio de\n"
            "la frecuencia (FFT/espectrogramas), que necesita esa resolución extra.",
            "**Resolución: 16 a 24 bits**",
            "Cambios sutiles en la estructura (grietas incipientes) producen variaciones\n"
            "de amplitud muy pequeñas. Con pocos bits (ej. 8 bits = 256 niveles), esas\n"
            "variaciones quedan por debajo del error de cuantización y se pierden. Con\n"
            "16-24 bits el ruido de cuantización es lo bastante chico para no enmascarar\n"
            "la señal real (estándar en sistemas de monitoreo de condición - CMS).",
        ],
    )

    y_cursor -= 0.5

    y_cursor = draw_panel(
        fig, ax, x=0.5, y_top=y_cursor, w=12,
        titulo="Análisis de riesgos y su impacto en el modelo de ML",
        items=[
            "**Riesgo 1 - Interferencia electromagnética (cableado analógico)**",
            "Entre el sensor y la etapa de acondicionamiento, la señal todavía es\n"
            "analógica (voltaje) y viaja por cable dentro de la nacelle, cerca de\n"
            "motores, generador e inversores de potencia. Ese entorno induce ruido\n"
            "eléctrico que se suma a la señal real antes de digitalizarla.",
            "**Riesgo 2 - Aliasing o cuantización gruesa (en el ADC)**",
            "Si la frecuencia de muestreo es insuficiente para 200 Hz, aparecen\n"
            "frecuencias falsas (aliasing) que no existen en la vibración real. Si la\n"
            "resolución es baja, los cambios sutiles de amplitud se redondean y se\n"
            "pierden en el error de cuantización.",
            "**Impacto en el modelo de Machine Learning**",
            "\"Garbage in, garbage out\": el modelo entrena con lo que le llega, no con\n"
            "la vibración real de la pala. Ruido eléctrico → el modelo puede aprender a\n"
            "asociar ruido con falla (falsos positivos, alertas innecesarias). Aliasing o\n"
            "baja resolución → se pierde justo la señal sutil que anticipa una grieta\n"
            "(falsos negativos, no se detecta la falla real a tiempo). En un aerogenerador,\n"
            "un falso negativo puede terminar en una falla estructural catastrófica.",
        ],
    )

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig_diagrama = construir_diagrama()
    fig_diagrama.savefig("diagrama_daq_aerogenerador.png", dpi=200, bbox_inches="tight")

    fig_parametros = construir_pagina_parametros()

    with PdfPages("diseno_daq_aerogenerador.pdf") as pdf:
        pdf.savefig(fig_diagrama)
        pdf.savefig(fig_parametros)

    plt.close(fig_diagrama)
    plt.close(fig_parametros)
    print("Listo: diagrama_daq_aerogenerador.png y diseno_daq_aerogenerador.pdf generados.")
