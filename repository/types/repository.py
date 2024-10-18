from . import (
    GatherRepository,
    GuildRepository,
    NSOTokenRepository,
    PinnedPlayerRepository,
    RequestRepository,
    ResultRepository,
    SessionTokenRepository,
    UserRepository,
)

__all__ = ("Repository",)


class Repository(
    GatherRepository,
    GuildRepository,
    NSOTokenRepository,
    PinnedPlayerRepository,
    RequestRepository,
    ResultRepository,
    SessionTokenRepository,
    UserRepository,
):
    pass
