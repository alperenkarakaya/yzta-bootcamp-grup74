"""Paket-göreli dosya yolları — çalışma dizininden (CWD) bağımsız.

Django (product/04-backend) ile scriptler (repo kökü) farklı CWD'lerde çalışır;
model ve veri yolları bu yüzden __file__'e göre çözülür, env ile override edilebilir.
"""
import os
from pathlib import Path

_PKG = Path(__file__).resolve().parent                     # .../product/02-ai-agents/aks_core
ARTIFACTS_DIR = _PKG / "artifacts"
_REPO = _PKG.parents[2]                                     # .../<repo kökü>
_DEFAULT_DATA = _REPO / "product" / "01-data" / "datasets"

MODEL_PATH = Path(os.environ.get("AKS_MODEL", ARTIFACTS_DIR / "aks_model.joblib"))
METRICS_PATH = ARTIFACTS_DIR / "metrikler.json"
DATA_DIR = Path(os.environ.get("AKS_DATA_DIR", _DEFAULT_DATA))


def data(name: str) -> str:
    """01-data/datasets içindeki bir dosyanın tam yolu (env: AKS_DATA_DIR)."""
    return str(DATA_DIR / name)


def model_path() -> str:
    return str(MODEL_PATH)
