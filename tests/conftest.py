import copy
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Dynamically load the app module from src/app.py so tests work regardless of
# whether `src` is a package on sys.path.
ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "src" / "app.py"
spec = importlib.util.spec_from_file_location("src.app", str(APP_PATH))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = getattr(app_module, "app")


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def isolate_activities():
    """Deep-copy the in-memory `activities` before each test and restore it
    afterwards so tests remain isolated.
    """
    activities = getattr(app_module, "activities", None)
    if activities is None:
        yield
        return

    orig = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(orig)
