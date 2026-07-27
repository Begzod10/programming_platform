"""Load a course spec module given a dotted name or a file path."""
from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from types import ModuleType


def load_spec(path_or_name: str) -> ModuleType:
    p = Path(path_or_name)
    if p.suffix == ".py" and p.exists():
        spec = importlib.util.spec_from_file_location(p.stem, p)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module
    return importlib.import_module(path_or_name)


def require(module: ModuleType, name: str):
    if not hasattr(module, name):
        raise AttributeError(f"spec module {module.__name__!r} has no top-level {name!r}")
    return getattr(module, name)
