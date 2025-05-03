import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

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

RATINGS = [
    ("1", "1 ⭐"),
    ("2", "2 ⭐⭐"),
    ("3", "3 ⭐⭐⭐"),
    ("4", "4 ⭐⭐⭐⭐"),
    ("5", "5 ⭐⭐⭐⭐⭐")
]

class ProductSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=label, value=value) for value, label in PRODUCTS]
        super().__init__(placeholder="Select a product", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        product = self.values[0]
        await interaction.response.send_message("Now select a rating:", view=RatingView(product), ephemeral=True)

class RatingSelect(discord.ui.Select):
    def __init__(self, product):
        self.product = product
        options = [discord.SelectOption(label=label, value=value) for value, label in RATINGS]
        super().__init__(placeholder="Select a rating", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        rating = self.values[0]
        customer = interaction.user

        conn = sqlite3.connect("vouches.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS vouches (user_id TEXT, product TEXT, rating INTEGER)")
        c.execute("INSERT INTO vouches (user_id, product, rating) VALUES (?, ?, ?)", (str(customer.id), self.product, int(rating)))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Feedback Received",
            description="We received feedback for your transaction!",
            color=discord.Color.green()
        )
        embed.add_field(name="Customer", value=customer.mention, inline=False)
        embed.add_field(name="Product", value=dict(PRODUCTS).get(self.product, self.product), inline=True)
        embed.add_field(name="Rating", value=f"{rating} ⭐", inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123456789/logo.png")
        embed.set_footer(text="Thanks for your support! | Made by Kai")

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Vouch submitted successfully!", ephemeral=True)

class ProductView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ProductSelect())

class RatingView(discord.ui.View):
    def __init__(self, product):
        super().__init__(timeout=60)
        self.add_item(RatingSelect(product))

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot is online as {bot.user}")

@bot.tree.command(name="vouch", description="Vouch for a user")
async def vouch(interaction: discord.Interaction):
    await interaction.response.send_message("Please select the product:", view=ProductView(), ephemeral=True)

bot.run(TOKEN)
