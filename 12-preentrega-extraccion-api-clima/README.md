# Práctica 12 (Pre-entrega 4): Extracción y Almacenamiento Seguro de Datos vía API

Script en Python que consulta la API pública de
[Open-Meteo](https://open-meteo.com) para obtener el **pronóstico diario del
clima** de varias ciudades argentinas, limpia la respuesta JSON y la guarda en
un **CSV**.

La configuración se maneja con variables de entorno (archivo `.env`, que no se
sube al repo) y el script maneja errores HTTP, timeouts y fallas de conexión
sin cortarse de golpe.

Archivos:

- [`extraccion_api_clima.py`](extraccion_api_clima.py): el script de extracción, transformación y guardado.
- [`data_extracted.csv`](data_extracted.csv): el archivo de salida (35 filas: 5 ciudades × 7 días, extraído el 25/10/2026).
- [`.env.example`](.env.example): plantilla de configuración. Se copia como `.env`.
- [`requirements.txt`](requirements.txt): las librerías necesarias.
- [`../.gitignore`](../.gitignore): excluye `.env`, `__pycache__/` y otros archivos que no van al repo.

## ¿Por qué Open-Meteo?

Es gratuita, no pide registro y devuelve datos reales y actualizados. Como no
usa API key, el `.env` guarda la **configuración** (URL, ciudades, días,
timeout). Igual tiene una variable `API_KEY`: si se cambia a una API que la
pida (por ejemplo OpenWeather), alcanza con completarla en el `.env` sin tocar
el código. El script la envía solo si tiene valor.

## Librerías necesarias

| Librería | Para qué se usa |
|----------|-----------------|
| `requests` | Peticiones GET a la API |
| `python-dotenv` | Carga las variables del archivo `.env` |
| `truststore` *(opcional)* | Hace que Python confíe en los certificados de Windows/macOS (ver [Problemas frecuentes](#problemas-frecuentes)) |

El CSV se escribe con el módulo `csv` de la librería estándar.

Probado con Python 3.13, requests 2.34.2, python-dotenv 1.2.4 y truststore 0.10.4.

## Instalación y ejecución

```bash
# 1. (Opcional) crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear el archivo de configuración a partir de la plantilla
cp .env.example .env             # Windows: copy .env.example .env

# 4. Ejecutar
python extraccion_api_clima.py
```

El script imprime cada etapa y deja el resultado en `data_extracted.csv`.
Si algo falla, muestra un mensaje claro y termina con código de salida 1.

### Variables del `.env`

| Variable | Obligatoria | Ejemplo | Descripción |
|---|---|---|---|
| `API_BASE_URL` | Sí | `https://api.open-meteo.com/v1/forecast` | Endpoint de la API |
| `API_KEY` | No | *(vacía)* | Se envía como parámetro `apikey` solo si tiene valor |
| `CIUDADES` | Sí | `Buenos Aires,Córdoba,Rosario` | Separadas por coma. Disponibles: Buenos Aires, Córdoba, Rosario, Mendoza, Bariloche, Salta, Ushuaia |
| `DIAS_PRONOSTICO` | No (7) | `7` | Entre 1 y 16 |
| `TIMEOUT_SEGUNDOS` | No (10) | `10` | Espera máxima por petición |

## Qué hace el script, paso a paso

### 1. Configuración

`load_dotenv()` lee el `.env` y el script toma los valores con `os.getenv`.
Antes de hacer cualquier petición valida que:

- el `.env` exista (si no, avisa que hay que copiar `.env.example`);
- `API_BASE_URL` no esté vacía;
- `DIAS_PRONOSTICO` y `TIMEOUT_SEGUNDOS` sean números, y los días estén en
  rango;
- haya al menos una ciudad conocida. Las desconocidas se avisan y se omiten.

### 2. Extracción

Una petición GET por ciudad con `requests.get(..., params=..., timeout=...)`.

| Situación | Qué hace el script |
|---|---|
| `200 OK` | Parsea el JSON (si no es JSON válido, lo informa) |
| `404 Not Found` | Avisa que el endpoint no existe y sugiere revisar `API_BASE_URL` |
| `401` / `403` | Avisa que el acceso fue denegado y sugiere revisar `API_KEY` |
| Otro `4xx` | Muestra el motivo que devuelve la API (campo `reason`) |
| `5xx` (servidor caído o con errores) | **Reintenta** hasta 3 veces, esperando 2 y 4 s entre intentos |
| Timeout | También reintenta, porque puede ser algo temporal |
| Sin conexión / DNS | Informa que no hay conexión con la API |
| Certificado SSL no verificable | Sugiere instalar `truststore` |

Los errores se convierten en una excepción propia (`ErrorExtraccion`) con un
mensaje legible. Si falla una ciudad, se informa y **se sigue con las demás**.
Solo si no se obtuvo ningún dato el script termina sin generar el CSV.

### 3. Transformación

La API devuelve metadatos que no interesan (`generationtime_ms`, `elevation`,
`utc_offset_seconds`, `daily_units`...) y los datos diarios en formato
**columnar** (una lista por variable):

```json
"daily": {
  "time": ["2026-10-25", "2026-10-26"],
  "temperature_2m_max": [17.0, 16.8],
  ...
}
```

El script descarta los metadatos, agrega el nombre de la ciudad y pasa los
datos a **una fila por ciudad y día**, con nombres de columna en castellano.

### 4. Persistencia

`csv.DictWriter` escribe `data_extracted.csv` en UTF-8. Si no se puede
escribir el archivo (por ejemplo, porque está abierto en Excel), el script lo
informa en lugar de cortarse.

## Archivo de salida

`data_extracted.csv`, una fila por ciudad y día:

| Columna | Descripción |
|---|---|
| `ciudad` | Nombre de la ciudad |
| `fecha` | Fecha del pronóstico (`AAAA-MM-DD`, hora de Argentina) |
| `temp_max_c` | Temperatura máxima (°C) |
| `temp_min_c` | Temperatura mínima (°C) |
| `precipitacion_mm` | Precipitación total del día (mm) |
| `prob_precipitacion_pct` | Probabilidad máxima de precipitación (%) |
| `viento_max_kmh` | Velocidad máxima del viento a 10 m (km/h) |

Ejemplo:

```
ciudad,fecha,temp_max_c,temp_min_c,precipitacion_mm,prob_precipitacion_pct,viento_max_kmh
Buenos Aires,2026-10-25,17.0,11.0,0.3,37,16.4
Buenos Aires,2026-10-26,16.8,8.3,0.0,2,15.1
```

Como es un pronóstico, al volver a correr el script los valores cambian.

## Pruebas de manejo de errores

Se probó cada caso modificando el `.env`:

| Cambio en el `.env` | Salida del script |
|---|---|
| `API_BASE_URL=https://api.open-meteo.com/v1/noexiste` | `[error] Buenos Aires: 404: el endpoint no existe, revisá API_BASE_URL (...)` |
| `CIUDADES=Rosario,Narnia` | `[aviso] Ciudad 'Narnia' sin coordenadas cargadas: se omite.` |
| Parámetro inválido en la URL | `[error] Rosario: 400: petición inválida (Invalid value: ...)` |
| `API_BASE_URL=https://host-que-no-existe.invalid/v1` | `[error] Buenos Aires: no se pudo conectar con la API (¿hay conexión a internet?)` |
| `TIMEOUT_SEGUNDOS=0.001` | Dos `[reintento]` y luego `[error] Salta: la API no respondió en 0.001 s, después de 3 intentos` |
| Sin archivo `.env` | `[error] No se encontró .env. Copiá .env.example como .env y completá los valores.` |

En ningún caso se muestra un traceback: el script termina con un mensaje y
código de salida 1.

## Problemas frecuentes

**`no se pudo verificar el certificado SSL`**: pasa cuando un antivirus (por
ejemplo Avast) o un proxy corporativo inspecciona el tráfico HTTPS con su
propio certificado. `requests` no confía en ese certificado. Solución:

```bash
pip install truststore
```

Si `truststore` está instalado, el script lo activa solo y Python pasa a usar
los certificados del sistema operativo. **No** conviene desactivar la
verificación con `verify=False`, porque deja la conexión expuesta.

## Checklist de la consigna

1. **README con instrucciones de configuración y ejecución**: este archivo.
2. **Petición exitosa a una API externa**: `requests.get` a Open-Meteo, 5
   ciudades × 7 días recuperados.
3. **Variables de entorno con `.env`**: `python-dotenv` carga la configuración
   (y la API key, si hiciera falta). El `.env` está en el `.gitignore` y se
   sube solo `.env.example` como plantilla.
4. **Datos guardados en un archivo estructurado**: `data_extracted.csv`, en
   esta carpeta.
5. **Manejo de errores**: `try/except` sobre las excepciones de `requests` y
   validación del status code (404, 401/403, otros 4xx, 5xx con reintentos).

## Errores comunes evitados

- **Hardcoding**: la URL y la key se leen del `.env`, no están escritas en el
  código. Las coordenadas de las ciudades sí están en el código, pero no son
  datos sensibles.
- **Falta de manejo de excepciones**: si la API está caída o no responde, el
  script muestra un mensaje claro en vez de cortarse con un traceback.
- **Subir el `.env`**: está excluido en el `.gitignore`.

---

Tomás Bezzana
