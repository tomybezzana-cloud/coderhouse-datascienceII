"""
Pre-entrega 4: Extracción y Almacenamiento Seguro de Datos vía API.

Consulta la API pública de Open-Meteo (https://open-meteo.com) para obtener el
pronóstico diario de varias ciudades argentinas y lo guarda en un CSV.

Pasos:
1. Configuración: carga de variables desde .env con python-dotenv.
2. Extracción: petición GET por ciudad con requests, con manejo de errores
   HTTP (404, 5xx), timeouts, fallas de conexión y respuestas inválidas.
3. Transformación: de la respuesta JSON se conservan solo los campos útiles
   y se pasa de formato "por columnas" a una fila por ciudad y día.
4. Persistencia: exportación a data_extracted.csv
"""

import csv
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    # Opcional: hace que Python confíe en los certificados del sistema
    # operativo (útil si un antivirus o proxy corporativo inspecciona HTTPS).
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
RUTA_ENV = BASE_DIR / ".env"
RUTA_CSV = BASE_DIR / "data_extracted.csv"

# Coordenadas de las ciudades disponibles. No son datos sensibles, por eso
# viven en el código; qué ciudades se consultan se elige desde el .env.
CIUDADES = {
    "Buenos Aires": (-34.61, -58.38),
    "Córdoba": (-31.42, -64.18),
    "Rosario": (-32.95, -60.65),
    "Mendoza": (-32.89, -68.83),
    "Bariloche": (-41.13, -71.31),
    "Salta": (-24.79, -65.41),
    "Ushuaia": (-54.80, -68.30),
}

VARIABLES_DIARIAS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
]

# Nombres de columna del CSV final (en castellano y sin unidades en el nombre
# de la API).
COLUMNAS_CSV = {
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "precipitation_sum": "precipitacion_mm",
    "precipitation_probability_max": "prob_precipitacion_pct",
    "wind_speed_10m_max": "viento_max_kmh",
}

MAX_INTENTOS = 3  # reintentos ante errores 5xx o timeouts


class ErrorExtraccion(Exception):
    """Falla al obtener datos de la API, con un mensaje legible."""


def titulo(texto: str) -> None:
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


# ---------------------------------------------------------------------------
# 1. Configuración
# ---------------------------------------------------------------------------
def cargar_configuracion() -> dict:
    if not RUTA_ENV.exists():
        raise ErrorExtraccion(
            f"No se encontró {RUTA_ENV.name}. Copiá .env.example como .env "
            "y completá los valores."
        )
    load_dotenv(RUTA_ENV)

    base_url = os.getenv("API_BASE_URL", "").strip()
    if not base_url:
        raise ErrorExtraccion("Falta la variable API_BASE_URL en el .env.")

    try:
        dias = int(os.getenv("DIAS_PRONOSTICO", "7"))
        timeout = float(os.getenv("TIMEOUT_SEGUNDOS", "10"))
    except ValueError as e:
        raise ErrorExtraccion(f"Valor numérico inválido en el .env: {e}") from e
    if not 1 <= dias <= 16:
        raise ErrorExtraccion("DIAS_PRONOSTICO debe estar entre 1 y 16.")

    nombres = [c.strip() for c in os.getenv("CIUDADES", "").split(",") if c.strip()]
    desconocidas = [c for c in nombres if c not in CIUDADES]
    for c in desconocidas:
        print(f"  [aviso] Ciudad '{c}' sin coordenadas cargadas: se omite.")
    ciudades = [c for c in nombres if c in CIUDADES]
    if not ciudades:
        raise ErrorExtraccion("CIUDADES no tiene ninguna ciudad válida.")

    return {
        "base_url": base_url,
        # Open-Meteo no usa key; se lee igual para no tener que tocar el
        # código si se cambia a una API que la pida.
        "api_key": os.getenv("API_KEY", "").strip(),
        "dias": dias,
        "timeout": timeout,
        "ciudades": ciudades,
    }


# ---------------------------------------------------------------------------
# 2. Extracción
# ---------------------------------------------------------------------------
def pedir_pronostico(ciudad: str, config: dict) -> dict:
    lat, lon = CIUDADES[ciudad]
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(VARIABLES_DIARIAS),
        "timezone": "America/Argentina/Buenos_Aires",
        "forecast_days": config["dias"],
    }
    if config["api_key"]:
        params["apikey"] = config["api_key"]

    for intento in range(1, MAX_INTENTOS + 1):
        try:
            respuesta = requests.get(
                config["base_url"], params=params, timeout=config["timeout"]
            )
        except requests.exceptions.Timeout:
            motivo = f"la API no respondió en {config['timeout']:g} s"
        except requests.exceptions.SSLError:
            # Subclase de ConnectionError: va antes para dar un mensaje propio.
            raise ErrorExtraccion(
                "no se pudo verificar el certificado SSL (si un antivirus "
                "inspecciona HTTPS, instalá truststore: ver README)"
            )
        except requests.exceptions.ConnectionError:
            # Sin red o servidor caído: reintentar rara vez ayuda.
            raise ErrorExtraccion(
                "no se pudo conectar con la API (¿hay conexión a internet?)"
            )
        except requests.exceptions.RequestException as e:
            raise ErrorExtraccion(f"error inesperado en la petición: {e}") from e
        else:
            codigo = respuesta.status_code
            if codigo == 200:
                try:
                    return respuesta.json()
                except ValueError:
                    raise ErrorExtraccion("la respuesta no es un JSON válido")
            if codigo == 404:
                raise ErrorExtraccion(
                    f"404: el endpoint no existe, revisá API_BASE_URL ({config['base_url']})"
                )
            if codigo in (401, 403):
                raise ErrorExtraccion(f"{codigo}: acceso denegado, revisá API_KEY")
            if 400 <= codigo < 500:
                # Open-Meteo explica el problema en el campo "reason".
                try:
                    detalle = respuesta.json().get("reason", respuesta.text)
                except ValueError:
                    detalle = respuesta.text
                raise ErrorExtraccion(f"{codigo}: petición inválida ({detalle})")
            motivo = f"error del servidor ({codigo})"  # 5xx: puede ser temporal

        if intento < MAX_INTENTOS:
            espera = 2 ** intento
            print(f"  [reintento] {ciudad}: {motivo}. Nuevo intento en {espera} s...")
            time.sleep(espera)

    raise ErrorExtraccion(f"{motivo}, después de {MAX_INTENTOS} intentos")


# ---------------------------------------------------------------------------
# 3. Transformación
# ---------------------------------------------------------------------------
def transformar(ciudad: str, datos: dict) -> list[dict]:
    """Convierte la respuesta en filas (una por día) con solo los campos útiles.

    La API devuelve cada variable como una lista paralela a "time" y agrega
    metadatos que no interesan (generationtime_ms, elevation, utc_offset...).
    """
    try:
        diario = datos["daily"]
        fechas = diario["time"]
        filas = []
        for i, fecha in enumerate(fechas):
            fila = {"ciudad": ciudad, "fecha": fecha}
            for variable, columna in COLUMNAS_CSV.items():
                fila[columna] = diario[variable][i]
            filas.append(fila)
    except (KeyError, IndexError, TypeError) as e:
        raise ErrorExtraccion(f"la respuesta no tiene el formato esperado ({e})") from e
    return filas


# ---------------------------------------------------------------------------
# 4. Persistencia
# ---------------------------------------------------------------------------
def guardar_csv(filas: list[dict], ruta: Path) -> None:
    columnas = ["ciudad", "fecha", *COLUMNAS_CSV.values()]
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def main() -> int:
    titulo("1. Configuración")
    try:
        config = cargar_configuracion()
    except ErrorExtraccion as e:
        print(f"  [error] {e}")
        return 1
    print(f"  Endpoint: {config['base_url']}")
    print(f"  Ciudades: {', '.join(config['ciudades'])}")
    print(f"  Días de pronóstico: {config['dias']}")

    titulo("2-3. Extracción y transformación")
    filas, fallidas = [], []
    for ciudad in config["ciudades"]:
        try:
            datos = pedir_pronostico(ciudad, config)
            filas_ciudad = transformar(ciudad, datos)
        except ErrorExtraccion as e:
            # Una ciudad que falla no frena al resto.
            print(f"  [error] {ciudad}: {e}")
            fallidas.append(ciudad)
            continue
        filas.extend(filas_ciudad)
        print(f"  [ok] {ciudad}: {len(filas_ciudad)} días")

    if not filas:
        print("\n  No se obtuvo ningún dato. No se genera el CSV.")
        return 1

    titulo("4. Persistencia")
    try:
        guardar_csv(filas, RUTA_CSV)
    except OSError as e:
        print(f"  [error] No se pudo escribir {RUTA_CSV.name}: {e}")
        return 1
    print(f"  {len(filas)} filas guardadas en {RUTA_CSV.name}")
    if fallidas:
        print(f"  Ciudades sin datos: {', '.join(fallidas)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
