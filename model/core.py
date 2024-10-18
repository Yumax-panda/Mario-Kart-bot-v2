from sqlalchemy import MetaData

__all__ = (
    "Base",
    "GATHERS_TABLE_NAME",
    "GUILDS_TABLE_NAME",
    "NSO_TOKENS_TABLE_NAME",
    "PINNED_PLAYERS_TABLE_NAME",
    "REQUESTS_TABLE_NAME",
    "RESULTS_TABLE_NAME",
    "SESSION_TOKENS_TABLE_NAME",
    "USERS_TABLE_NAME",
)

metadata = MetaData()


GATHERS_TABLE_NAME = "gathers"
GUILDS_TABLE_NAME = "guilds"
NSO_TOKENS_TABLE_NAME = "nso_tokens"
PINNED_PLAYERS_TABLE_NAME = "pinned_players"
REQUESTS_TABLE_NAME = "requests"
RESULTS_TABLE_NAME = "results"
SESSION_TOKENS_TABLE_NAME = "session_tokens"
USERS_TABLE_NAME = "users"
