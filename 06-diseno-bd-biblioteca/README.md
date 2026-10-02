# Pre-entrega 1: Diseño de base de datos para una biblioteca universitaria

Archivos entregables:

- [`diagrama_er_biblioteca.png`](diagrama_er_biblioteca.png) — diagrama Entidad-Relación (entregable pedido).
- [`generar_diagrama.py`](generar_diagrama.py) — script que genera el PNG con `matplotlib`.

## Caso de estudio

La biblioteca migra sus registros desde hojas de cálculo, donde tenía dos
problemas típicos de un modelo no relacional:

- **Redundancia**: los datos del autor (nombre, nacionalidad) se repetían en
  cada fila por cada libro que escribía.
- **Inconsistencia**: la categoría de cada libro se cargaba como texto libre,
  con errores de tipeo (`"Ciencia Ficcion"`, `"cs ficcion"`, `"Cs. Ficción"`
  refiriéndose a lo mismo).

El diseño resuelve ambos problemas normalizando `autores` y `categorias`
como tablas propias, referenciadas por clave foránea en vez de texto
repetido.

## Paso 1: Entidades y atributos

| Entidad | Atributos | PK |
|---|---|---|
| **categorias** | `id_categoria`, `nombre_categoria` | `id_categoria` |
| **libros** | `id_libro`, `titulo`, `isbn`, `anio_publicacion`, `id_categoria` (FK) | `id_libro` |
| **autores** | `id_autor`, `nombre`, `nacionalidad` | `id_autor` |
| **libro_autores** (tabla intermedia N:M) | `id_libro` (FK), `id_autor` (FK) | `(id_libro, id_autor)` compuesta |
| **usuarios** | `id_usuario`, `nombre`, `email`, `tipo_usuario`, `fecha_registro` | `id_usuario` |
| **prestamos** | `id_prestamo`, `id_usuario` (FK), `id_libro` (FK), `fecha_prestamo`, `fecha_devolucion_estimada`, `fecha_devolucion_real` | `id_prestamo` |

Son 6 tablas en total: las 4 entidades principales sugeridas por la consigna
(**Libros**, **Autores**, **Usuarios**, **Préstamos**) más 2 tablas que
aparecen como consecuencia de normalizar: `categorias` (para no repetir ni
tipear mal el nombre de categoría en cada libro) y `libro_autores` (para
resolver la relación N:M entre libros y autores).

## Paso 2: Relaciones y cardinalidad

- **categorias → libros (1:N)**: una categoría agrupa muchos libros, cada
  libro pertenece a una sola categoría. Se resuelve con `id_categoria` como
  FK en `libros`.
- **libros ↔ autores (N:M)**: un libro puede tener varios autores (por
  ejemplo, una obra en coautoría) y un autor puede haber escrito varios
  libros. Al ser N:M, no se puede resolver con una FK simple en ninguna de
  las dos tablas, así que se crea la tabla intermedia **`libro_autores`**,
  con FK hacia ambas y PK compuesta por las dos.
- **usuarios → prestamos (1:N)**: un usuario puede tener muchos préstamos a
  lo largo del tiempo, pero cada préstamo pertenece a un único usuario. FK
  `id_usuario` en `prestamos`.
- **libros → prestamos (1:N)**: un libro puede prestarse muchas veces (en
  distintos momentos), pero cada fila de `prestamos` referencia a un único
  libro. FK `id_libro` en `prestamos`.

## Paso 3: Normalización (3FN)

- **1FN**: todos los atributos son atómicos (por ejemplo, no hay una columna
  `autores` con varios nombres separados por coma dentro de `libros`; para
  eso está `libro_autores`).
- **2FN**: la única tabla con clave compuesta es `libro_autores`, y no tiene
  ningún atributo extra que dependa solo de una parte de la clave (no hay
  dependencias parciales).
- **3FN**: no quedan dependencias transitivas. `nombre_categoria` no se
  guarda en `libros` (se accede vía `id_categoria` → `categorias`), y los
  datos del autor no se guardan en `libros` ni se repiten por cada libro
  (se accede vía `libro_autores` → `autores`). Esto es justamente lo que
  elimina la redundancia y la inconsistencia del problema original.

## Cómo regenerar el diagrama

```bash
python generar_diagrama.py
```
