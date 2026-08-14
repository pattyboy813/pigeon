import os
import asyncio
import pathlib
import traceback
import logging

import discord
from discord.ext import commands

log = logging.getLogger("pigeon")

COGS_DIR = pathlib.Path(__file__).parent / "cogs"

DEV_GUILD: int | None = 1528913550028836984

class Pigeon(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=commands.when_mentioned,
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
        if not COGS_DIR.exists():
            log.warning("Unable to locate cogs at %s", COGS_DIR)
            return
        loaded = 0
        for file in sorted(COGS_DIR.glob("*.py")):
            if file.stem.startswith("_"):
                continue # ignore init file
            extension = f"cogs.{file.stem}"
            try:
                await self.load_extension(extension)
                loaded += 1
            except Exception:
                log.error("Failed to load %s: %s", extension, traceback.format_exc())
        
        log.info("Cogs: %s", loaded)
    
    async def on_ready(self) -> None:
        log.info("Connected to Discord as %s (id: %s)", self.user, self.user.id)

async def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("No Discord Token detected. Please ensure this has been set...")
    
    bot = Pigeon()

    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Keyboard shutdown detected. Shutting down gracefully...")