"""
components.py — THE complete Components V2 + interactive reference (verified working).

Drop in cogs/. Adds demo commands you can run to SEE each thing:
  /demo_buttons   every button style, disabled, link — inside a card
  /demo_menus     string select + role picker — inside a card
  /demo_card      a polished "server info" card (the Brisbane look)
  /demo_live      a menu + button that actually respond, inside a card
  /demo_toggle    a button that disables itself after one click
  /demo_modal     a pop-up form
  /demo_classic   old-style buttons UNDER a normal message (View, not LayoutView)

================================================================================
TWO SYSTEMS — READ THIS FIRST
================================================================================
1. discord.ui.View — the CLASSIC system. An invisible holder for buttons/selects
   that attach UNDER a normal message (which still has content=/embed=). Buttons
   auto-arrange into rows. Good for "a couple of buttons under a message."

2. discord.ui.LayoutView — "Components V2". The message IS the layout. You build
   it out of blocks. It REPLACES content/embeds — you send ONLY view=.

================================================================================
THE ONE RULE THAT MAKES A "CARD"
================================================================================
A card = a discord.ui.Container. Whatever you want INSIDE the card, you pass
INSIDE the Container(...) parentheses. Blocks left loose in the LayoutView have
no border and float in the message. Buttons/selects must be wrapped in an
ActionRow, and that ActionRow goes inside the Container like any other block.

    class MyCard(discord.ui.LayoutView):
        card = discord.ui.Container(      # <- the bordered box
            discord.ui.TextDisplay("..."),   # inside
            discord.ui.ActionRow(MyButton()),# inside
            accent_color=discord.Color.blurple(),
        )
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

# Reliable, correctly-sized demo images (picsum gives real images at the size you ask):
BANNER = "https://picsum.photos/seed/pigeon/1000/300"  # WIDE — good for MediaGallery
ICON = "https://picsum.photos/seed/pigeon/200"          # small square — good for Thumbnail


# ============================================================================
# BUTTONS
# ============================================================================
# A button's arguments:
#   label     text on it (<=80 chars)          emoji     "🕊️" or "<:name:id>"
#   style     colour/kind (see below)          disabled  True = greyed & unclickable
#   url       makes it a LINK button (no callback)       row  force which row (0-4)
#   custom_id stable id — required for PERSISTENT buttons (survive restarts)
#
# ButtonStyle: primary/blurple · secondary/grey · success/green · danger/red · link
#
# TWO ways to give a button behaviour:
#   (A) subclass discord.ui.Button, override async def callback(self, interaction)
#       -> use this INSIDE containers (clean when nested)
#   (B) @discord.ui.button(...) decorator on a View method
#       -> use this in a classic View (top-level)


class ActionButton(discord.ui.Button):
    """Pattern (A): a reusable button subclass. Works anywhere, including inside
    a Container. Give it a label/style, override callback."""

    def __init__(self, label: str, style: discord.ButtonStyle) -> None:
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"You clicked **{self.label}**", ephemeral=True)


class ButtonsCard(discord.ui.LayoutView):
    """Every button style, a disabled one, and a link — all INSIDE one card."""

    card = discord.ui.Container(
        discord.ui.TextDisplay("## Buttons — every style"),
        discord.ui.TextDisplay(
            "`primary` blurple · `secondary` grey · `success` green · `danger` red · `link`"
        ),
        discord.ui.Separator(),
        # Row 1: the four coloured styles (each ActionRow holds up to 5 buttons).
        discord.ui.ActionRow(
            ActionButton("Primary", discord.ButtonStyle.primary),
            ActionButton("Secondary", discord.ButtonStyle.secondary),
            ActionButton("Success", discord.ButtonStyle.success),
            ActionButton("Danger", discord.ButtonStyle.danger),
        ),
        # Row 2: a DISABLED (greyed-out) button, and a LINK button.
        discord.ui.ActionRow(
            discord.ui.Button(label="Disabled", style=discord.ButtonStyle.secondary, disabled=True),
            discord.ui.Button(label="Open Discord", style=discord.ButtonStyle.link, url="https://discord.com"),
        ),
        accent_color=discord.Color.blurple(),
    )


# ============================================================================
# SELECT MENUS (dropdowns)
# ============================================================================
# String select: you define the options yourself.
#   placeholder  greyed hint    min_values/max_values  how many can be chosen
#   disabled     grey it out    SelectOption(label, value, emoji, description, default)
# The picks arrive as self.values (a list of the chosen `value`s).
#
# "Auto" selects populated by Discord (no options list) — .values are real objects:
#   RoleSelect · UserSelect · ChannelSelect · MentionableSelect


class FavouriteSelect(discord.ui.Select):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Pick your favourite bird…",
            min_values=1,
            max_values=1,  # set >1 to allow multi-select
            options=[
                discord.SelectOption(label="Pigeon", value="pigeon", emoji="🕊️", description="Obviously"),
                discord.SelectOption(label="Owl", value="owl", emoji="🦉"),
                discord.SelectOption(label="Crow", value="crow", emoji="🐦‍⬛", default=True),  # pre-selected
            ],
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        for option in self.options:
            option.default = option.value in self.values #make the menu select stick
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"You picked: {self.values[0]}", ephemeral=True)


class RolePicker(discord.ui.RoleSelect):
    """An auto-select: Discord fills it with the server's roles."""

    def __init__(self) -> None:
        super().__init__(placeholder="Pick a role…", max_values=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        role = self.values[0]  # a real discord.Role
        await interaction.response.send_message(f"You picked {role.mention}", ephemeral=True)


class MenusCard(discord.ui.LayoutView):
    """A string dropdown and a role picker — each in its own ActionRow, inside a card."""

    card = discord.ui.Container(
        discord.ui.TextDisplay("## Menus"),
        discord.ui.TextDisplay("A dropdown you define, and a live role picker."),
        discord.ui.Separator(),
        discord.ui.ActionRow(FavouriteSelect()),
        discord.ui.ActionRow(RolePicker()),
        accent_color=discord.Color.green(),
    )


# ============================================================================
# THE POLISHED CARD — the "Brisbane" look (banner + info + status pills)
# ============================================================================
# Tricks used here:
#   - DISABLED buttons as STATUS PILLS (not clickable, just badges).
#   - inline `code` for the little grey chips in text.
#   - a LINK button for "Join".
#   - a Section: text on the LEFT, a Thumbnail on the RIGHT. NOTE: a Section grows
#     to the height of its accessory, so give it a FEW lines of text or it looks
#     empty. For a big image across the card, use MediaGallery (WIDE image!).


def _pill(label: str, emoji: str | None = None) -> discord.ui.Button:
    """A disabled button used purely as a status badge."""
    return discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, disabled=True, emoji=emoji)


class ServerInfoCard(discord.ui.LayoutView):
    card = discord.ui.Container(
        # A wide banner across the top. MediaGallery = large; feed it a WIDE image.
        discord.ui.MediaGallery(discord.MediaGalleryItem(BANNER, description="server banner")),
        discord.ui.TextDisplay("## Server Information"),
        # A bullet list. `- ` makes bullets; **bold** labels; `code` = grey chips.
        discord.ui.TextDisplay(
            "- **Server Name:** Pigeon Test Server\n"
            "- **Owner:** <@1520000000000000000>\n"
            "- **Join Code:** `PIGEON`\n"
            "- **Players:** `21/50`"
        ),
        discord.ui.Separator(spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay("### ℹ️ Status"),
        # A row of DISABLED buttons acting as status pills, plus a real link button.
        discord.ui.ActionRow(
            _pill("Players: 21/50", emoji="👤"),
            _pill("Queue: 0", emoji="👥"),
            discord.ui.Button(label="Online", style=discord.ButtonStyle.success, disabled=True, emoji="✅"),
            discord.ui.Button(label="Join", style=discord.ButtonStyle.link, url="https://discord.com"),
        ),
        accent_color=discord.Color.blurple(),
    )


# ============================================================================
# INTERACTIVE PATTERNS — respond, and edit the card in place
# ============================================================================


class LiveButton(discord.ui.Button):
    """Counts clicks and edits its own label. Shows editing a LayoutView in place."""

    def __init__(self) -> None:
        super().__init__(label="Clicked 0 times", style=discord.ButtonStyle.success)
        self.count = 0

    async def callback(self, interaction: discord.Interaction) -> None:
        self.count += 1
        self.label = f"Clicked {self.count} times"
        await interaction.response.edit_message(view=self.view)  # re-render with new label


class LiveCard(discord.ui.LayoutView):
    card = discord.ui.Container(
        discord.ui.TextDisplay("## Live controls"),
        discord.ui.TextDisplay("The menu and button below actually respond."),
        discord.ui.Separator(),
        discord.ui.ActionRow(FavouriteSelect()),
        discord.ui.ActionRow(LiveButton()),
        accent_color=discord.Color.gold(),
    )


class ToggleButton(discord.ui.Button):
    """Disables itself after one use — the common 'spent' pattern."""

    def __init__(self) -> None:
        super().__init__(label="Use me (once)", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.disabled = True
        self.label = "Used ✔"
        self.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self.view)


class ToggleCard(discord.ui.LayoutView):
    card = discord.ui.Container(
        discord.ui.TextDisplay("## One-shot button"),
        discord.ui.ActionRow(ToggleButton()),
        accent_color=discord.Color.red(),
    )


# ============================================================================
# MODALS (pop-up forms)
# ============================================================================
# Show with interaction.response.send_modal(...). TextInput fields:
#   label · style (TextStyle.short / .paragraph) · placeholder · required
#   max_length / min_length · default (pre-filled)
# Read values in on_submit via each field's .value.


class FeedbackModal(discord.ui.Modal, title="Send Feedback"):
    subject = discord.ui.TextInput(label="Subject", style=discord.TextStyle.short, max_length=100)
    body = discord.ui.TextInput(
        label="Message",
        style=discord.TextStyle.paragraph,
        placeholder="Type as much as you like…",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Thanks! **{self.subject.value}**:\n> {self.body.value}", ephemeral=True
        )


# ============================================================================
# CLASSIC VIEW — buttons UNDER a normal message (not a LayoutView)
# ============================================================================
# When you just want a couple of buttons beneath a text/embed message, a plain
# View is simplest. Here the @decorator style shines (no subclassing needed).


class ClassicView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=180)  # buttons stop working after 180s idle

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message("You said yes 👍", ephemeral=True)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message("You said no 👎", ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


# ============================================================================
# PERSISTENT VIEW — buttons that survive a bot restart
# ============================================================================
# Normal views die after their timeout or a restart. For buttons that must ALWAYS
# work (a "get roles" panel that lives forever), make the view persistent:
#   - timeout=None
#   - every component has a stable custom_id
#   - register it once on startup with bot.add_view(...) (see setup() below)


class PersistentPanel(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Always works", style=discord.ButtonStyle.primary, custom_id="pigeon:persist:hello")
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message("Works even after a restart 🎉", ephemeral=True)


# ============================================================================
# THE COG — wires everything to slash commands
# ============================================================================


class ComponentsDemo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="demo_buttons", description="Every button style, disabled, and a link — in a card.")
    async def demo_buttons(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=ButtonsCard())

    @app_commands.command(name="demo_menus", description="A dropdown and a role picker — in a card.")
    async def demo_menus(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=MenusCard())

    @app_commands.command(name="demo_card", description="A polished server-info card.")
    async def demo_card(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=ServerInfoCard())

    @app_commands.command(name="demo_live", description="A menu + button that respond, inside a card.")
    async def demo_live(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=LiveCard())

    @app_commands.command(name="demo_toggle", description="A button that disables itself after one click.")
    async def demo_toggle(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=ToggleCard())

    @app_commands.command(name="demo_modal", description="Pop up a form.")
    async def demo_modal(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(FeedbackModal())

    @app_commands.command(name="demo_classic", description="Old-style buttons under a normal message.")
    async def demo_classic(self, interaction: discord.Interaction) -> None:
        # Classic View attaches UNDER a normal message, so content= is allowed here.
        await interaction.response.send_message("Do you like Pigeon?", view=ClassicView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ComponentsDemo(bot))
    # Register persistent views ONCE so their custom_id buttons work across restarts.
    bot.add_view(PersistentPanel())
