from . import GatherRepository, GuildRepository, PinnedPlayerRepository, ResultRepository, UserRepository

__all__ = ("Repository",)


class Repository(
    GatherRepository,
    GuildRepository,
    PinnedPlayerRepository,
    ResultRepository,
    UserRepository,
):
    pass
