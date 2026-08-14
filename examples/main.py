"""
main.py — Pigeon's entry point, written the "best practice" way.

WHAT THIS FILE DOES
-------------------
1. Configures logging so you can see what the bot is doing.
2. Defines a Bot subclass (the standard pattern — you hook into its lifecycle).
3. AUTOMATICALLY loads every cog file in the `cogs/` folder — you never have to
   maintain a hand-written list of cogs.
4. Syncs slash commands to Discord.
5. Starts the bot using a token from the environment.

Run it with:  python main.py

A "cog" is just a file that groups related commands/listeners into a class.
Each cog file must end with an `async def setup(bot)` function (see cogs/*.py).
This file discovers and loads them all on startup.
"""

from __future__ import annotations

import asyncio
import logging
import os
import pathlib
import traceback

import discord
from discord.ext import commands

log = logging.getLogger("pigeon")

# Where cog files live, relative to this file. Every .py file in here (that isn't
# private, i.e. doesn't start with "_") is loaded automatically at startup.
COGS_DIR = pathlib.Path(__file__).parent / "cogs"

# During development, syncing commands to a single test guild is INSTANT.
# Global sync (guild=None) can take up to an hour to show up in Discord.
# Put your server's ID here while developing; set to None to sync globally.
DEV_GUILD_ID: int | None = None  # e.g. 123456789012345678


class Pigeon(commands.Bot):
    def __init__(self) -> None:
        # Intents = which events Discord will send you. Intents.default() is the
        # non-privileged baseline and is enough for slash commands.
        # Privileged intents (members, message_content, presences) must ALSO be
        # enabled in the Developer Portal → Bot → Privileged Gateway Intents.
        # Only turn on what a feature actually needs.
        intents = discord.Intents.default()
        # intents.members = True          # needed to see member joins / member data
        # intents.message_content = True  # needed to READ message text (starboard, etc.)

        super().__init__(
            command_prefix=commands.when_mentioned,  # we use slash commands; this is a fallback
            intents=intents,
            help_command=None,  # we don't use the old text-based help
        )

    async def setup_hook(self) -> None:
        """Runs ONCE after login but before the bot is ready. The correct place
        to load cogs and sync commands."""
        await self._load_all_cogs()

        # Sync the slash-command tree to Discord.
        if DEV_GUILD_ID is not None:
            guild = discord.Object(id=DEV_GUILD_ID)
            # Copy globally-defined commands into the dev guild and sync there —
            # instant, so you see changes immediately while developing.
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d commands to dev guild %s", len(synced), DEV_GUILD_ID)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d commands globally (may take up to 1h to appear)", len(synced))

    async def _load_all_cogs(self) -> None:
        """Import every cogs/*.py as an extension. One broken cog won't stop the
        others from loading — we log its traceback and carry on."""
        if not COGS_DIR.exists():
            log.warning("No cogs/ directory found at %s", COGS_DIR)
            return
        for file in sorted(COGS_DIR.glob("*.py")):
            if file.stem.startswith("_"):
                continue  # skip __init__.py and private helpers
            extension = f"cogs.{file.stem}"
            try:
                await self.load_extension(extension)
                log.info("Loaded cog: %s", extension)
            except Exception:
                log.error("Failed to load cog %s:\n%s", extension, traceback.format_exc())

    async def on_ready(self) -> None:
        # on_ready can fire more than once (on reconnects) — don't do one-time
        # setup here; use setup_hook for that. This is just a friendly log line.
        log.info("Logged in as %s (id: %s) — in %d guild(s)", self.user, self.user.id, len(self.guilds))


async def main() -> None:
    # discord.py ships a sensible logging setup; this colourises logs nicely.
    discord.utils.setup_logging(level=logging.INFO)

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN is not set. Add it as an environment variable / Codespaces secret.")

    bot = Pigeon()
    # `async with` guarantees the bot closes its network sessions cleanly on exit.
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Ctrl+C — exit quietly
