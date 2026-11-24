#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Figures of bench/README.md, from the captures and reports in bench/results/.

Needs the eight captures `<backend>_<model>.csv` written by `just measure`.
"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent / "results"
MODELS = {"kws": "Keyword spotting", "ad": "Anomaly detection",
          "ic": "Image classification", "vww": "Visual wake words"}
BACKENDS = {"axon": ("Axon NPU", "#2a78d6"), "tflm": ("TFLM, CPU", "#eb6834")}
INK, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
DT = 1e-5      # s per sample
YMAX = 10.0    # mA: the wake-up bursts of the PPK2 go above


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5, colors=MUTED, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)


def report(backend, model):
    """Width in ms and median charge in µC of the D0 regions, from the report."""
    text = (HERE / f"{backend}_{model}.txt").read_text()
    line = next(l for l in text.splitlines() if l.startswith("D0 "))
    return float(re.search(r"width\s+([\d.]+)", line).group(1)), float(re.search(r"median ([\d.]+)", line).group(1))


def bars(index, unit, what, out):
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2), facecolor=SURFACE)
    for ax, (model, title) in zip(axes.flat, MODELS.items()):
        values = [report(backend, model)[index] for backend in BACKENDS]
        drawn = ax.bar(range(2), values, width=0.58, color=[c for _, c in BACKENDS.values()])
        for bar, value in zip(drawn, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:,.0f}" if value >= 100 else f"{value:.3g}",
                    ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.set_title(f"{title}\n{values[1] / values[0]:.1f} times less on Axon", fontsize=10, color=INK, loc="left")
        ax.set_ylim(0, max(values) * 1.15)
        ax.set_xlim(-0.8, 1.8)
        ax.set_xticks([])
        ax.set_ylabel(unit, fontsize=9, color=MUTED)
        ax.locator_params(axis="y", nbins=5)
        style(ax)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in BACKENDS.values()],
               labels=[n for n, _ in BACKENDS.values()], loc="lower center", ncol=2, frameon=False,
               fontsize=9.5, labelcolor=INK)
    fig.suptitle(f"{what} per inference on the nRF54LM20B", fontsize=11.5, color=INK, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(HERE / out, dpi=150)


def capture(backend, model):
    """Current in µA, and the D0 region with the median charge."""
    rows = np.loadtxt(HERE / f"{backend}_{model}.csv", delimiter=",", skiprows=1, usecols=(1, 3))
    current, d0 = rows[:, 0], rows[:, 1].astype(np.int8)
    edges = np.flatnonzero(np.diff(d0)) + 1
    rises = [e for e in edges if d0[e] == 1]
    falls = [e for e in edges if d0[e] == 0 and e > rises[0]]
    regions = list(zip(rises, falls))
    charge = [current[a:b].sum() * DT for a, b in regions]
    return current, regions[int(np.argsort(charge)[len(charge) // 2])]


def traces(out):
    """Raw samples of one inference per backend, the two of a model on the same scales."""
    fig = plt.figure(figsize=(12, 8.4), facecolor=SURFACE)
    for sub, (model, title) in zip(fig.subfigures(2, 2, wspace=0.03, hspace=0.04).flat, MODELS.items()):
        sub.set_facecolor(SURFACE)
        axes = sub.subplots(2, 1, sharex=True, sharey=True)
        captures = {backend: capture(backend, model) for backend in BACKENDS}
        span = max(b - a for _, (a, b) in captures.values()) * DT * 1e3
        for ax, (backend, (name, colour)) in zip(axes, BACKENDS.items()):
            current, (a, b) = captures[backend]
            lo, hi = a - int(0.06 * span / 1e3 / DT), a + int(1.08 * span / 1e3 / DT)
            t = (np.arange(lo, hi) - a) * DT * 1e3
            y = current[lo:hi] / 1000
            width = (b - a) * DT * 1e3
            inside = (t >= 0) & (t <= width)
            ax.plot(t, np.minimum(y, YMAX), color=colour, linewidth=0.5, alpha=0.4)
            ax.plot(t[inside], np.minimum(y[inside], YMAX), color=colour, linewidth=0.6)
            ax.fill_between(t, 0, np.minimum(y, YMAX), where=inside, color=colour, alpha=0.2, linewidth=0)
            ax.hlines(-0.55, 0, width, color=INK, linewidth=2.4)
            peak = y[(t >= -0.02 * span) & (t <= width)].max()
            ax.set_title(f"{name}: {width:.2f} ms, {current[a:b].sum() * DT:.1f} µC"
                         + (f", peak {peak:.0f} mA" if peak > YMAX else ""), fontsize=9, color=INK, loc="left")
            ax.set_ylim(-1.1, YMAX)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
            ax.set_ylabel("mA", fontsize=9, color=MUTED)
            style(ax)
        axes[1].set_xlabel("ms", fontsize=8.5, color=MUTED)
        sub.suptitle(title, fontsize=11.5, color=INK, x=0.02, ha="left")
        sub.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.11, hspace=0.38)
    fig.savefig(HERE / out, dpi=150)


bars(0, "ms", "Time", "latency.png")
bars(1, "µC", "Charge", "charge.png")
traces("traces.png")
