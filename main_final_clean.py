import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import aiosqlite
import os
from keep_alive import keep_alive

# === Keep alive for Railway ===
keep_alive()

# === Environment Variables ===
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# === Database ===
DB_FILE = "vouches.db"

# === Product & Rating Lists ===
products = [
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
    ("FreeFire-TOURN4M3NT", "FreeFire-TOURN4M3NT"),
    ("BGMI-ACC0UN7S", "BGMI-ACC0UN7S"),
    ("BGMI-UC", "BGMI-UC"),
    ("BGMI-TOURN4M3NT", "BGMI-TOURN4M3NT"),
    ("4M4ZON-SHOP", "4M4ZON-SHOP"),
    ("OTHER PRODUCT", "OTHER PRODUCT")
]

ratings = [
    ("5/5 ⭐⭐⭐⭐⭐", "5"),
    ("4/5 ⭐⭐⭐⭐", "4"),
    ("3/5 ⭐⭐⭐", "3"),
    ("2/5 ⭐⭐", "2"),
    ("1/5 ⭐", "1")
]

class ProductSelect(Select):
    def __init__(self, view):
        self.parent_view = view
        options = [discord.SelectOption(label=label, value=value) for value, label in products]
        super().__init__(placeholder="Select a Product", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.product = self.values[0]
        await interaction.response.defer()
        self.parent_view.stop()

class RatingSelect(Select):
    def __init__(self, view):
        self.parent_view = view
        options = [discord.SelectOption(label=label, value=value) for label, value in ratings]
        super().__init__(placeholder="Select Rating", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.rating = self.values[0]
        await interaction.response.defer()
        self.parent_view.stop()

class ProductView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.product = None
        self.rating = None
        self.add_item(ProductSelect(self))

class RatingView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.rating = None
        self.add_item(RatingSelect(self))

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    synced = await tree.sync(guild=discord.Object(id=int(GUILD_ID)))
    print(f"Synced {len(synced)} commands.")

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS vouches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vouched_user_id INTEGER,
                vouched_by_id INTEGER,
                product TEXT,
                rating TEXT,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

@tree.command(name="vouch", description="Vouch for a user", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(user="User to vouch for", feedback="Your feedback")
async def vouch(interaction: discord.Interaction, user: discord.Member, feedback: str):
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't vouch for yourself!", ephemeral=True)
        return

    view = ProductView()
    await interaction.response.send_message("Select a product:", view=view, ephemeral=True)
    await view.wait()
    if not view.product:
        await interaction.followup.send("⚠️ You didn't select a product.", ephemeral=True)
        return

    rating_view = RatingView()
    await interaction.followup.send("Select rating:", view=rating_view, ephemeral=True)
    await rating_view.wait()
    if not rating_view.rating:
        await interaction.followup.send("⚠️ You didn't select a rating.", ephemeral=True)
        return

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO vouches (vouched_user_id, vouched_by_id, product, rating, feedback) VALUES (?, ?, ?, ?, ?)",
            (user.id, interaction.user.id, view.product, rating_view.rating, feedback)
        )
        await db.commit()

    embed = discord.Embed(title="Feedback Received", color=discord.Color.green())
    embed.add_field(name="Customer", value=user.mention, inline=False)
    embed.add_field(name="Rating", value=f"{rating_view.rating} ⭐", inline=False)
    embed.add_field(name="Feedback", value=f"+rep {user.mention} {feedback}", inline=False)
    embed.set_thumbnail(url="https://i.imgur.com/iywsi5L.png")
    embed.set_footer(text="Thanks for your support! • Made by Kai")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send("✅ Your vouch has been recorded!", ephemeral=True)

# Run bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ No TOKEN found in environment variables.")
