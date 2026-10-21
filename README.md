# Strava_Mahalanobis

Análisis estadístico de mis salidas de ciclismo de ruta (Bogotá) con datos de Strava, usando la **distancia de Mahalanobis** para estudiar atipicidades multivariadas, y un **recomendador de rutas** construido sobre ese análisis.

> Estado: en construcción. Fase 1 (atipicidades) en desarrollo.

## Pregunta

1. ¿Qué salidas se salen de mi patrón habitual en terreno y ritmo, mirando las variables en conjunto y no una por una?
2. ¿Cómo cambia mi rendimiento en subida con el tiempo?
3. Dado el tiempo y el esfuerzo que quiero hoy, ¿qué ruta y qué distancia son probables según mi historial?

## Método

- **Mahalanobis clásico:** d²(x) = (x − μ)ᵀ Σ⁻¹ (x − μ). Corrige escala y correlación entre variables.
- **Referencia teórica:** si los datos son normales multivariados, d² ~ χ²(p). Se revisa el ajuste con un QQ-plot.
- **Mahalanobis robusto (MCD):** estimación de μ y Σ resistente a atípicos, para evitar el *masking*.
- **Variables (sin sensores de pulso ni potencia):** distancia, tiempo en movimiento, desnivel, desnivel por km, velocidad media y máxima, ratio de paradas, VAM en subida.
- **Fase 2:** agrupación de salidas en rutas, modelo de tiempo y distancia esperados con intervalos de predicción, y recomendador.

## Limitaciones declaradas

- No hay etiquetas de "atípico verdadero": la validación se hace contra salidas que conozco.
- Sin pulso ni potencia, el "esfuerzo" es un proxy basado en ritmo, terreno y VAM.
- Las salidas son una serie temporal y Mahalanobis las trata como independientes.
- Las distintas rutas probablemente no comparten una sola matriz de covarianza.

## Estructura

```
data/raw/            datos crudos (no se versionan)
data/processed/      datos procesados agregados
notebooks/           análisis paso a paso
src/stravamaha/      código reutilizable
tests/               pruebas
reports/figures/     figuras para el informe
```

## Privacidad

No se publican trazas GPS ni ubicaciones. Solo se versionan variables agregadas por actividad.

## Uso

```bash
pip install -r requirements.txt
pytest
```
