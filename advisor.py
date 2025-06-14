#!/usr/bin/env python3
"""pycri.advisor
A *very* small proof‑of‑concept ML "resource oracle" that watches a
container's cgroup stats and prints suggestions to raise / lower the
memory limit.

⚠️  This is **demo code** – not production‑grade autoscaling logic.
"""
from __future__ import annotations

import argparse
import pathlib
import time
from collections import deque

import numpy as np
from sklearn.linear_model import LinearRegression
from rich.console import Console
from rich.table import Table

console = Console()


class MemoryAdvisor:  # noqa: D101 – self‑describing class
    def __init__(self, cgroup_path: pathlib.Path, horizon: int = 60, window: int = 120):
        self.cg_path = cgroup_path
        self.horizon = horizon
        self.window = window  # seconds of history to keep
        self.samples: deque[tuple[float, int]] = deque(maxlen=window)
        self.model = LinearRegression()

    # ---------------------------------------------------------------------
    # Public helpers

    def sample(self) -> None:
        """Read memory.current (v2) or memory.usage_in_bytes (v1)."""
        now = time.time()
        try:  # cgroup v2
            txt = (self.cg_path / "memory.current").read_text()
        except FileNotFoundError:  # v1 fallback
            txt = (self.cg_path / "memory.usage_in_bytes").read_text()
        self.samples.append((now, int(txt.strip())))

    def suggest(self) -> tuple[str, int] | None:
        """Return (action, new_limit) or None if no change suggested."""
        if len(self.samples) < 10:
            return None  # need more data

        # prepare X=time (s ago), y=RSS bytes
        t0 = self.samples[0][0]
        X = np.array([[t - t0] for t, _ in self.samples])
        y = np.array([rss for _, rss in self.samples])
        self.model.fit(X, y)

        future = np.array([[X[-1][0] + self.horizon]])
        predicted = int(self.model.predict(future).item())

        curr_limit = self._current_limit()
        if curr_limit is None:
            return None

        # thresholds: <50 % → shrink; >90 % soon → grow
        if predicted > 0.9 * curr_limit:
            return ("raise", int(predicted * 1.2))
        if predicted < 0.5 * curr_limit:
            return ("lower", int(predicted * 0.8))
        return None

    # ------------------------------------------------------------------
    # Internals

    def _current_limit(self) -> int | None:
        try:
            txt = (self.cg_path / "memory.max").read_text()
            return int(       # "max" means unlimited
                txt.strip() if txt.strip() != "max" else 1 << 63
            )
        except FileNotFoundError:
            try:
                txt = (self.cg_path / "memory.limit_in_bytes").read_text()
                return int(txt.strip())
            except FileNotFoundError:
                return None


# ----------------------------------------------------------------------
# CLI helper


def main() -> None:  # noqa: D401 – simple CLI
    p = argparse.ArgumentParser(description="PyCRI memory advisor (demo)")
    p.add_argument("cgroup", type=pathlib.Path, help="/sys/fs/cgroup/<cid>")
    p.add_argument("--interval", type=int, default=5, help="sampling interval (s)")
    args = p.parse_args()

    advisor = MemoryAdvisor(args.cgroup)
    table = Table("time", "rss", "suggestion")

    while True:
        advisor.sample()
        suggestion = advisor.suggest()
        now = time.strftime("%H:%M:%S")
        rss = advisor.samples[-1][1]
        action = (
            f"{suggestion[0]} → {suggestion[1] // (1024 ** 2)} MiB"
            if suggestion
            else "‑"
        )
        table.add_row(now, f"{rss // (1024 ** 2)} MiB", action)
        console.clear()
        console.print(table)
        time.sleep(args.interval)


if __name__ == "__main__":  # pragma: no cover
    main()
