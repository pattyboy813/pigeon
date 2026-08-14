import os
import asyncio
import pathlib
import traceback
import logging
import time
from dotenv import load_dotenv

import discord
from discord.ext import commands

log = logging.getLogger("pigeon")

COGS_DIR = pathlib.Path(__file__).parent / "cogs"

HIDDEN_COGS_DIR = pathlib.Path(__file__).parent / "hidden_cogs"

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
        for hcog in sorted(HIDDEN_COGS_DIR.glob("*.py")): 
            if hcog.stem.startswith("_"): # ignore init files or not finished files
                continue
            hextension = f"hidden_cogs.{hcog.stem}"
            try:
                await self.load_extension(hextension)
                log.info("Loaded hidden cog: %s", hextension)
            except Exception:
                log.error("Failed to load %s:\n %s", hextension, traceback.format_exc())

        # normal commands, loads anything in cogs/ 
        if not COGS_DIR.exists():
            log.warning("Unable to locate cogs at %s", COGS_DIR)
            return
        loaded = 0
        for cog in sorted(COGS_DIR.glob("*.py")):
            if cog.stem.startswith("_"): # ignore init files or not finished files
                continue
            extension = f"cogs.{cog.stem}"
            try:
                await self.load_extension(extension)
                loaded += 1
            except Exception:
                log.error("Failed to load %s:\n %s", extension, traceback.format_exc())
        
        log.info("Cogs: %s", loaded)
    
    async def on_ready(self) -> None:
        log.info("Connected to Discord as %s (id: %s)", self.user, self.user.id)

async def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("No Discord token found. Unable to connect")
    
    bot = Pigeon()

    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Keyboard shutdown detected. Shutting down...")