from sqlalchemy import MetaData

__all__ = (
    "Base",
    "GATHERS_TABLE_NAME",
    "GUILDS_TABLE_NAME",
    "PINNED_PLAYERS_TABLE_NAME",
    "RESULTS_TABLE_NAME",
    "USERS_TABLE_NAME",
)

metadata = MetaData()


GATHERS_TABLE_NAME = "gathers"
GUILDS_TABLE_NAME = "guilds"
PINNED_PLAYERS_TABLE_NAME = "pinned_players"
RESULTS_TABLE_NAME = "results"
USERS_TABLE_NAME = "users"
