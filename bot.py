from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from discord import Activity, ActivityType, Intents, Status
from discord.ext import commands

from ui.bookmark import BookmarkView

try:
    import _config
except ImportError:
    pass

from handler import Handler
from mk8dx import LoungeClient
from repository import Config
from service import Service

fmt = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt, handlers=[logging.StreamHandler()])

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.WARN)

if TYPE_CHECKING:
    from discord import Guild

    from handler.types.handler import Handler as IHandler


class Bot(commands.AutoShardedBot):

    if TYPE_CHECKING:
        h: IHandler
        _token: str
        persistent_views_added: bool
        session: ClientSession

    def __init__(
        self,
        token: str,
        h: IHandler,
        command_prefix: str = "!",
        case_insensitive: bool = True,
        help_command: commands.HelpCommand | None = None,
        owner_id: int | None = None,
    ) -> None:
        # これはbotの機能に関する内容で開発者に依存されないため, ここで設定する
        intents = Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            case_insensitive=case_insensitive,
            help_command=help_command,
            owner_id=owner_id,
        )
        self.h = h
        self._token = token
        self.persistent_views_added = False

    async def close(self) -> None:
        await super().close()
        await self.h.session.close()

    async def login(self, token: str) -> None:
        await super().login(token)

        await self.setup()

        return

    async def setup(self) -> None:

        if not hasattr(self.h, "session"):
            self.h.session = ClientSession()

        if not self.persistent_views_added:
            for cls in (BookmarkView,):
                self.add_view(cls())
            self.persistent_views_added = True

        await self.h.setup_repository()

    async def on_ready(self):
        await self.update_activity()
        logging.info(f"Bot is ready as {self.user}.")

    async def update_activity(self):
        activity = Activity(
            status=Status.online,
            type=ActivityType.watching,
            name=f"{len(self.guilds)} servers",
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, _: Guild):
        await self.update_activity()

    async def on_guild_remove(self, _: Guild):
        await self.update_activity()

    def run(self) -> None:
        extensions = [
            "cog.admin",
            "cog.bookmark",
            "cog.friend",
            # TODO: implement GameCog
            # "cog.game",
            "cog.recruit",
            "cog.result",
            "cog.team",
            "cog.utility",
        ]

        for extension in extensions:
            self.load_extension(extension)

        super().run(self._token)


class Container(containers.DeclarativeContainer):
    # TODO: configは全てjsonから読み込むようにする
    config = providers.Configuration()
    lc = providers.Singleton(LoungeClient)
    cfg = providers.Singleton(
        Config,
        user=config.db_user,
        password=config.db_password,
        host_name=config.db_hostname,
        port=config.db_port,
        db_name=config.db_name,
    )
    srv = providers.Singleton(Service, firebase_key=config.firebase_key, firebase_url=config.firebase_url)

    h = providers.Singleton(
        Handler,
        webhook_token=config.webhook_url,
        lc=lc,
        config=cfg,
        srv=srv,
    )

    bot = providers.Factory(
        Bot,
        token=config.bot_token,
        h=h,
        command_prefix=config.command_prefix,
        case_insensitive=True,
        help_command=None,
        owner_id=config.owner_id,
    )


@inject
def main(bot: Bot = Provide[Container.bot]) -> None:
    bot.run()


if __name__ == "__main__":
    container = Container()
    container.config.db_user.from_env("DB_USERNAME", default="root")
    container.config.db_password.from_env("DB_PASSWORD", default="password")
    container.config.db_hostname.from_env("DB_HOSTNAME", default="localhost")
    container.config.db_port.from_env("DB_PORT", as_=int, default=3306)
    container.config.db_name.from_env("DB_NAME", default="mkbot")
    container.config.firebase_key.from_env("FIREBASE_KEY", required=True)
    container.config.firebase_url.from_env("FIREBASE_URL", default="https://mariokart-c27da-default-rtdb.firebaseio.com/")
    container.config.webhook_url.from_env("WEBHOOK_URL", required=True)
    container.config.bot_token.from_env("BOT_TOKEN", required=True)
    container.config.command_prefix.from_env("COMMAND_PREFIX", default="!")
    container.config.owner_id.from_env("OWNER_ID", as_=int, default=815565736557936640)
    container.wire(modules=[__name__])

    main()
