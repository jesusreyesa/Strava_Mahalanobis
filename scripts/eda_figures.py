"""Genera las figuras del EDA en reports/figures/ (trayectos de mañana)."""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd  # noqa: E402

from stravamaha import plots  # noqa: E402

VARS_MODELO = ["dist_km", "elev_gain_m", "vel_media_kmh", "vel_max_kmh", "ratio_paradas"]
VARS_CORR = ["dist_km", "moving_min", "elapsed_min", "elev_gain_m",
             "vel_media_kmh", "vel_max_kmh", "ratio_paradas"]

d = pd.read_csv(RAIZ / "data/processed/salidas.csv")
m = d[d["ruta"] == "trayecto_manana"].copy()
fig_dir = RAIZ / "reports/figures"

plots.distribuciones(m, VARS_MODELO, str(fig_dir / "eda_distribuciones.png"))
plots.correlacion(m, VARS_CORR, str(fig_dir / "eda_correlacion.png"))
plots.serie_velocidad(m, str(fig_dir / "eda_serie_velocidad.png"))
print("figuras en", fig_dir)
