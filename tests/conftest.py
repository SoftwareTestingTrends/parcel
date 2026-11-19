import pytest


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    """Tests never call a real model, whatever your shell has set."""
    for name in ("PARCEL_BACKEND", "PARCEL_MODEL", "PARCEL_REFUND_GUARD", "PARCEL_TEMPERATURE"):
        monkeypatch.delenv(name, raising=False)
