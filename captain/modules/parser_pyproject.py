"""
Module: parser.pyproject
Purpose: generate pyproject.toml from build.yaml
Responds to: command:pyproject
"""
from __future__ import annotations
from typing import Any, Dict, List
import sys
from pathlib import Path
import tomli_w  # pip install tomli-w

try:
    import yaml
except Exception:
    print("Install: python -m pip install pyyaml tomli-w", file=sys.stderr)
    raise

BUILD_FILE = "build.yaml"
OUT_FILE = "pyproject.toml"


def register(core) -> None:
    """Register command in the core."""
    core.subscribe("command:pyproject", _convert_to_pyproject)


def _convert_to_pyproject(_topic: str, _payload: Any) -> None:
    cfg = _load_build_yaml(BUILD_FILE)
    deps = _extract_dependencies(cfg) if cfg else []
    project_name = cfg.get("myproject", "example-app") if cfg else "example-app"
    pyproject_data = _render_pyproject(project_name, deps)
    _write_toml(OUT_FILE, pyproject_data)
    print(f"[OK] {OUT_FILE}")


# ---- helpers ----

def _load_build_yaml(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[ERR] Cannot read {path}: {e}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) and data else None


def _extract_dependencies(cfg: Dict[str, Any]) -> List[str]:
    raw = cfg.get("dependencies", [])
    if not isinstance(raw, list):
        return []
    return [item.strip() for item in raw if isinstance(item, str) and item.strip()]


def _render_pyproject(name: str, deps: List[str]) -> Dict[str, Any]:
    """Creates pyproject.toml structure as dict."""
    return {
        "project": {
            "name": name,
            "version": "1.0",
            "dependencies": deps,
        },
        "build-system": {
            "requires": ["setuptools", "wheel"],
            "build-backend": "setuptools.build_meta",
        },
    }


MODULES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULES_DIR.parent
OUT_DIR = PROJECT_DIR / "Output"


def _write_toml(path: str, data: Dict[str, Any]) -> None:
    """Write to pyproject file"""
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir.joinpath(path)
    with file_path.open(mode="wb") as f:
        tomli_w.dump(data, f)