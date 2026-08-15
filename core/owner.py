# purposely not app command as don't need other people seeing these commands.

from __future__ import annotations

import logging
import os
import pathlib
import traceback

from discord.ext import commands

log = logging.getLogger("pigeon")  # identify all log for main pigeon

log_cog = logging.getLogger("pigeon(COG)")

COGS_DIR = pathlib.Path(__file__).parent.parent / "cogs"


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.group(
        invoke_without_command=True
    )  # command group for cog related commands
    async def cog(self, ctx):
        msg = (
            "```"
            "Cog commands:\n\n"
            "- ;cog list       | Show cogs and their status\n\n"
            "- ;cog reload     | Reload a specific cog\n"
            "  ;cog reload all | Reload all cogs in cogs directory"
            "```"
        )

        await ctx.send(msg)

    @cog.command(name="list")
    async def coglist(self, ctx):
        log_cog.info("REQUEST - List Cogs")

        if not COGS_DIR.exists():
            log_cog.error(
                f"Unable to locate cogs directory at {COGS_DIR}. Does it exists?"
            )
            await ctx.send("An error has occurred! Please check the logs.")
            return

        loaded = []
        unloaded = []

        for cog in sorted(COGS_DIR.glob("*.py")):
            if cog.stem.startswith("_"):
                continue

            extension = f"cogs.{cog.stem}"

            if extension in self.bot.extensions:
                loaded.append(f"`{cog.stem}`")
            else:
                unloaded.append(f"`{cog.stem}`")

        loaded_str = "\n".join(loaded) if loaded else "None"
        unloaded_str = "\n".join(unloaded) if unloaded else "None"

        loaded_num = len(loaded)
        unloaded_num = len(unloaded)

        log_cog.info("Identified %s loaded cogs", loaded_num)
        log_cog.info("Identitied %s unloaded cogs", unloaded_num)

        response = (
            "**Cogs**\n\n"
            f"Loaded ({loaded_num})\n{loaded_str}\n\n"
            f"Unloaded ({unloaded_num})\n{unloaded_str}\n\n"
        )

        await ctx.send(response)

    @cog.command(name="reload")
    async def cogreload(self, ctx, cog_name: str):
        if str.lower(cog_name) == "all":
            log_cog.info("REQUEST - Cog Reload | All")

            msg = await ctx.send("Reloading all cogs...")

            loaded = 0
            failed = 0

            for cog in sorted(COGS_DIR.glob("*.py")):
                if cog.stem.startswith("_"):
                    continue  # ignore files that start with underscore

                extension = f"cogs.{cog.stem}"

                try:
                    await self.bot.reload_extension(extension)
                    loaded += 1
                except Exception as e:  # noqa: BLE001
                    log_cog.error("Unable to load %s: %s", extension, e)
                    failed += 1

            log_cog.info("Reloaded %s cog(s)", loaded)
            log_cog.info("Failed to reload %s cog(s)", failed)

            await msg.edit(content=f"Successfully reloaded {loaded} cog(s)")

        else:
            log_cog.info("REQUEST - Cog Reload | %s", cog_name)
            msg = await ctx.send(f"Attempting reload of `{cog_name}`")

            if not cog_name.startswith("cogs."):
                if os.path.exists(f"cogs/{cog_name}.py"):
                    log_cog.info("Located %s, reloading", cog_name)

                    extension = f"cogs.{cog_name}"
                    try:
                        await self.bot.reload_extension(extension)
                        log_cog.info("Reload successful")
                        await msg.edit(content=f"Successfully reloaded `{cog_name}`")
                    except commands.ExtensionNotLoaded:
                        log_cog.error("Reload failed, %s is not loaded", cog_name)
                        await msg.edit(
                            content=f"Unable to reload `{cog_name}`. Refer to log for info."
                        )
                    except commands.ExtensionError as e:
                        log_cog.error("Reload failed with error: %s", e)
                        await msg.edit(
                            content=f"Unable to reload `{cog_name}`. Refer to log for info."
                        )
                    except Exception as e:  # noqa: BLE001
                        log_cog.error("Reload failed with error: %s", e)
                        await msg.edit(
                            content=f"Unable to reload `{cog_name}`. Refer to log for info."
                        )
                else:
                    log_cog.error("%s was not found in %s", cog_name, COGS_DIR)
                    await msg.edit(
                        content=f"Unable to reload `{cog_name}`. Cog not found!"
                    )

    @commands.is_owner()
    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        log.info("REQUEST - Bot Shutdown")
        msg = await ctx.send("Cya 👋")
        try:
            await self.bot.close()  # close connection with Discord
            log.info("Shutdown Successful")
        except Exception:  # noqa: BLE001
            log.error("Shutdown failed with reason: %s", traceback.format_exc())
            await msg.edit(content="Shutdown failed. Refer to logs.")


async def setup(bot):
    await bot.add_cog(Owner(bot))
