from typing import Literal, TypeAlias

__all__ = (
    "Locale",
    "LocaleDict",
)

Locale = Literal["ja", "en-US"]
LocaleDict: TypeAlias = dict[Locale, str]
