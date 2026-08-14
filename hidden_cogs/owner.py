# purposely not app command as don't need other people seeing these commands.

from __future__ import annotations

import logging
import time
import sys
import os

import discord
from discord.ext import commands

log = logging.getLogger("pigeon(Owner)") # identify all logs from this cog

class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        log.info("Requested shutdown from Discord client, trying...")
        msg = await ctx.send("Attempting shutdown...")
        try:
            await self.bot.close()
            log.info("Great Success!")
        except Exception as e:
            log.error("Shutdown failed with reason: %s", e)
            await msg.edit(content="Shutdown failed. Refer to logs.")

async def setup(bot):
    await bot.add_cog(Owner(bot))