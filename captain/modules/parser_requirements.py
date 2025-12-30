"""
Module: parser.requirements
Purpose: generate requirements.txt from build.yaml
Responds to: command:req
"""
from __future__ import annotations
from typing import Any, Dict, List
from pathlib import Path
import sys

try:
    import yaml  # minimal dependency (like in core)
except Exception:  # pragma: no cover
    print("Install: python -m pip install pyyaml", file=sys.stderr)
    raise

BUILD_FILE = "build.yaml"
OUT_FILE = "requirements.txt"


def register(core) -> None:
    """Register the only needed command."""
    core.subscribe("command:req", _convert_to_txt)


def _convert_to_txt(_topic: str, _payload: Any) -> None:
    cfg = _load_build_yaml(BUILD_FILE)
    deps = _extract_dependencies(cfg) if cfg else []
    _write_text(OUT_FILE, _render_requirements(deps))
    print(f"[OK] {OUT_FILE}")


# ---- helpers (simple and predictable) ----

def _load_build_yaml(path: str) -> Dict[str, Any] | None:
    """Load build.yaml → dict or None when missing/empty/non-dict."""
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
    """Return list of strings from dependencies section; skip other entries."""
    raw = cfg.get("dependencies", [])
    if not isinstance(raw, list):
        return []
    deps: List[str] = []
    for item in raw:
        if isinstance(item, str):
            s = item.strip()
            if s:
                deps.append(s)
    return deps


def _render_requirements(deps: List[str]) -> str:
    """Convert list to file content (with trailing newline)."""
    return ("\n".join(deps) + "\n") if deps else ""


MODULES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULES_DIR.parent
OUT_DIR = PROJECT_DIR / "Output"


def _write_text(path: str, content: str) -> None:
    """Write to txt file"""
    out_dir = Path(OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir.joinpath(path)
    with file_path.open(mode="w", encoding="utf-8") as f:
        f.write(content)