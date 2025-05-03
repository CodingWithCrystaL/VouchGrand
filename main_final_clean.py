import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

PRODUCTS = [
    ("1337-ch3at5", "1337-ch3at5"),
    ("grandrp-m0n3y", "grandrp-m0n3y"),
    ("grandrp-acc0unt5", "grandrp-acc0unt5"),
    ("grandrp-m0n3y-m3th0d", "grandrp-m0n3y-m3th0d"),
    ("tr1gg3r-b0t", "tr1gg3r-b0t"),
    ("shax-cl3an3r", "shax-cl3an3r"),
    ("custom-discord-bot", "custom-discord-bot"),
    ("custom-ch3at3r", "custom-ch3at3r"),
    ("l3ad3r-scr1pts", "l3ad3r-scr1pts"),
    ("adm1n-scr1pts", "adm1n-scr1pts"),
    ("l3ad3r-or-adm1n-appl1cat1on", "l3ad3r-or-adm1n-appl1cat1on"),
    ("pc-cl3an3r", "pc-cl3an3r"),
    ("custom-ch3at3r-redux", "custom-ch3at3r-redux"),
    ("h0w-to-b4n-evad3", "h0w-to-b4n-evad3"),
    ("premium-b4n-evad3", "premium-b4n-evad3"),
    ("pc-ch3ck-pr0c3dur3", "pc-ch3ck-pr0c3dur3"),
    ("V4LOR4NT-SHOP", "V4LOR4NT-SHOP"),
    ("FreeFire-P4N3LS", "FreeFire-P4N3LS"),
    ("FreeFire-D14MONDS", "FreeFire-D14MONDS"),
    ("FreeFire-ACC0UN7S", "FreeFire-ACC0UN7S"),
    ("BGMI-ACC0UN7S", "BGMI-ACC0UN7S"),
    ("BGMI-UC", "BGMI-UC"),
    ("4M4ZON-SHOP", "4M4ZON-SHOP"),
    ("OTHER PRODUCT", "OTHER PRODUCT")
]

LOGO_URL = "https://cdn.discordapp.com/attachments/1328282907814531073/1368106724795351102/BD9E3BFA-F422-4AF8-8AF2-349AD4D3E145.png"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class ProductDropdown(discord.ui.Select):
    def __init__(self, user: discord.User):
        self.user = user
        options = [discord.SelectOption(label=label, value=value) for value, label in PRODUCTS]
        super().__init__(placeholder="Select a product", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FeedbackModal(product=self.values[0], user=self.user))

class ProductView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.add_item(ProductDropdown(user))

class FeedbackModal(discord.ui.Modal, title="Provide Feedback"):
    def __init__(self, product: str, user: discord.User):
        super().__init__()
        self.product = product
        self.user = user
        self.feedback_input = discord.ui.TextInput(label="Feedback", style=discord.TextStyle.paragraph, required=True)
        self.add_item(self.feedback_input)

    async def on_submit(self, interaction: discord.Interaction):
        feedback = self.feedback_input.value

        # Save to DB
        conn = sqlite3.connect("vouches.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS vouches (
            customer TEXT, product TEXT, feedback TEXT
        )""")
        cursor.execute("INSERT INTO vouches (customer, product, feedback) VALUES (?, ?, ?)",
                       (str(self.user), self.product, feedback))
        conn.commit()
        conn.close()

        # Send embed
        embed = discord.Embed(title="New Vouch Received", color=discord.Color.purple())
        embed.add_field(name="Customer", value=self.user.mention, inline=False)
        embed.add_field(name="Product", value=self.product, inline=False)
        embed.add_field(name="Feedback", value=feedback, inline=False)
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_footer(text="Thanks for your support! | Made by Kai", icon_url=LOGO_URL)

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Vouch submitted successfully!", ephemeral=True)

@bot.tree.command(name="vouch", description="Submit a vouch", guild=discord.Object(id=GUILD_ID))
async def vouch(interaction: discord.Interaction):
    await interaction.response.send_message("Please select a product:", view=ProductView(interaction.user), ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot is ready. Logged in as {bot.user}")

bot.run(TOKEN)
