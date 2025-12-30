"""
Module: validator.build
Purpose: minimally check if build.yaml is valid.
Responds to: command:validate build
Simple rules:
- build.yaml exists and parses to a non-empty dict,
- allowed keys: myproject (str), dependencies (list[str]),
- each entry in dependencies is a non-empty string (after strip).
"""
from __future__ import annotations
from typing import Any, Dict, List
import sys

try:
    import yaml  # pip install pyyaml
except Exception:
    print("Install: python -m pip install pyyaml", file=sys.stderr)
    raise

BUILD_FILE = "build.yaml"
ALLOWED_KEYS = {"myproject", "dependencies"}


def register(core) -> None:
    """Register command in the core"""
    core.subscribe("command:validate build", _validate_build)


def _validate_build(_topic: str, _payload: Any) -> None:
    """Validation: short, clear and without magic"""
    cfg = _load_build_yaml(BUILD_FILE)
    if cfg is None:
        print("[ERR] Missing or unreadable build.yaml", file=sys.stderr)
        return
    
    if not isinstance(cfg, dict) or not cfg:
        print(
            "[ERR] build.yaml must be a non-empty dictionary (YAML mapping)",
            file=sys.stderr,
        )
        return
    
    # 1) unknown keys -> warn, but don't block
    unknown = sorted(set(cfg.keys()) - ALLOWED_KEYS)
    if unknown:
        print(f"[WARN] Unknown keys: {', '.join(unknown)}", file=sys.stderr)
    
    # 2) myproject (optional)
    if "myproject" in cfg:
        if not isinstance(cfg["myproject"], str) or not cfg["myproject"].strip():
            print("[ERR] 'myproject' must be a non-empty string", file=sys.stderr)
            return
    
    # 3) dependencies (optional)
    if "dependencies" in cfg:
        deps = cfg["dependencies"]
        if not isinstance(deps, list):
            print("[ERR] 'dependencies' must be a list of strings", file=sys.stderr)
            return
        
        bad: List[int] = [
            i for i, v in enumerate(deps) if not isinstance(v, str) or not v.strip()
        ]
        if bad:
            print(
                f"[ERR] dependencies[{bad[0]}] must be a non-empty string",
                file=sys.stderr,
            )
            return
    
    print("[OK] build.yaml")


# --- helpers ---

def _load_build_yaml(path: str) -> Dict[str, Any] | None:
    """Load YAML -> dict or None when missing/error"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return data if isinstance(data, dict) else None