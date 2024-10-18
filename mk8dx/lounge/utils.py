from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Literal, TypeVar

__all__ = (
    "BaseModel",
    "Search",
)

T = TypeVar("T")
PayloadT = TypeVar("PayloadT")


class BaseModel(metaclass=ABCMeta):
    """Lounge APIモデルの基底クラス."""

    __slots__ = ()

    @abstractmethod
    def __init__(self, data: dict) -> None:
        """モデルを初期化する.

        Parameters
        ----------
        data : dict
            モデルのdict表現. Lounge APIのレスポンスと同様の形式.
        """
        ...

    @abstractmethod
    def to_dict(self):
        """モデルをdictに変換する.

        Returns
        -------
        dict
            モデルのdict表現. Lounge APIのレスポンスと同様の形式.
        """
        ...


SearchCategory = Literal["mkc", "switch", "discord"]


class Search:

    __slots__ = ("category", "value")

    if TYPE_CHECKING:
        category: SearchCategory
        value: str | int

    def __init__(self, category: SearchCategory, value: str | int) -> None:
        self.category = category
        self.value = value

    @property
    def query(self) -> str:
        return f"{self.category}={self.value}"
