from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, TypedDict

import matplotlib.pyplot as plt
import numpy as np

from .utils import styled

__all__ = ("create_result_graph",)

if TYPE_CHECKING:

    class Result(TypedDict):
        score: int
        enemyScore: int

else:
    Result = dict[str, int]


@styled("figure/styles/result.mplstyle")
def create_result_graph(results: list[Result]) -> BytesIO:
    """戦績のグラフを作成する.

    Parameters
    ----------
    results : list[Result]
        戦績のリスト

    Returns
    -------
    BytesIO
        作成したグラフのバイナリデータ
    """
    xs = np.arange(len(results))
    win_or_lose = np.sign(np.array([result["score"] - result["enemyScore"] for result in results]))
    history = np.cumsum(win_or_lose)
    plt.plot(history, label="Wins - Loses")
    _, _, y_min, y_max = plt.axis()
    plt.grid(visible=True, which="both", axis="both", color="gray")
    plt.legend(bbox_to_anchor=(0, 1))
    plt.fill_between(xs, y_min, 0, facecolor="#87ceeb", alpha=0.3)
    plt.fill_between(xs, 0, y_max, facecolor="#ffa07a", alpha=0.3)
    plt.title("Win&Lose History")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)

    plt.clf()
    plt.close()
    return buffer
