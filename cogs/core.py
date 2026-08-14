from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("pigeon(Core)")

STATUSES = {
    "online": "🟢 Online",
    "dnd": "⛔️ Do Not Disturb",
    "idle": "🌙 Idle",
    "offline": "⚪️ Offline / Invisible",
}

class PingCard(discord.ui.LayoutView):
    def __init__(self, gateway_ms: int, servers: int, members: int) -> None:
        super().__init__()

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay("### You called?"),
                discord.ui.TextDisplay("It's alive!!! or is it?"),
                discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
                discord.ui.ActionRow(
                    discord.ui.Button(label=f"Latency: {gateway_ms}ms", style=discord.ButtonStyle.success, disabled=True),
                    discord.ui.Button(label=f"Servers: {servers}", style=discord.ButtonStyle.secondary, disabled=True),
                    discord.ui.Button(label=f"Helping {members} people", style=discord.ButtonStyle.secondary, disabled=True),                  
                ),
                accent_color=discord.Color.green(),
            )
        )

class UserCard(discord.ui.LayoutView):
    def __init__(self, member: discord.Member) -> None:
        super().__init__()

        

        status_text = STATUSES.get(member.raw_status, "⚪️ Offline / Invisible")

        age_days = (discord.utils.utcnow() - member.created_at).days

        blocks = [
            discord.ui.Section(
                discord.ui.TextDisplay(f"### {member.display_name} {'<a:booster:1529440901879828601>' if member.premium_since else ""}"),
                discord.ui.TextDisplay(f"-# Status: {status_text}"),
                discord.ui.TextDisplay(f"-# Member of {member.guild.name} since {discord.utils.format_dt(member.joined_at, "D")}"),
                accessory=discord.ui.Thumbnail(member.display_avatar.url),
            ),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                f"> User ID: `{member.id}`\n" \
                f"> Joined Discord {discord.utils.format_dt(member.created_at, "R")} ({discord.utils.format_dt(member.created_at, "D")})\n" \
                f"> That's {age_days} days ago!"
            ),
        ]

        if member.premium_since:
            blocks.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
            blocks.append(discord.ui.TextDisplay(f"**{member.display_name} boost's this server! They've done this since time!**"))
            
        
        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(f"-# User Information"),
                *blocks,
            ),
        )


async def error_card(interaction: discord.Interaction):
    embed = discord.Embed(
        title="No can do!",
        description="Sorry, this command doesn't work for bots. To view bot info run `/botinfo bot:`",
        color=discord.Color.dark_gray(),
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)
        

class CoreCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check to see if Pigeon is online or not.")
    async def ping(self, interaction: discord.Interaction) -> None:
        gateway_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(view=PingCard(
            gateway_ms,
            servers=len(self.bot.guilds),
            members=sum(g.member_count or 0 for g in self.bot.guilds),
            )
        )
        log.info("App Command Run: ping")

    @app_commands.command(name="userinfo", description="View info about yourself or someone else.")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        member = member or interaction.user
        

        if interaction.guild:
            member = interaction.guild.get_member(member.id) or member

        if member.bot:
            await error_card(interaction)
        else:
            await interaction.response.send_message(view=UserCard(member))


async def setup(bot) -> None:
    await bot.add_cog(CoreCommands(bot))