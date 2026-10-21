"""Genera data/processed/salidas.csv a partir del CSV crudo (que no se versiona)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from stravamaha.data import cargar_crudo, derivar  # noqa: E402

crudo = cargar_crudo(str(RAIZ / "data/raw/activities_raw.csv"))
proc = derivar(crudo)
proc.round(3).to_csv(RAIZ / "data/processed/salidas.csv", index=False)
print(len(crudo), "salidas")
print(proc["ruta"].value_counts().to_string())
