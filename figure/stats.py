from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

from utils.constants import CURRENT_SEASON

from .utils import styled

__all__ = ("create_mmr_history_graph",)


@styled("figure/styles/stats.mplstyle")
def create_mmr_history_graph(mmr_history: list[int], season: int | None = None) -> BytesIO:
    if season is None:
        season = CURRENT_SEASON

    if season == 5:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 11000, 13000, 14000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 12000]
    elif season == 6 or season == 7:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 15000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 11000, 13000]
    else:
        ranks = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 17000]
        colors_between = [1000, 3000, 5000, 7000, 9000, 11000, 13000, 15000]
        colors = [
            "#817876",
            "#E67E22",
            "#7D8396",
            "#F1C40F",
            "#3FABB8",
            "#286CD3",
            "#D51C5e",
            "#9CCBD6",
            "#0E0B0B",
            "#A3022C",
        ]

    if season not in list(range(8, CURRENT_SEASON + 1)):
        colors = [
            "#817876",
            "#E67E22",
            "#7D8396",
            "#F1C40F",
            "#3FABB8",
            "#286CD3",
            "#9CCBD6",
            "#0E0B0B",
            "#A3022C",
        ]

    xs = np.arange(len(mmr_history))
    lines = plt.plot(mmr_history)
    xmin, xmax, ymin, ymax = plt.axis()
    plt.ylabel("MMR")
    plt.grid(True, which="both")

    for i in range(len(ranks)):
        if ranks[i] > ymax:
            continue
        maxfill = ymax
        if i + 1 < len(ranks):
            if ranks[i] < ymin and ranks[i + 1] < ymin:
                continue
            if ranks[i + 1] < ymax:
                maxfill = ranks[i + 1]
        if ranks[i] < ymin:
            minfill = ymin
        else:
            minfill = ranks[i]
        plt.fill_between(xs, minfill, maxfill, color=colors[i])
        divide = [i for i in colors_between if minfill <= i <= maxfill]
        plt.hlines(divide, xmin, xmax, colors="snow", linestyle="solid", linewidth=1)

    plt.fill_between(xs, ymin, mmr_history, facecolor="#212121", alpha=0.4)
    fp = BytesIO()
    plt.savefig(fp, format="png", bbox_inches="tight")
    fp.seek(0)
    plt.clf()
    plt.close()
    return fp
