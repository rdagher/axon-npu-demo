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
DT = 1e-5        # s per sample
YMAX = 6.0       # mA: the wake-up bursts of the PPK2 go above
SMOOTH = 20      # samples of the moving average, 0.2 ms
captures = {}


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8, colors=MUTED, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)


def capture(backend, model):
    """Current in µA, the regions where D0 is high, and the one with the median charge."""
    if (backend, model) not in captures:
        rows = np.loadtxt(HERE / f"{backend}_{model}.csv", delimiter=",", skiprows=1, usecols=(1, 3))
        current, d0 = rows[:, 0], rows[:, 1].astype(np.int8)
        edges = np.flatnonzero(np.diff(d0)) + 1
        rises = [e for e in edges if d0[e] == 1]
        falls = [e for e in edges if d0[e] == 0 and e > rises[0]]
        regions = list(zip(rises, falls))
        charge = [current[a:b].sum() * DT for a, b in regions]
        captures[backend, model] = current, regions, int(np.argsort(charge)[len(charge) // 2]), charge
    return captures[backend, model]


def trace(ax, backend, model, span, detailed):
    """One inference, from just before its start, over `span` ms."""
    name, colour = BACKENDS[backend]
    current, regions, i, charge = capture(backend, model)
    a, b = regions[i]
    lo, hi = a - int(0.08 * span / 1e3 / DT), a + int(1.12 * span / 1e3 / DT)
    t = (np.arange(lo, hi) - a) * DT * 1e3
    y = np.convolve(current[lo:hi] / 1000, np.ones(SMOOTH) / SMOOTH, mode="same")
    width = (b - a) * DT * 1e3
    inside = (t >= 0) & (t <= width)
    ax.plot(t, np.minimum(y, YMAX), color=colour, linewidth=1.0, alpha=0.35)
    ax.plot(t[inside], np.minimum(y[inside], YMAX), color=colour, linewidth=1.3)
    ax.fill_between(t, 0, np.minimum(y, YMAX), where=inside, color=colour, alpha=0.28, linewidth=0)
    ax.hlines(-0.32, 0, width, color=INK, linewidth=2.5)
    label = f"{name}: {width:.2f} ms, {charge[i]:.1f} µC"
    if detailed:
        label += f", mean {current[a:b].mean() / 1000:.2f} mA"
        if y.max() > YMAX:
            peak = t[int(np.argmax(y))]
            ax.annotate(f"wake-up burst, to {y.max():.0f} mA", xy=(peak, YMAX),
                        xytext=(peak + 0.04 * span, YMAX * 0.82), fontsize=8, color=MUTED,
                        arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.6))
        if i + 1 < len(regions) and (regions[i + 1][0] - a) * DT * 1e3 < 1.1 * span:
            ax.text((regions[i + 1][0] - a) * DT * 1e3, 4.7, "next inference, after a 50 ms sleep",
                    fontsize=8, color=MUTED, ha="center")
    ax.set_title(label, fontsize=9.5 if detailed else 9, color=INK, loc="left")
    ax.set_ylim(-0.7, YMAX)
    ax.set_yticks([0, 2, 4, 6])
    ax.set_ylabel("mA", fontsize=9, color=MUTED)
    style(ax)


def span(model):
    """Width in ms of the longer of the two inferences of a model."""
    return max(r[i][1] - r[i][0] for _, r, i, _ in (capture(b, model) for b in BACKENDS)) * DT * 1e3


def trace_one(model, out):
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.4), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, backend in zip(axes, BACKENDS):
        trace(ax, backend, model, span(model), True)
    axes[1].set_xlabel("Time from the start of the inference (ms). Black bar: the D0 marker", fontsize=9, color=MUTED)
    fig.suptitle(f"Current of the nRF54LM20B during one {MODELS[model].lower()} inference",
                 fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(HERE / out, dpi=160)


def trace_all(out):
    fig = plt.figure(figsize=(12, 8.2), facecolor=SURFACE)
    for sub, (model, title) in zip(fig.subfigures(2, 2, wspace=0.03, hspace=0.04).flat, MODELS.items()):
        sub.set_facecolor(SURFACE)
        axes = sub.subplots(2, 1, sharex=True, sharey=True)
        for ax, backend in zip(axes, BACKENDS):
            trace(ax, backend, model, span(model), False)
        axes[1].set_xlabel("ms", fontsize=8.5, color=MUTED)
        sub.suptitle(title, fontsize=11, color=INK, x=0.02, ha="left")
        sub.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.11, hspace=0.38)
    fig.savefig(HERE / out, dpi=150)


def time_bars(out):
    fig, axes = plt.subplots(1, len(MODELS), figsize=(9, 2.9), facecolor=SURFACE)
    for ax, (model, title) in zip(axes, MODELS.items()):
        values = []
        for backend in BACKENDS:
            line = next(l for l in (HERE / f"{backend}_{model}.txt").read_text().splitlines() if l.startswith("D0 "))
            values.append(float(re.search(r"width\s+([\d.]+) ms", line).group(1)))
        bars = ax.bar(range(len(values)), values, width=0.62, color=[c for _, c in BACKENDS.values()])
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:,.0f}" if value >= 100 else f"{value:.3g}",
                    ha="center", va="bottom", fontsize=9, color=INK)
        ax.set_title(f"{title}\n{values[1] / values[0]:.1f} times less on Axon", fontsize=9, color=INK, loc="left")
        ax.set_ylim(0, max(values) * 1.15)
        ax.set_xticks([])
        style(ax)
    axes[0].set_ylabel("ms", fontsize=9, color=MUTED)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in BACKENDS.values()],
               labels=[n for n, _ in BACKENDS.values()], loc="lower center", ncol=2, frameon=False,
               fontsize=9, labelcolor=INK)
    fig.suptitle("Time per inference on the nRF54LM20B (each panel has its own scale)", fontsize=11, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(HERE / out, dpi=160)


trace_one("kws", "trace_kws.png")
trace_all("traces.png")
time_bars("latency.png")
