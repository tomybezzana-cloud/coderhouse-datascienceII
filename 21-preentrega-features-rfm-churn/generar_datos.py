"""
Genera los datos crudos del e-commerce: data/usuarios.csv y data/pedidos.csv.
Autor: Tomás Bezzana

Los datos son sintéticos y reproducibles (semilla fija). Cada usuario sigue un
perfil de comportamiento, pero el perfil NO se guarda en los CSV: el objetivo
es que las features lo descubran a partir de los pedidos.

Perfiles:
  activo       compra cada 15-45 días durante todo el período.
  en_declive   empieza comprando seguido y cada vez compra menos y más espaciado.
  abandonado   compra unos meses y deja de comprar a mitad de año.
  nuevo        se registra en el último trimestre.
  sin_compras  se registra y nunca compra.

Período: pedidos desde 2025-01-01 hasta 2026-02-28. Las features usan hasta
la fecha de corte (2025-12-31); los pedidos de 2026 solo sirven para armar la
etiqueta de churn.

Uso:
    python generar_datos.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 42
INICIO = date(2025, 1, 1)
FIN_DATOS = date(2026, 2, 28)
PROB_CANCELADO = 0.08

PERFILES = (["activo"] * 24 + ["en_declive"] * 12 + ["abandonado"] * 10
            + ["nuevo"] * 8 + ["sin_compras"] * 6)

CARPETA = Path(__file__).resolve().parent / "data"


def dia(n: int) -> date:
    return INICIO + timedelta(days=n)


def compras(perfil: str, registro: date, rng: random.Random) -> list[tuple[date, float]]:
    """Devuelve la lista de (fecha, monto) de un usuario según su perfil."""
    fin = (FIN_DATOS - INICIO).days
    resultado = []
    actual = (registro - INICIO).days + rng.randint(0, 15)

    if perfil == "activo":
        while actual <= fin:
            resultado.append((dia(actual), rng.uniform(30, 150)))
            actual += rng.randint(15, 45)

    elif perfil == "en_declive":
        gap, monto = rng.randint(12, 25), rng.uniform(80, 160)
        while actual <= fin:
            resultado.append((dia(actual), monto * rng.uniform(0.85, 1.15)))
            actual += int(gap)
            gap *= rng.uniform(1.25, 1.45)   # compra cada vez más espaciado
            monto *= 0.88                    # y gasta cada vez menos

    elif perfil == "abandonado":
        corte = rng.randint(110, 220)        # deja de comprar entre abril y agosto
        while actual <= corte:
            resultado.append((dia(actual), rng.uniform(25, 120)))
            actual += rng.randint(18, 40)

    elif perfil == "nuevo":
        while actual <= fin and rng.random() > 0.15:
            resultado.append((dia(actual), rng.uniform(20, 110)))
            actual += rng.randint(10, 35)

    return resultado


def main() -> None:
    rng = random.Random(SEMILLA)
    perfiles = PERFILES[:]
    rng.shuffle(perfiles)

    usuarios, pedidos = [], []
    for usuario_id, perfil in enumerate(perfiles, start=1):
        if perfil == "nuevo":
            registro = dia(rng.randint(275, 335))   # octubre-noviembre
        elif perfil == "sin_compras":
            registro = dia(rng.randint(0, 330))
        else:
            registro = dia(rng.randint(0, 120))
        usuarios.append((usuario_id, registro.isoformat()))

        for fecha, monto in compras(perfil, registro, rng):
            estado = "cancelado" if rng.random() < PROB_CANCELADO else "completado"
            pedidos.append([usuario_id, fecha.isoformat(), round(monto, 2), estado])

    # Los pedido_id siguen el orden cronológico, como en un sistema real.
    pedidos.sort(key=lambda p: (p[1], p[0]))

    CARPETA.mkdir(exist_ok=True)
    with open(CARPETA / "usuarios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["usuario_id", "fecha_registro"])
        w.writerows(usuarios)
    with open(CARPETA / "pedidos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pedido_id", "usuario_id", "fecha_pedido", "monto", "estado"])
        w.writerows([i, *p] for i, p in enumerate(pedidos, start=1))

    print(f"usuarios.csv: {len(usuarios)} usuarios")
    print(f"pedidos.csv:  {len(pedidos)} pedidos")


if __name__ == "__main__":
    main()
