"""
Práctica de repaso de modelado de bases de datos - Data Science II
Objetivo: traducir un problema real (plataforma de cursos online) a un
esquema de base de datos, mediante un diagrama Entidad-Relación (Chen) y
su conversión a tablas relacionales.

Este script genera dos archivos a partir del mismo diseño:
  - diagrama_er_cursos.png  -> solo el diagrama ER (para subir como imagen)
  - diseno_bd_cursos.pdf    -> diagrama ER + conversión a tablas (2 páginas)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages

# Paleta simple y con buen contraste en fondo claro.
COLOR_ENTIDAD = "#dbe9f6"
COLOR_RELACION = "#fde9c8"
COLOR_BORDE = "#33475b"
COLOR_TEXTO = "#1b2733"
COLOR_TABLA = "#eef3f7"


def draw_entity(ax, cx, cy, w, h, titulo, atributos, pk_index=0):
    """Dibuja una entidad (rectángulo) con su nombre y sus atributos.
    El atributo en pk_index se marca como Clave Primaria (PK)."""
    rect = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=COLOR_BORDE, facecolor=COLOR_ENTIDAD,
        zorder=3,
    )
    ax.add_patch(rect)
    ax.text(cx, cy + h / 2 - 0.28, titulo, ha="center", va="top",
             fontsize=12, fontweight="bold", color=COLOR_TEXTO, zorder=4)
    ax.plot([cx - w / 2 + 0.15, cx + w / 2 - 0.15],
             [cy + h / 2 - 0.5, cy + h / 2 - 0.5],
             color=COLOR_BORDE, linewidth=0.8, zorder=4)

    y = cy + h / 2 - 0.78
    for i, attr in enumerate(atributos):
        etiqueta = attr
        peso = "normal"
        if i == pk_index:
            etiqueta = f"{attr} (PK)"
            peso = "bold"
        ax.text(cx, y, etiqueta, ha="center", va="top", fontsize=9.3,
                 fontweight=peso, color=COLOR_TEXTO, zorder=4)
        y -= 0.32
    return (cx - w / 2, cy), (cx + w / 2, cy), (cx, cy - h / 2), (cx, cy + h / 2)


def draw_relationship(ax, cx, cy, w, h, titulo, atributos=None):
    """Dibuja una relación (rombo) con su nombre."""
    puntos = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    rombo = Polygon(puntos, closed=True, linewidth=1.6,
                     edgecolor=COLOR_BORDE, facecolor=COLOR_RELACION, zorder=3)
    ax.add_patch(rombo)
    ax.text(cx, cy, titulo, ha="center", va="center", fontsize=9.5,
             fontweight="bold", color=COLOR_TEXTO, zorder=4)

    if atributos:
        y = cy - h / 2 - 0.28
        for attr in atributos:
            ax.text(cx, y, attr, ha="center", va="top", fontsize=8.3,
                     style="italic", color=COLOR_TEXTO, zorder=4)
            y -= 0.28
    return (cx - w / 2, cy), (cx + w / 2, cy), (cx, cy - h / 2), (cx, cy + h / 2)


def connect(ax, p1, p2, label_p1=None, label_p2=None):
    """Une dos puntos con una línea recta y etiqueta la cardinalidad
    cerca de cada extremo."""
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_BORDE,
             linewidth=1.4, zorder=2)
    if label_p1:
        lx = p1[0] + (p2[0] - p1[0]) * 0.18
        ly = p1[1] + (p2[1] - p1[1]) * 0.18 + 0.18
        ax.text(lx, ly, label_p1, fontsize=10, fontweight="bold",
                 color="#b03a2e", zorder=5)
    if label_p2:
        lx = p1[0] + (p2[0] - p1[0]) * 0.82
        ly = p1[1] + (p2[1] - p1[1]) * 0.82 + 0.18
        ax.text(lx, ly, label_p2, fontsize=10, fontweight="bold",
                 color="#b03a2e", zorder=5)


def construir_diagrama_er():
    """Construye la figura del diagrama Entidad-Relación (notación Chen):
    rectángulos = entidades, rombos = relaciones, con cardinalidad 1:N / N:M."""
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5.1)
    ax.axis("off")
    ax.set_title(
        "Diagrama Entidad-Relación · Plataforma de Cursos Online",
        fontsize=14, fontweight="bold", color=COLOR_TEXTO, pad=14,
    )

    cy = 3.5

    # Entidades
    _, inst_der, _, _ = draw_entity(
        ax, cx=2.0, cy=cy, w=3.0, h=2.2,
        titulo="INSTRUCTORES",
        atributos=["id_instructor", "nombre", "email", "especialidad"],
    )
    curso_izq, curso_der, curso_abajo, _ = draw_entity(
        ax, cx=6.5, cy=cy, w=3.0, h=2.2,
        titulo="CURSOS",
        atributos=["id_curso", "titulo", "precio", "id_instructor (FK)"],
    )
    est_izq, _, est_arriba, _ = draw_entity(
        ax, cx=11.0, cy=cy, w=3.0, h=2.2,
        titulo="ESTUDIANTES",
        atributos=["id_estudiante", "nombre", "email", "fecha_registro"],
    )

    # Relación 1:N entre Instructores y Cursos
    dicta_izq, dicta_der, _, _ = draw_relationship(
        ax, cx=4.25, cy=cy, w=1.6, h=1.0, titulo="DICTA",
    )
    connect(ax, inst_der, dicta_izq, label_p1="1")
    connect(ax, dicta_der, curso_izq, label_p2="N")

    # Relación N:M entre Cursos y Estudiantes (con atributos propios)
    insc_izq, insc_der, _, _ = draw_relationship(
        ax, cx=8.75, cy=cy, w=1.6, h=1.0, titulo="SE\nINSCRIBE",
        atributos=["fecha_inscripcion", "calificacion"],
    )
    connect(ax, curso_der, insc_izq, label_p1="N")
    connect(ax, insc_der, est_izq, label_p2="M")

    ax.text(
        6.5, 1.55,
        "Lectura: 1 Instructor dicta N Cursos  ·  N Cursos se relacionan con M Estudiantes "
        "(y viceversa) a través de la inscripción.\n"
        "La relación N:M lleva atributos propios (fecha_inscripcion, calificacion) "
        "→ por eso necesita su propia tabla intermedia (ver Tabla: inscripciones).",
        ha="center", va="top", fontsize=9, color=COLOR_TEXTO,
    )

    fig.tight_layout()
    return fig


def dibujar_tabla(ax, cx, cy, w, titulo, columnas, subtitulo=None):
    """Dibuja el bloque visual de una tabla relacional (Paso 3)."""
    fila_h = 0.42
    h = fila_h * (len(columnas) + 1)
    ax.add_patch(Rectangle(
        (cx - w / 2, cy + h / 2 - fila_h), w, fila_h,
        linewidth=1.6, edgecolor=COLOR_BORDE, facecolor=COLOR_BORDE, zorder=3,
    ))
    ax.text(cx, cy + h / 2 - fila_h / 2, titulo, ha="center", va="center",
             fontsize=10.5, fontweight="bold", color="white", zorder=4)

    y = cy + h / 2 - fila_h - fila_h / 2
    for nombre, tipo in columnas:
        ax.add_patch(Rectangle(
            (cx - w / 2, y - fila_h / 2), w, fila_h,
            linewidth=1.0, edgecolor=COLOR_BORDE, facecolor=COLOR_TABLA, zorder=3,
        ))
        ax.text(cx - w / 2 + 0.15, y, nombre, ha="left", va="center",
                 fontsize=9, fontweight="bold" if "PK" in tipo else "normal",
                 color=COLOR_TEXTO, zorder=4)
        ax.text(cx + w / 2 - 0.15, y, tipo, ha="right", va="center",
                 fontsize=8.3, style="italic", color="#5a6b7a", zorder=4)
        y -= fila_h

    if subtitulo:
        ax.text(cx, cy - h / 2 - 0.22, subtitulo, ha="center", va="top",
                 fontsize=8, color="#5a6b7a")


def construir_pagina_tablas():
    """Construye la figura con la conversión del diagrama ER a tablas
    relacionales (Paso 3), marcando PK y FK."""
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    ax.set_title(
        "Conversión a tablas relacionales",
        fontsize=14, fontweight="bold", color=COLOR_TEXTO, pad=14,
    )

    dibujar_tabla(
        ax, cx=2.1, cy=5.1, w=3.6, titulo="instructores",
        columnas=[
            ("id_instructor", "PK"),
            ("nombre", ""),
            ("email", ""),
            ("especialidad", ""),
        ],
    )
    dibujar_tabla(
        ax, cx=6.5, cy=5.1, w=3.8, titulo="cursos",
        columnas=[
            ("id_curso", "PK"),
            ("titulo", ""),
            ("precio", ""),
            ("id_instructor", "FK"),
        ],
        subtitulo="id_instructor → instructores.id_instructor",
    )
    dibujar_tabla(
        ax, cx=11.0, cy=5.1, w=3.6, titulo="estudiantes",
        columnas=[
            ("id_estudiante", "PK"),
            ("nombre", ""),
            ("email", ""),
            ("fecha_registro", ""),
        ],
    )
    dibujar_tabla(
        ax, cx=6.5, cy=1.9, w=5.4, titulo="inscripciones  (tabla intermedia N:M)",
        columnas=[
            ("id_inscripcion", "PK"),
            ("id_estudiante", "FK"),
            ("id_curso", "FK"),
            ("fecha_inscripcion", ""),
            ("calificacion", ""),
        ],
        subtitulo=(
            "id_estudiante → estudiantes.id_estudiante   ·   "
            "id_curso → cursos.id_curso"
        ),
    )

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig_er = construir_diagrama_er()
    fig_er.savefig("diagrama_er_cursos.png", dpi=200, bbox_inches="tight")

    fig_tablas = construir_pagina_tablas()

    with PdfPages("diseno_bd_cursos.pdf") as pdf:
        pdf.savefig(fig_er)
        pdf.savefig(fig_tablas)

    plt.close(fig_er)
    plt.close(fig_tablas)
    print("Listo: diagrama_er_cursos.png y diseno_bd_cursos.pdf generados.")
