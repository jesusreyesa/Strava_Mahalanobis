"""Carga, limpieza, variables derivadas y etiquetado provisional de salidas.

Las etiquetas de ruta de este módulo son REGLAS SIMPLES sobre distancia,
desnivel y hora. Son provisionales: en la fase 2 se validan y se refinan
agrupando las trazas GPS.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FECHA_INICIO = "2025-08-01"

# Actividades con problemas conocidos de calidad: se marcan, no se borran.
# 16433608626: actividad de Huawei Health el mismo día que "Vals del obrero";
# puede ser un tramo grabado dos veces.
REVISAR = {"16433608626": "posible tramo duplicado el mismo dia"}

# Etiquetas asignadas a mano donde las reglas fallarían.
ETIQUETA_MANUAL = {
    "16433608626": "otra_media",
    "15558881255": "otra_media",  # ~21 km, ~629 m: distinta de Verjoncito
}

# (etiqueta, dist_km_min, dist_km_max, desnivel_min, desnivel_max)
REGLAS_LARGAS = [
    ("patios", 33.0, 38.5, 540.0, 780.0),
    ("verjon", 20.0, 31.0, 590.0, 750.0),
    ("patios_verjon", 53.0, 61.0, 1300.0, 1620.0),
    ("sopo", 100.0, 104.0, 860.0, 880.0),
    ("romeral", 79.0, 81.5, 980.0, 1005.0),
    ("santandercito_similar", 78.0, 92.0, 1135.0, 1180.0),
    ("mesitas", 118.0, 120.0, 1915.0, 1960.0),
    ("la_vega_cuchilla", 128.0, 152.0, 2200.0, 2320.0),
]


def etiquetar(fila: pd.Series) -> str:
    """Etiqueta provisional del tipo de salida a partir de reglas simples."""
    if fila["id"] in ETIQUETA_MANUAL:
        return ETIQUETA_MANUAL[fila["id"]]

    d, e, h = fila["dist_km"], fila["elev_gain_m"], fila["hora"]

    if d <= 16.0:
        if h >= 16:
            return "trayecto_tarde"
        if 10.0 <= d <= 15.5 and e <= 60.0:
            return "trayecto_manana"
        return "corta_otra"

    for nombre, dmin, dmax, emin, emax in REGLAS_LARGAS:
        if dmin <= d <= dmax and emin <= e <= emax:
            return nombre

    return "otra_larga" if d >= 60.0 else "otra_media"


def cargar_crudo(ruta: str) -> pd.DataFrame:
    """Lee el CSV crudo y filtra por fecha."""
    df = pd.read_csv(ruta, dtype={"id": str}, parse_dates=["start_local"])
    df = df[df["start_local"] >= FECHA_INICIO].copy()
    return df.sort_values("start_local").reset_index(drop=True)


def derivar(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula variables derivadas y la etiqueta provisional."""
    out = pd.DataFrame({"id": df["id"], "fecha": df["start_local"].dt.date})
    out["hora"] = df["start_local"].dt.hour + df["start_local"].dt.minute / 60
    out["dia_semana"] = df["start_local"].dt.dayofweek  # 0 = lunes

    out["dist_km"] = df["distance_m"] / 1000
    out["moving_min"] = df["moving_s"] / 60
    out["elapsed_min"] = df["elapsed_s"] / 60
    out["elev_gain_m"] = df["elev_gain_m"]
    out["elev_por_km"] = out["elev_gain_m"] / out["dist_km"]
    out["vel_media_kmh"] = out["dist_km"] / (out["moving_min"] / 60)
    out["vel_max_kmh"] = df["max_speed_ms"] * 3.6
    out["ratio_paradas"] = (df["elapsed_s"] - df["moving_s"]) / df["elapsed_s"]

    out["ruta"] = out.apply(etiquetar, axis=1)
    out["revisar"] = out["id"].map(REVISAR).fillna("")
    return out
