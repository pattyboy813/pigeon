"""
slash_commands.py — THE slash-command (application command) teaching file.

Everything about /commands: parameters & types, descriptions, choices,
autocomplete, number ranges, groups & subcommands, permissions, cooldowns,
ephemeral replies, deferring for slow work, and error handling.

Drop this in cogs/ and the commands below appear in Discord.

MENTAL MODEL
------------
- You DEFINE commands with the @app_commands.command decorator (or in a Cog).
- Discord needs to be TOLD they exist — that's what bot.tree.sync() does (main.py).
- Parameters become typed inputs in Discord's UI automatically, based on the
  Python type hint you give them (str -> text box, int -> number, discord.Member
  -> user picker, etc.).
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class SlashDemo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ------------------------------------------------------------------ basics
    @app_commands.command(name="hello", description="The simplest possible command.")
    async def hello(self, interaction: discord.Interaction) -> None:
        # ephemeral=True -> only the person who ran it can see the reply.
        await interaction.response.send_message("Hello! 🕊️", ephemeral=True)

    # ---------------------------------------------------- parameters and types
    # The TYPE HINT decides the input widget Discord shows.
    #   str -> text | int/float -> number | bool -> True/False toggle
    #   discord.Member / User -> user picker | discord.Role -> role picker
    #   discord.TextChannel -> channel picker | discord.Attachment -> file upload
    # @describe adds the little help text under each field.
    @app_commands.command(name="greet", description="Greet someone with options.")
    @app_commands.describe(
        person="Who to greet",
        times="How many times (1-5)",
        loudly="Shout it?",
    )
    async def greet(
        self,
        interaction: discord.Interaction,
        person: discord.Member,
        times: app_commands.Range[int, 1, 5],  # Range enforces min/max IN Discord's UI
        loudly: bool = False,  # a default makes the parameter OPTIONAL
    ) -> None:
        msg = f"Hello {person.mention}! " * times
        if loudly:
            msg = msg.upper()
        await interaction.response.send_message(msg)

    # ------------------------------------------------------------- fixed choices
    # When there's a small fixed set of options, use choices — Discord shows them
    # as a dropdown and validates the input for you.
    @app_commands.command(name="setcolor", description="Pick from fixed choices.")
    @app_commands.choices(
        color=[
            app_commands.Choice(name="Blurple", value="blurple"),
            app_commands.Choice(name="Green", value="green"),
            app_commands.Choice(name="Red", value="red"),
        ]
    )
    async def setcolor(self, interaction: discord.Interaction, color: app_commands.Choice[str]) -> None:
        # color.name is what the user saw; color.value is what you get in code.
        await interaction.response.send_message(f"You chose {color.name} ({color.value}).", ephemeral=True)

    # -------------------------------------------------------------- autocomplete
    # For a LARGE or dynamic set, use autocomplete — a function that returns
    # suggestions as the user types. Great for "pick a registered name" etc.
    FRUITS = ["apple", "apricot", "banana", "blueberry", "cherry", "date", "elderberry"]

    async def fruit_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # `current` is what they've typed so far. Return up to 25 suggestions.
        return [
            app_commands.Choice(name=f, value=f)
            for f in self.FRUITS
            if current.lower() in f.lower()
        ][:25]

    @app_commands.command(name="pickfruit", description="Autocomplete as you type.")
    @app_commands.autocomplete(fruit=fruit_autocomplete)
    async def pickfruit(self, interaction: discord.Interaction, fruit: str) -> None:
        await interaction.response.send_message(f"You picked {fruit}.", ephemeral=True)

    # ------------------------------------------------- permissions & guild-only
    # default_permissions hides the command from members who lack that permission
    # (admins can re-enable per-server). guild_only stops it working in DMs.
    @app_commands.command(name="adminonly", description="Only members with Manage Server see this.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def adminonly(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("You have Manage Server.", ephemeral=True)

    # -------------------------------------------------------------- cooldowns
    # Limit how often a command can be used. This one: 1 use / 10s per user.
    @app_commands.command(name="slow", description="Rate-limited command.")
    @app_commands.checks.cooldown(rate=1, per=10.0)
    async def slow(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Used it. Wait 10s to use again.", ephemeral=True)

    # -------------------------------------------- deferring for slow work
    # An interaction must get a FIRST response within 3 seconds. If your command
    # does slow work (an API call, a big query), DEFER first — that buys you time
    # and shows "Pigeon is thinking…". Then reply with followup.
    @app_commands.command(name="longtask", description="Defer, then reply after slow work.")
    async def longtask(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        # ... imagine slow work here (await some_api(), a big DB query) ...
        await interaction.followup.send("Done after the slow work!", ephemeral=True)

    # ----------------------------------------------- per-cog error handling
    # Catch errors from THIS cog's commands (e.g. cooldown hit, check failed)
    # and reply nicely instead of letting it blow up silently.
    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏳ Slow down — try again in {error.retry_after:.0f}s."
        elif isinstance(error, app_commands.MissingPermissions):
            msg = "🚫 You don't have permission to do that."
        else:
            msg = f"Something went wrong: {error}"
        # The interaction may or may not already be responded to; handle both.
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


# ============================================================================
# COMMAND GROUPS (subcommands) — e.g. /throne register, /throne link
# ============================================================================
#
# A Group turns one top-level name into a namespace of subcommands. This is how
# you'll build /throne, /settings, etc. Define a class subclassing app_commands.Group.

class ThroneGroup(app_commands.Group):
    """Becomes /throne with subcommands under it."""

    def __init__(self) -> None:
        super().__init__(name="throne", description="Throne tracking commands.")

    @app_commands.command(name="register", description="(demo) Register a creator.")
    async def register(self, interaction: discord.Interaction, throne_url: str) -> None:
        await interaction.response.send_message(f"(demo) would register {throne_url}", ephemeral=True)

    @app_commands.command(name="link", description="(demo) Link your Throne name.")
    async def link(self, interaction: discord.Interaction, name: str) -> None:
        await interaction.response.send_message(f"(demo) would link {name}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SlashDemo(bot))
    # Groups are added to the tree directly (not via a cog).
    bot.tree.add_command(ThroneGroup())
