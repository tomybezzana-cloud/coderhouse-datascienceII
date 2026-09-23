"""
Ejecuta los scripts .sql de esta práctica contra practica_tcl.db y muestra
el resultado de cada SELECT, para poder comprobar en la consola que el
COMMIT y los ROLLBACK se comportan como dicen los comentarios de cada
archivo.

Se usa isolation_level=None (modo autocommit de Python) para que el propio
BEGIN/COMMIT/ROLLBACK escrito en el .sql sea el que controla la transacción,
en vez de que el módulo sqlite3 abra una transacción implícita por su cuenta.

Igual que la consola oficial `sqlite3`, si una sentencia falla se informa el
error y se sigue con la siguiente (así el ROLLBACK del Caso 3 se ejecuta
después del error, en vez de cortar el script entero).
"""

import sqlite3
from pathlib import Path

CARPETA = Path(__file__).parent
BASE_DE_DATOS = CARPETA / "practica_tcl.db"


def dividir_en_sentencias(texto_sql):
    """Quita las líneas de comentario (--) y separa el resto en sentencias
    individuales usando ';' como delimitador."""
    lineas_utiles = [
        linea for linea in texto_sql.splitlines()
        if not linea.strip().startswith("--") and linea.strip() != ""
    ]
    cuerpo = "\n".join(lineas_utiles)
    sentencias = [s.strip() for s in cuerpo.split(";")]
    return [s for s in sentencias if s]


def ejecutar_archivo(cursor, ruta):
    print(f"\n{'=' * 70}\n{ruta.name}\n{'=' * 70}")
    texto = ruta.read_text(encoding="utf-8")

    for sentencia in dividir_en_sentencias(texto):
        try:
            cursor.execute(sentencia)
            if sentencia.strip().upper().startswith("SELECT"):
                columnas = [d[0] for d in cursor.description]
                filas = cursor.fetchall()
                print(f"\n>> {sentencia}")
                print("   " + " | ".join(columnas))
                for fila in filas:
                    print("   " + " | ".join(str(v) for v in fila))
            else:
                print(f"\n>> {sentencia}   [OK]")
        except sqlite3.Error as error:
            print(f"\n>> {sentencia}")
            print(f"   [ERROR] {error}")


def main():
    conexion = sqlite3.connect(BASE_DE_DATOS, isolation_level=None)
    cursor = conexion.cursor()

    ejecutar_archivo(cursor, CARPETA / "schema.sql")
    ejecutar_archivo(cursor, CARPETA / "caso1_transaccion_exitosa.sql")
    ejecutar_archivo(cursor, CARPETA / "caso2_boton_panico.sql")
    ejecutar_archivo(cursor, CARPETA / "caso3_atomicidad_fallo.sql")

    conexion.close()


if __name__ == "__main__":
    main()
