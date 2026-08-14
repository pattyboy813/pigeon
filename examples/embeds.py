"""
embeds.py — THE embed teaching file.

An EMBED is the classic "rich box" (title, coloured stripe, fields, images).
It's simpler and older than Components V2. Use embeds when you want a quick,
good-looking box and don't need the layout control of a LayoutView.

Drop this in cogs/ and run /demo_embed and /demo_embeds to see them.

ANATOMY OF AN EMBED (and Discord's hard limits — exceed them and the send fails):
  title        up to 256 chars      the bold heading
  description  up to 4096 chars     the main body (markdown works)
  colour       the left stripe colour
  url          makes the title a clickable link
  timestamp    a datetime, shown in the footer area in each user's timezone
  author       name + optional icon + url, shown ABOVE the title
  footer       text + optional icon, shown at the bottom
  thumbnail    small image, top-right
  image        big image, bottom
  fields       up to 25; each: name (256) + value (1024), inline True/False
  TOTAL of all text across the embed must be <= 6000 chars
You can send up to 10 embeds in ONE message (embeds=[...]).
"""

from __future__ import annotations

import datetime

import discord
from discord import app_commands
from discord.ext import commands

LOGO = "https://raw.githubusercontent.com/github/explore/main/topics/discord/discord.png"


def build_showcase_embed() -> discord.Embed:
    """One embed using every part, so you can see them all at once."""

    # COLOUR — three equivalent ways to set it:
    #   named:  discord.Color.blurple(), .green(), .red(), .gold(), .random() ...
    #   hex:    discord.Color(0x8B5CF6)
    #   rgb:    discord.Color.from_rgb(139, 92, 246)
    embed = discord.Embed(
        title="Pigeon — Embed Showcase",
        url="https://discord.com",  # makes the title clickable
        description=(
            "This is the **description**. Markdown works: *italic*, `code`, "
            "[links](https://discord.com), and\n> quotes.\n\n"
            "The coloured stripe on the left is the embed's `colour`."
        ),
        colour=discord.Color.blurple(),
        timestamp=datetime.datetime.now(datetime.timezone.utc),  # shows in the footer
    )

    # AUTHOR — appears above the title (great for "posted by @someone").
    embed.set_author(name="Pigeon 🕊️", icon_url=LOGO, url="https://discord.com")

    # THUMBNAIL — small image, top-right.
    embed.set_thumbnail(url=LOGO)

    # IMAGE — large image across the bottom.
    embed.set_image(url=LOGO)

    # FOOTER — small text at the very bottom (next to the timestamp).
    embed.set_footer(text="Footer text • v1", icon_url=LOGO)

    # FIELDS — mini name/value blocks. inline=True lets up to 3 sit side-by-side;
    # inline=False forces a full-width row.
    embed.add_field(name="Inline A", value="side", inline=True)
    embed.add_field(name="Inline B", value="by side", inline=True)
    embed.add_field(name="Inline C", value="three across", inline=True)
    embed.add_field(name="Full width", value="This field is on its own row.", inline=False)

    # A blank field is a handy spacer trick (zero-width space in name):
    embed.add_field(name="​", value="​", inline=False)

    return embed


class EmbedsDemo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="demo_embed", description="One embed using every feature.")
    async def demo_embed(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=build_showcase_embed())

    @app_commands.command(name="demo_embeds", description="Send multiple embeds in one message.")
    async def demo_embeds(self, interaction: discord.Interaction) -> None:
        # Up to 10 embeds per message. Handy for a themed set of coloured cards.
        first = discord.Embed(title="Green", description="Positive", colour=discord.Color.green())
        second = discord.Embed(title="Red", description="Negative", colour=discord.Color.red())
        third = discord.Embed(title="Custom hex", description="#8B5CF6", colour=discord.Color(0x8B5CF6))
        await interaction.response.send_message(embeds=[first, second, third])


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EmbedsDemo(bot))
