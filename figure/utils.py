from typing import Callable, ParamSpec, TypeVar

import matplotlib as mpl

__all__ = ("styled",)

P = ParamSpec("P")
T = TypeVar("T")


def styled(filepath: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """mpl.rc_contextを使ってmatplotlibのスタイルを変更するデコレータ.
    グローバルではなく関数内でのみスタイルを変更する.

    Parameters
    ----------
    filepath : str
        スタイルファイルのパス

    Returns
    -------
    Callable[[Callable[P, T]], Callable[P, T]]
        デコレータ
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with mpl.rc_context(fname=filepath):
                return func(*args, **kwargs)

        return wrapper

    return decorator
