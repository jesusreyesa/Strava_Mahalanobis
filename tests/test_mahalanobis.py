import numpy as np
from scipy import stats
from scipy.spatial.distance import mahalanobis as scipy_mahalanobis

from stravamaha import chi2_cutoff, fit_classical, fit_robust, mahalanobis_sq


def _datos_normales(n=2000, seed=0):
    rng = np.random.default_rng(seed)
    cov = np.array([[4.0, 2.0, 0.5], [2.0, 3.0, 1.0], [0.5, 1.0, 2.0]])
    mean = np.array([10.0, -3.0, 5.0])
    return rng.multivariate_normal(mean, cov, size=n), mean, cov


def test_coincide_con_scipy():
    X, mean, cov = _datos_normales(n=50)
    inv = np.linalg.inv(cov)
    esperado = np.array([scipy_mahalanobis(x, mean, inv) ** 2 for x in X])
    np.testing.assert_allclose(mahalanobis_sq(X, mean, cov), esperado)


def test_distribucion_chi_cuadrado():
    X, mean, cov = _datos_normales()
    d2 = mahalanobis_sq(X, mean, cov)
    # Con parámetros verdaderos, d² ~ chi²(p): la prueba KS no debe rechazar
    _, pvalor = stats.kstest(d2, "chi2", args=(3,))
    assert pvalor > 0.01


def test_corte_chi2_cobertura():
    X, mean, cov = _datos_normales()
    d2 = mahalanobis_sq(X, mean, cov)
    fraccion = np.mean(d2 <= chi2_cutoff(3, 0.975))
    assert abs(fraccion - 0.975) < 0.01


def test_robusto_resiste_atipicos():
    """El MCD debe estimar mejor la media que la clásica cuando hay contaminación."""
    X, mean, cov = _datos_normales(n=500)
    X_cont = X.copy()
    X_cont[:50] += np.array([40.0, 40.0, 40.0])  # 10 % de atípicos

    m_clasica, _ = fit_classical(X_cont)
    m_robusta, _ = fit_robust(X_cont)

    err_clasica = np.linalg.norm(m_clasica - mean)
    err_robusta = np.linalg.norm(m_robusta - mean)
    assert err_robusta < err_clasica
