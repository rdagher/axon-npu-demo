#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bar charts from the `west ppk2 attribute` reports in bench/results/."""

import re
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent / "results"
MODELS = {"kws": "Keyword spotting", "ad": "Anomaly detection",
          "ic": "Image classification", "vww": "Visual wake words"}
BACKENDS = {"axon": ("Axon NPU", "#2a78d6"), "tflm": ("TFLM + CMSIS-NN, CPU", "#eb6834")}
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"


def read(backend, model):
    line = next(l for l in (HERE / f"{backend}_{model}.txt").read_text().splitlines() if l.startswith("D0 "))
    width = float(re.search(r"width\s+([\d.]+) ms", line).group(1))
    charge = float(re.search(r"median ([\d.]+)", line).group(1))
    return width, charge


def chart(index, unit, title, out):
    fig, axes = plt.subplots(1, len(MODELS), figsize=(9, 2.9), facecolor=SURFACE)
    for ax, (model, name) in zip(axes, MODELS.items()):
        values = [read(b, model)[index] for b in BACKENDS]
        bars = ax.bar(range(len(BACKENDS)), values, width=0.62, color=[c for _, c in BACKENDS.values()])
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:,.0f}" if value >= 100 else f"{value:.3g}", ha="center", va="bottom",
                    fontsize=9, color=INK)
        ax.set_title(f"{name}\n{values[1] / values[0]:.1f}× less on Axon", fontsize=9, color=INK, loc="left")
        ax.set_ylim(0, max(values) * 1.15)
        ax.set_xticks([])
        ax.set_facecolor(SURFACE)
        ax.tick_params(axis="y", labelsize=8, colors=MUTED, length=0)
        ax.grid(axis="y", color="#e4e3df", linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)
    axes[0].set_ylabel(unit, fontsize=9, color=MUTED)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in BACKENDS.values()],
               labels=[n for n, _ in BACKENDS.values()], loc="lower center", ncol=2, frameon=False,
               fontsize=9, labelcolor=INK)
    fig.suptitle(title, fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(HERE / out, dpi=160)


chart(0, "ms", "Time per inference, nRF54LM20B (each panel has its own scale)", "latency.png")
chart(1, "µC", "Charge per inference, median, nRF54LM20B (each panel has its own scale)", "charge.png")
