import pandas as pd

from stravamaha.data import derivar, etiquetar


def _fila(**kw):
    base = dict(id="x", dist_km=13.6, elev_gain_m=35.0, hora=6.3)
    base.update(kw)
    return pd.Series(base)


def test_trayecto_manana():
    assert etiquetar(_fila()) == "trayecto_manana"


def test_trayecto_tarde():
    assert etiquetar(_fila(hora=17.4, elev_gain_m=131.0)) == "trayecto_tarde"


def test_ruta_larga_conocida():
    assert etiquetar(_fila(dist_km=102.0, elev_gain_m=870.0)) == "sopo"


def test_salida_no_reconocida():
    assert etiquetar(_fila(dist_km=70.0, elev_gain_m=300.0)) == "otra_larga"


def test_derivar_velocidad_y_paradas():
    df = pd.DataFrame(
        {
            "id": ["a"],
            "start_local": pd.to_datetime(["2026-01-05T06:20:00"]),
            "distance_m": [36000.0],
            "moving_s": [7200],
            "elapsed_s": [9000],
            "elev_gain_m": [540.0],
            "max_speed_ms": [10.0],
            "name": ["n"],
        }
    )
    out = derivar(df).iloc[0]
    assert abs(out["vel_media_kmh"] - 18.0) < 1e-9
    assert abs(out["ratio_paradas"] - 0.2) < 1e-9
    assert abs(out["elev_por_km"] - 15.0) < 1e-9


def test_cargar_crudo_excluye_duplicado_confirmado():
    import os
    import tempfile

    from stravamaha.data import cargar_crudo

    filas = (
        "id,start_local,distance_m,moving_s,elapsed_s,elev_gain_m,max_speed_ms,name\n"
        "16433608626,2025-11-03T08:50:32,36253,5695,5803,679.8,17.3,dup\n"
        "16342647758,2025-11-03T06:15:18,105338,16588,17701,937.9,17.2,completa\n"
        "1,2024-01-01T06:00:00,10000,2000,2100,10,9,vieja\n"
    )
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, "crudo.csv")
        with open(ruta, "w") as f:
            f.write(filas)
        df = cargar_crudo(ruta)
    assert list(df["id"]) == ["16342647758"]
