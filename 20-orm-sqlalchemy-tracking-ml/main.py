"""
Inicializa la base de datos del sistema de tracking y prueba el mapeo ORM.
Autor: Tomás Bezzana

Uso (con el entorno virtual activado):
    python main.py

Genera analytics.db en esta misma carpeta.
"""

import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateTable

from models import Base, Dataset, ModelExperiment

# La base queda junto a este archivo, sin importar desde qué carpeta se ejecute
# el script. Es equivalente a create_engine("sqlite:///analytics.db") corrido
# desde esta carpeta.
RUTA_DB = Path(__file__).resolve().parent / "analytics.db"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # 1. El engine es la conexión con la base. Con SQLite, si el archivo no
    #    existe se crea en la primera conexión.
    engine = create_engine(f"sqlite:///{RUTA_DB.as_posix()}")

    # 2. create_all recorre Base.metadata (todas las clases que heredan de
    #    Base) y ejecuta un CREATE TABLE por cada tabla que todavía no exista.
    #    Si ya existen no las toca, así que se puede correr varias veces.
    Base.metadata.create_all(engine)
    print(f"Base de datos creada: {RUTA_DB.name}\n")

    # 3. Traducción objeto -> tabla: el SQL que SQLAlchemy genera a partir de
    #    cada clase.
    print("=== SQL generado a partir de las clases ===")
    for tabla in Base.metadata.sorted_tables:
        print(str(CreateTable(tabla).compile(engine)).strip(), end="\n\n")

    # 4. Verificación sobre el archivo .db real: se leen las tablas y columnas
    #    directamente de la base, no de las clases de Python.
    print("=== Tablas encontradas en analytics.db ===")
    inspector = inspect(engine)
    for nombre in inspector.get_table_names():
        print(f"{nombre}:")
        for col in inspector.get_columns(nombre):
            nulo = "NULL" if col["nullable"] else "NOT NULL"
            print(f"  - {col['name']:<15} {str(col['type']):<13} {nulo}")
    print()

    # 5. Prueba de concepto: instanciar un objeto de cada clase. Son objetos
    #    Python comunes; todavía no se guardan en la base (para eso hace falta
    #    una Session). Por eso id es None: lo asigna la base al insertar.
    print("=== Objetos instanciados ===")
    dataset = Dataset(
        name="hotel_bookings",
        source_url="https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand",
        num_rows=119_390,
    )
    experimento = ModelExperiment(
        algorithm_name="RandomForestClassifier",
        accuracy=0.87,
        is_deployed=False,
    )
    print(dataset)
    print(experimento)

    # El atributo de la clase sabe a qué tabla y columna corresponde.
    print(f"\nDataset.num_rows        -> columna {Dataset.num_rows.expression}")
    print(f"ModelExperiment.accuracy -> columna {ModelExperiment.accuracy.expression}")

    engine.dispose()


if __name__ == "__main__":
    main()
