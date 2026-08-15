import asyncio
import logging
import os
import pathlib
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv

log = logging.getLogger("pigeon")

USER_COGS_DIR = pathlib.Path(__file__).parent / "cogs"

CORE_COGS_DIR = pathlib.Path(__file__).parent / "core"

DEV_GUILD: int | None = 1528913550028836984

load_dotenv()


class Pigeon(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=";",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        await self.load_cogs()

        if DEV_GUILD is not None:
            guild = discord.Object(id=DEV_GUILD)

            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("[DEV] Commands synced: %d", len(synced))
        else:
            synced = await self.tree.sync()
            log.info("Commands synced: %d", len(synced))

    async def load_cogs(self) -> None:

        # "hidden" commands. just owner only commands
        for core in sorted(CORE_COGS_DIR.glob("*.py")):
            if core.stem.startswith("_"):  # ignore init files or not finished files
                continue
            corecog = f"core.{core.stem}"
            try:
                await self.load_extension(corecog)
                log.info("Loaded hidden cog: %s", corecog)
            except Exception:  # noqa: BLE001
                log.error("Failed to load %s:\n %s", corecog, traceback.format_exc())

        # normal commands, loads anything in cogs/
        if not USER_COGS_DIR.exists():
            log.warning("Unable to locate cogs at %s", USER_COGS_DIR)
            return
        loaded = 0
        for cog in sorted(USER_COGS_DIR.glob("*.py")):
            if cog.stem.startswith("_"):  # ignore init files or not finished files
                continue
            extension = f"cogs.{cog.stem}"
            try:
                await self.load_extension(extension)
                loaded += 1
            except Exception:  # noqa: BLE001
                log.error("Failed to load %s:\n %s", extension, traceback.format_exc())

        log.info("Cogs: %s", loaded)

    async def on_ready(self) -> None:
        log.info("Connected to Discord as %s (id: %s)", self.user, self.user.id)


async def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit(log.critical("No Discord token found. Please set it!"))

    bot = Pigeon()

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Keyboard shutdown detected. Shutting down...")
