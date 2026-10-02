"""
Pre-entrega 1 - Data Science II
Diseño de base de datos para el sistema de gestión de una biblioteca
universitaria (modelo Entidad-Relación, ya resuelto a nivel de tablas
relacionales con PK/FK, en Tercera Forma Normal).

Genera diagrama_er_biblioteca.png: el ERD detallado con tablas, campos,
claves primarias/foráneas y cardinalidad de cada relación.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

COLOR_BORDE = "#33475b"
COLOR_TEXTO = "#1b2733"
COLOR_TITULO = "#33475b"
COLOR_FILA = "#eef3f7"
COLOR_FILA_INTERMEDIA = "#fde9c8"
COLOR_LINEA = "#33475b"
COLOR_CARD = "#b03a2e"

FILA_H = 0.4


def dibujar_tabla(ax, cx, cy, w, titulo, columnas, color_titulo=COLOR_TITULO, color_fila=COLOR_FILA):
    """Dibuja una tabla relacional: encabezado + una fila por columna,
    marcando PK/FK a la derecha de cada campo. cy es el centro vertical."""
    h = FILA_H * (len(columnas) + 1)
    top = cy + h / 2

    ax.add_patch(Rectangle(
        (cx - w / 2, top - FILA_H), w, FILA_H,
        linewidth=1.6, edgecolor=COLOR_BORDE, facecolor=color_titulo, zorder=3,
    ))
    ax.text(cx, top - FILA_H / 2, titulo, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=4)

    y = top - FILA_H - FILA_H / 2
    for nombre, tipo, llave in columnas:
        ax.add_patch(Rectangle(
            (cx - w / 2, y - FILA_H / 2), w, FILA_H,
            linewidth=1.0, edgecolor=COLOR_BORDE, facecolor=color_fila, zorder=3,
        ))
        etiqueta = nombre if not llave else f"{nombre} ({llave})"
        ax.text(cx - w / 2 + 0.15, y, etiqueta, ha="left", va="center",
                fontsize=8.8, fontweight="bold" if "PK" in llave else "normal",
                color=COLOR_TEXTO, zorder=4)
        ax.text(cx + w / 2 - 0.15, y, tipo, ha="right", va="center",
                fontsize=7.8, style="italic", color="#5a6b7a", zorder=4)
        y -= FILA_H

    return {"cx": cx, "cy": cy, "w": w, "h": h, "top": top, "bottom": top - h}


def punto(tabla, lado, offset=0.0):
    if lado == "top":
        return (tabla["cx"] + offset, tabla["top"])
    if lado == "bottom":
        return (tabla["cx"] + offset, tabla["bottom"])
    if lado == "left":
        return (tabla["cx"] - tabla["w"] / 2, tabla["cy"] + offset)
    if lado == "right":
        return (tabla["cx"] + tabla["w"] / 2, tabla["cy"] + offset)
    raise ValueError(lado)


def conectar(ax, p1, p2, card1=None, card2=None):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLOR_LINEA, linewidth=1.3, zorder=2)
    if card1:
        lx = p1[0] + (p2[0] - p1[0]) * 0.12
        ly = p1[1] + (p2[1] - p1[1]) * 0.12
        ax.text(lx, ly, card1, fontsize=10, fontweight="bold", color=COLOR_CARD, zorder=5)
    if card2:
        lx = p1[0] + (p2[0] - p1[0]) * 0.88
        ly = p1[1] + (p2[1] - p1[1]) * 0.88
        ax.text(lx, ly, card2, fontsize=10, fontweight="bold", color=COLOR_CARD, zorder=5)


def construir_diagrama():
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_xlim(0, 15.5)
    ax.set_ylim(-0.6, 9.4)
    ax.axis("off")
    ax.set_title(
        "Diagrama Entidad-Relación · Biblioteca Universitaria",
        fontsize=15, fontweight="bold", color=COLOR_TEXTO, pad=16,
    )

    categorias = dibujar_tabla(
        ax, cx=2.4, cy=7.6, w=3.6, titulo="categorias",
        columnas=[
            ("id_categoria", "INT", "PK"),
            ("nombre_categoria", "VARCHAR(60)", ""),
        ],
    )
    libros = dibujar_tabla(
        ax, cx=7.7, cy=7.4, w=4.4, titulo="libros",
        columnas=[
            ("id_libro", "INT", "PK"),
            ("titulo", "VARCHAR(200)", ""),
            ("isbn", "VARCHAR(20)", ""),
            ("anio_publicacion", "INT", ""),
            ("id_categoria", "INT", "FK"),
        ],
    )
    autores = dibujar_tabla(
        ax, cx=13.1, cy=7.6, w=3.6, titulo="autores",
        columnas=[
            ("id_autor", "INT", "PK"),
            ("nombre", "VARCHAR(150)", ""),
            ("nacionalidad", "VARCHAR(60)", ""),
        ],
    )
    libro_autores = dibujar_tabla(
        ax, cx=10.4, cy=4.5, w=3.8, titulo="libro_autores",
        columnas=[
            ("id_libro", "INT", "PK, FK"),
            ("id_autor", "INT", "PK, FK"),
        ],
        color_titulo="#8a5a00", color_fila=COLOR_FILA_INTERMEDIA,
    )
    usuarios = dibujar_tabla(
        ax, cx=2.4, cy=1.9, w=3.8, titulo="usuarios",
        columnas=[
            ("id_usuario", "INT", "PK"),
            ("nombre", "VARCHAR(150)", ""),
            ("email", "VARCHAR(150)", ""),
            ("tipo_usuario", "VARCHAR(30)", ""),
            ("fecha_registro", "DATE", ""),
        ],
    )
    prestamos = dibujar_tabla(
        ax, cx=8.0, cy=1.9, w=4.6, titulo="prestamos",
        columnas=[
            ("id_prestamo", "INT", "PK"),
            ("id_usuario", "INT", "FK"),
            ("id_libro", "INT", "FK"),
            ("fecha_prestamo", "DATE", ""),
            ("fecha_devolucion_estimada", "DATE", ""),
            ("fecha_devolucion_real", "DATE", ""),
        ],
    )

    # categorias 1---N libros
    conectar(ax, punto(categorias, "right"), punto(libros, "left", offset=-0.9),
             card1="1", card2="N")

    # libros 1---N libro_autores  y  autores 1---N libro_autores  (resuelven N:M)
    conectar(ax, punto(libros, "bottom", offset=1.8), punto(libro_autores, "top", offset=-1.2),
             card1="1", card2="N")
    conectar(ax, punto(autores, "bottom"), punto(libro_autores, "top", offset=1.2),
             card1="1", card2="N")

    # usuarios 1---N prestamos
    conectar(ax, punto(usuarios, "right"), punto(prestamos, "left", offset=0.6),
             card1="1", card2="N")

    # libros 1---N prestamos
    conectar(ax, punto(libros, "bottom", offset=-0.6), punto(prestamos, "top", offset=0.4),
             card1="1", card2="N")

    ax.text(
        7.7, -0.3,
        "1 Categoría agrupa N Libros  ·  N Libros y M Autores se resuelven con la tabla intermedia libro_autores (N:M)\n"
        "1 Usuario realiza N Préstamos  ·  1 Libro puede tener N Préstamos a lo largo del tiempo",
        ha="center", va="bottom", fontsize=9, color=COLOR_TEXTO,
    )

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = construir_diagrama()
    fig.savefig("diagrama_er_biblioteca.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Listo: diagrama_er_biblioteca.png generado.")
