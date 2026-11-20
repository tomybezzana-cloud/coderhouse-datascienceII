"""
Modelos ORM del sistema de tracking de un proyecto de Data Science.
Autor: Tomás Bezzana

Cada clase es una tabla y cada atributo, una columna. Se usa solo el estilo
declarativo de SQLAlchemy 2.0:
  - Mapped[...]      -> el tipo Python de la columna. Si NO es opcional
                        (Mapped[int]) la columna se crea NOT NULL; con
                        Mapped[str | None] admite NULL.
  - mapped_column()  -> las restricciones: clave primaria, largo del texto,
                        unicidad, valor por defecto, etc.
No se usa Column() (estilo 1.x) en ningún lugar.
"""

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Clase base de todas las entidades.

    Junta en Base.metadata la definición de todas las tablas que heredan de
    ella, y eso es lo que usa create_all() para crearlas en la base.
    """


class Dataset(Base):
    """Un dataset que el proyecto procesa."""

    # Nombre de la tabla en SQL. Sin esto SQLAlchemy no sabe qué tabla crear
    # y lanza un error al definir la clase.
    __tablename__ = "datasets"

    # Integer + primary_key: en SQLite la base asigna el id sola (1, 2, 3...).
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # String(100): texto de hasta 100 caracteres. unique=True impide registrar
    # dos datasets con el mismo nombre.
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # Opcional: un dataset generado a mano puede no tener URL de origen.
    source_url: Mapped[str | None] = mapped_column(String(255))

    num_rows: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return (f"Dataset(id={self.id}, name={self.name!r}, "
                f"source_url={self.source_url!r}, num_rows={self.num_rows})")


class ModelExperiment(Base):
    """Un experimento de entrenamiento: qué algoritmo se usó y cómo le fue."""

    __tablename__ = "model_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    algorithm_name: Mapped[str] = mapped_column(String(50))

    # Float: la métrica es un número decimal entre 0 y 1.
    accuracy: Mapped[float] = mapped_column(Float)

    # Boolean: si el modelo está en producción. default=False lo completa
    # SQLAlchemy al INSERTAR la fila si no se indicó otro valor.
    is_deployed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return (f"ModelExperiment(id={self.id}, algorithm_name={self.algorithm_name!r}, "
                f"accuracy={self.accuracy}, is_deployed={self.is_deployed})")
