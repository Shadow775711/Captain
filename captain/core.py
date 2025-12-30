#!/usr/bin/env python3
"""
Captain — minimal core:
- Typer CLI
- dynamic module loader
- simple event-bus (publish/subscribe)
- runs ONLY commands from config.yaml (preserving order)
"""

from __future__ import annotations

from collections import defaultdict
import importlib
import shutil
from typing import Any, Callable

import typer
import yaml  # pip install pyyaml

app = typer.Typer(add_completion=False)
Subscriber = Callable[[str, Any], None]


class Core:
    """Loads modules and dispatches commands as events."""

    def __init__(self, version: str = "1.0-Beta") -> None:
        self.version = version
        self.ctx: dict[str, Any] = {"version": version}
        self.subs: dict[str, list[Subscriber]] = defaultdict(list)
        self.allowed_cmds_list: list[str] = []
        self.allowed_cmds_set: set[str] = set()

    def subscribe(self, topic: str, fn: Subscriber) -> None:
        """Module subscribes to a topic (e.g. 'command:req')."""
        self.subs[topic].append(fn)

    def publish(self, topic: str, payload: Any = None) -> None:
        """Calls subscribers; errors don't stop core execution."""
        for fn in self.subs.get(topic, []):
            try:
                fn(topic, payload)
            except Exception as exc:
                typer.echo(f"[ERR] {topic}: {exc}", err=True)

    @staticmethod
    def _load_yaml(path: str) -> dict[str, Any]:
        """Loads YAML and always returns dict (even when file is empty)."""
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _load_modules(self, names: list[str]) -> None:
        """Loads modules and calls register(core).

        Imports: modules.<name_with_dots_replaced_by_underscores>
        """
        for name in names or []:
            if name == "core":
                continue

            mod_path = f"modules.{name.replace('.', '_')}"
            try:
                mod = importlib.import_module(mod_path)
            except ModuleNotFoundError:
                typer.echo(f"[WARN] missing module: {mod_path}")
                continue

            reg = getattr(mod, "register", None)
            if callable(reg):
                reg(self)
            else:
                typer.echo(f"[WARN] {mod_path} without register(core)")

    def run_config(self, cfg_path: str, extra_cmd: str | None) -> int:
        """Loads config.yaml, loads modules, publishes commands in order."""
        typer.echo(f"RUNNING FILE: {__file__}")
        cfg = self._load_yaml(cfg_path)
        typer.echo(f"Captain {cfg.get('version', self.version)}")

        mods = cfg.get("modules", [])
        if not isinstance(mods, list):
            typer.echo("Error: 'modules' must be a list", err=True)
            return 2
        self._load_modules(mods)

        cmds = cfg.get("commands", [])
        if not isinstance(cmds, list):
            typer.echo("Error: 'commands' must be a list", err=True)
            return 2
        if not all(isinstance(cmd, str) for cmd in cmds):
            typer.echo("Error: each command in 'commands' must be a string", err=True)
            return 2

        if extra_cmd is not None:  # Check if single command or run all at once
            selected = [extra_cmd]
        else:
            selected = cmds

        self.allowed_cmds_list = selected[:]
        self.allowed_cmds_set = set(selected)

        for cmd in self.allowed_cmds_list:
            self.publish(f"command:{cmd}")

        return 0


core = Core()


@app.command(help="Run Captain according to config.yaml (loads modules and publishes commands)")
def run(  # pylint: disable=missing-function-docstring
    config: str = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to config.yaml",
    ),
    extra_cmd: str | None = typer.Option(
        None,
        "--run",
        "-r",
        help='Additional command, e.g. "req"',
    ),
):
    raise SystemExit(core.run_config(config, extra_cmd))

if __name__ == "__main__":
    app()