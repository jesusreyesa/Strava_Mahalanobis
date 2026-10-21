"""Figuras del EDA. Misma paleta en todas: azul = normal, naranja = marcado."""

from __future__ import annotations

import matplotlib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

AZUL = "#2a78d6"  # categórico 1
NARANJA = "#eb6834"  # categórico 2
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERFICIE = "#fcfcfb"
REJILLA = "#e4e3df"

ETIQUETAS = {
    "dist_km": "Distancia (km)",
    "elev_gain_m": "Desnivel acumulado (m)",
    "vel_media_kmh": "Velocidad media (km/h)",
    "vel_max_kmh": "Velocidad máxima (km/h)",
    "ratio_paradas": "Proporción de paradas",
    "moving_min": "Tiempo en movimiento (min)",
    "elapsed_min": "Tiempo total (min)",
    "hora": "Hora de salida",
}


def _estilo(ax):
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.tick_params(colors=TINTA_2, labelsize=8)
    ax.grid(axis="y", color=REJILLA, linewidth=0.6)
    ax.set_axisbelow(True)


def marcar_z(serie: pd.Series, umbral: float = 3.0) -> pd.Series:
    """True donde |z| > umbral (z univariado, media y sd clásicas)."""
    return ((serie - serie.mean()) / serie.std()).abs() > umbral


def distribuciones(m: pd.DataFrame, columnas: list[str], ruta: str | None = None):
    """Un histograma por variable; las marcas naranjas bajo el eje son |z|>3."""
    n = len(columnas)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 3.0), facecolor=SUPERFICIE)
    for ax, col in zip(np.atleast_1d(axes), columnas):
        _estilo(ax)
        ax.hist(m[col], bins=20, color=AZUL, edgecolor=SUPERFICIE, linewidth=1.0)
        flag = marcar_z(m[col])
        if flag.any():
            ax.plot(
                m.loc[flag, col],
                np.full(int(flag.sum()), -0.02),
                "|",
                color=NARANJA,
                markersize=14,
                markeredgewidth=2,
                transform=ax.get_xaxis_transform(),
                clip_on=False,
            )
        ax.set_title(ETIQUETAS[col], fontsize=9, color=TINTA, loc="left")
        ax.set_ylabel("salidas" if col == columnas[0] else "", fontsize=8, color=TINTA_2)
    fig.legend(
        handles=[
            Patch(facecolor=AZUL, label="salidas"),
            Line2D([], [], marker="|", color=NARANJA, markersize=10,
                   markeredgewidth=2, linestyle="", label="|z| > 3"),
        ],
        loc="lower center", ncol=2, frameon=False, fontsize=8, labelcolor=TINTA_2,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    if ruta:
        fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE)
    return fig


def correlacion(m: pd.DataFrame, columnas: list[str], ruta: str | None = None):
    """Mapa de calor de correlaciones. Divergente azul-gris-naranja, centro en 0."""
    c = m[columnas].corr()
    cmap = LinearSegmentedColormap.from_list("div", [NARANJA, "#ecebe7", AZUL])
    fig, ax = plt.subplots(figsize=(6.6, 5.4), facecolor=SUPERFICIE)
    im = ax.imshow(c.values, cmap=cmap, vmin=-1, vmax=1)
    nombres = [ETIQUETAS[x] for x in columnas]
    ax.set_xticks(range(len(columnas)), nombres, rotation=40, ha="right", fontsize=8, color=TINTA_2)
    ax.set_yticks(range(len(columnas)), nombres, fontsize=8, color=TINTA_2)
    for i in range(len(columnas)):
        for j in range(len(columnas)):
            ax.text(j, i, f"{c.values[i, j]:.2f}", ha="center", va="center",
                    fontsize=7.5, color=TINTA)
    for lado in ax.spines.values():
        lado.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.ax.tick_params(labelsize=8, colors=TINTA_2)
    cb.outline.set_visible(False)
    ax.set_title("Correlación de Pearson (azul +, naranja −)", fontsize=10,
                 color=TINTA, loc="left")
    fig.tight_layout()
    if ruta:
        fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE)
    return fig


def serie_velocidad(m: pd.DataFrame, ruta: str | None = None):
    """Velocidad media en el tiempo, con mediana móvil y cortes de actividad."""
    d = m.assign(fecha=pd.to_datetime(m["fecha"])).sort_values("fecha")
    huecos = d["fecha"].diff().dt.days
    tramo = (huecos > 10).cumsum()
    fig, ax = plt.subplots(figsize=(8.5, 3.6), facecolor=SUPERFICIE)
    _estilo(ax)
    ax.scatter(d["fecha"], d["vel_media_kmh"], s=26, color=AZUL,
               edgecolor=SUPERFICIE, linewidth=1.0, zorder=3)
    # La mediana móvil se calcula y se dibuja por tramos: no cruza los huecos.
    for _, sub in d.groupby(tramo):
        med = sub["vel_media_kmh"].rolling(9, center=True, min_periods=5).median()
        ax.plot(sub["fecha"], med, color=NARANJA, linewidth=2, zorder=2)
    for i in np.flatnonzero(huecos.values > 10):
        ax.axvspan(d["fecha"].iloc[i - 1], d["fecha"].iloc[i], color=REJILLA, alpha=0.7, zorder=1)
        ax.text(d["fecha"].iloc[i - 1], ax.get_ylim()[1], " sin salidas", fontsize=8,
                color=TINTA_2, va="top")
    ax.set_ylabel("Velocidad media (km/h)", fontsize=8, color=TINTA_2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_title("Trayecto de mañana: velocidad media por salida", fontsize=10,
                 color=TINTA, loc="left")
    ax.legend(
        handles=[
            Line2D([], [], marker="o", color=AZUL, linestyle="", markersize=6, label="salida"),
            Line2D([], [], color=NARANJA, linewidth=2, label="mediana móvil (9 salidas)"),
        ],
        frameon=False, fontsize=8, labelcolor=TINTA_2, loc="lower left",
    )
    fig.tight_layout()
    if ruta:
        fig.savefig(ruta, dpi=150, facecolor=SUPERFICIE)
    return fig
