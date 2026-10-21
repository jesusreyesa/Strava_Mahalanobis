"""Análisis de atipicidades multivariadas en salidas de ciclismo con Mahalanobis."""

from .mahalanobis import (
    chi2_cutoff,
    fit_classical,
    fit_robust,
    mahalanobis_sq,
)

__all__ = ["chi2_cutoff", "fit_classical", "fit_robust", "mahalanobis_sq"]
