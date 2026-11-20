# Mapeo ORM con SQLAlchemy 2.0: tracking de un proyecto de Data Science

**Autor:** Tomás Bezzana

Un sistema de tracking mínimo para registrar los **datasets** que procesa un
proyecto y los **experimentos de modelos** que se entrenan. Las tablas no se crean
con SQL escrito a mano: se definen como clases de Python con el mapeo declarativo
de SQLAlchemy 2.0, y el ORM las traduce a tablas.

## Archivos

| Archivo | Qué contiene |
|---------|--------------|
| [`models.py`](models.py) | La clase `Base` y las entidades `Dataset` y `ModelExperiment` |
| [`main.py`](main.py) | Crea `analytics.db`, muestra el SQL generado, verifica las tablas en el archivo e instancia un objeto de cada clase |
| [`requirements.txt`](requirements.txt) | Dependencia: SQLAlchemy 2.x |

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate             # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

El script genera `analytics.db` en esta carpeta. Se puede correr varias veces:
`create_all` solo crea las tablas que todavía no existen. El `.db` no se sube al
repo porque lo regenera el script.

## Qué representa el modelo

```
datasets                          model_experiments
─────────────────────────────     ─────────────────────────────
id          INTEGER  PK           id              INTEGER  PK
name        VARCHAR(100) UNIQUE   algorithm_name  VARCHAR(50)
source_url  VARCHAR(255) NULL     accuracy        FLOAT
num_rows    INTEGER               is_deployed     BOOLEAN
```

- **`Dataset`** (`datasets`): cada fuente de datos que entra al pipeline. Guarda su
  nombre (único, para no registrar el mismo dataset dos veces), de dónde se bajó y
  cuántas filas tiene. `source_url` es opcional porque un dataset armado a mano
  puede no tener URL.
- **`ModelExperiment`** (`model_experiments`): cada entrenamiento. Guarda qué
  algoritmo se usó, qué accuracy obtuvo y si el modelo está en producción.

## Cómo funciona el mapeo

```python
class Base(DeclarativeBase):
    pass

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    source_url: Mapped[str | None] = mapped_column(String(255))
    num_rows: Mapped[int] = mapped_column(Integer)
```

- **`Base(DeclarativeBase)`:** todas las entidades heredan de ella. `Base.metadata`
  junta la definición de todas las tablas, y eso es lo que recorre `create_all()`.
- **`__tablename__`:** el nombre de la tabla en SQL.
- **`Mapped[...]`:** el tipo Python de la columna. Además define si la columna
  admite nulos: `Mapped[int]` se crea `NOT NULL` y `Mapped[str | None]` acepta
  `NULL`. No hace falta escribir `nullable=` a mano.
- **`mapped_column(...)`:** las restricciones. `primary_key=True`, el largo de
  `String(100)`, `unique=True` y `default=False`.

Las columnas cubren los tres tipos pedidos: `String` (`name`, `source_url`,
`algorithm_name`), `Integer` (`id`, `num_rows`), `Float` (`accuracy`) y `Boolean`
(`is_deployed`).

## Qué muestra `main.py`

1. **El SQL que genera el ORM a partir de cada clase.** Es la traducción objeto →
   tabla:

   ```sql
   CREATE TABLE model_experiments (
       id INTEGER NOT NULL,
       algorithm_name VARCHAR(50) NOT NULL,
       accuracy FLOAT NOT NULL,
       is_deployed BOOLEAN NOT NULL,
       PRIMARY KEY (id)
   )
   ```

2. **Las tablas leídas directamente de `analytics.db`** con `inspect(engine)`. Así
   se comprueba que el archivo `.db` es real y tiene el esquema esperado, sin
   depender de las clases de Python.

3. **Un objeto de cada clase:**

   ```
   Dataset(id=None, name='hotel_bookings', source_url='https://www.kaggle.com/...', num_rows=119390)
   ModelExperiment(id=None, algorithm_name='RandomForestClassifier', accuracy=0.87, is_deployed=False)
   ```

   El `id` es `None` porque los objetos todavía no se guardaron: el id lo asigna la
   base al insertar la fila, cosa que se hará con una `Session` en el próximo paso.

## Errores comunes evitados

- **Olvidar `__tablename__`.** Ambas clases lo definen. Si falta, SQLAlchemy falla
  en el momento de definir la clase, antes de llegar a la base:
  `InvalidRequestError: Class ... does not have a __table__ or __tablename__ specified`.
- **Mezclar estilos.** No se usa `Column()` (estilo 1.x) en ningún lugar: todas las
  columnas se declaran con `Mapped` + `mapped_column`, y la base hereda de
  `DeclarativeBase` en lugar de usar `declarative_base()`.
