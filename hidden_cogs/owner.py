# purposely not app command as don't need other people seeing these commands.

from __future__ import annotations

import logging
import os
import traceback

from discord.ext import commands

log = logging.getLogger("pigeon(Owner)")  # identify all logs from this cog


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        log.info("Requested shutdown from Discord client, trying...")
        msg = await ctx.send("Attempting shutdown...")
        try:
            await self.bot.close()  # close connection with Discord
            log.info("Great Success!")
        except Exception:  # this "should" not be needed but just incase
            log.error("Shutdown failed with reason: %s", traceback.format_exc())
            await msg.edit(content="Shutdown failed. Refer to logs.")

    @commands.is_owner()
    @commands.command(name="reload")  # reload cog (not hidden ones)
    async def reload_cog(self, ctx, cog_name: str):
        log.warning("Cog reload requested for %s", cog_name)
        if not cog_name.startswith("cogs."):
            if os.path.exists(f"cogs/{cog_name}.py"):
                log.info("Cog '%s' found!", cog_name)
                cog_name = f"cogs.{cog_name}"
                
                msg = await ctx.send(f"Reloading `{cog_name}`...")
                try:
                    await self.bot.reload_extension(cog_name)
                    log.info("Successfully reloaded '%s'", cog_name)
                    await msg.edit(content=f"`{cog_name}` has been successfully reloaded!")
                except commands.ExtensionNotLoaded:
                    log.error("Cog '%s' has not been loaded yet. Restart bot to load cog.")
                    await msg.edit(
                        content=f"`{cog_name}` has not been loaded! Load it during bot startup!"
                    )
                except Exception:
                    log.error("Failed to load '%s':\n %s", cog_name, traceback.format_exc())
                    await msg.edit(
                        content=f"Unable to reload `{cog_name}`. Refer to log for details."
                    )
            else:
                log.error("No cog found for '%s' in cogs directory.", cog_name)
                await ctx.send(f"Unable to locate  `{cog_name}` in cogs directory")



async def setup(bot):
    await bot.add_cog(Owner(bot))
