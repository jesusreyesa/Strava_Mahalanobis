"""Distancia de Mahalanobis: implementación propia, versión clásica y robusta (MCD)."""

from __future__ import annotations

import numpy as np
from scipy import stats
from sklearn.covariance import MinCovDet


def mahalanobis_sq(X, mean, cov) -> np.ndarray:
    """Distancia de Mahalanobis al cuadrado de cada fila de X.

    d²(x) = (x - mean)ᵀ cov⁻¹ (x - mean)

    Se usa solve en lugar de invertir la matriz, que es más estable
    numéricamente. Si cov es singular lanza np.linalg.LinAlgError.
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    diff = X - np.asarray(mean, dtype=float)
    sol = np.linalg.solve(np.asarray(cov, dtype=float), diff.T)
    return np.einsum("ij,ji->i", diff, sol)


def fit_classical(X):
    """Media y covarianza muestral clásicas."""
    X = np.asarray(X, dtype=float)
    return X.mean(axis=0), np.cov(X, rowvar=False)


def fit_robust(X, support_fraction: float | None = None, random_state: int = 0):
    """Media y covarianza robustas con MCD (Minimum Covariance Determinant)."""
    mcd = MinCovDet(support_fraction=support_fraction, random_state=random_state)
    mcd.fit(np.asarray(X, dtype=float))
    return mcd.location_, mcd.covariance_


def chi2_cutoff(p: int, level: float = 0.975) -> float:
    """Punto de corte χ²(p) para señalar atípicos bajo normalidad multivariada."""
    return float(stats.chi2.ppf(level, df=p))
