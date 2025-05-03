import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import aiosqlite
import os
from flask import Flask
from threading import Thread

# === KEEP ALIVE SERVER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

def keep_alive():
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080}).start()

keep_alive()

# === ENV VARIABLES ===
TOKEN = os.getenv("TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("GUILD_ID", 0))

if not TOKEN or not LOG_CHANNEL_ID or not GUILD_ID:
    print("❌ Missing one or more required environment variables.")
    exit()

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

DB_FILE = "vouches.db"

# === PRODUCT LIST (MAX 25) ===
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
    ("BGMI-ACC0UN7S", "BGMI-ACC0UN7S"),
    ("BGMI-UC", "BGMI-UC"),
    ("4M4ZON-SHOP", "4M4ZON-SHOP"),
    ("OTHER PRODUCT", "OTHER PRODUCT")
]

ratings = [
    ("⭐ 1/5", "1"),
    ("⭐⭐ 2/5", "2"),
    ("⭐⭐⭐ 3/5", "3"),
    ("⭐⭐⭐⭐ 4/5", "4"),
    ("⭐⭐⭐⭐⭐ 5/5", "5")
]

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} command(s) to guild ID {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Vouching Service"))

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS vouches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vouched_user_id INTEGER,
                vouched_by_id INTEGER,
                product TEXT,
                rating INTEGER,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

class ProductSelect(Select):
    def __init__(self, parent):
        self.parent = parent
        options = [discord.SelectOption(label=label, value=value) for value, label in products]
        super().__init__(placeholder="Select a product", options=options)

    async def callback(self, interaction):
        self.parent.product = self.values[0]
        await interaction.response.defer()
        self.parent.stop()

class RatingSelect(Select):
    def __init__(self, parent):
        self.parent = parent
        options = [discord.SelectOption(label=label, value=value) for label, value in ratings]
        super().__init__(placeholder="Select a rating", options=options)

    async def callback(self, interaction):
        self.parent.rating = int(self.values[0])
        await interaction.response.defer()
        self.parent.stop()

class ProductRatingView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.product = None
        self.rating = None
        self.add_item(ProductSelect(self))
        self.add_item(RatingSelect(self))

@tree.command(name="vouch", description="Submit a vouch for a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to vouch for", feedback="Your feedback")
async def vouch(interaction: discord.Interaction, user: discord.Member, feedback: str):
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot vouch for yourself.", ephemeral=True)
        return

    view = ProductRatingView()
    await interaction.response.send_message("Please select the product and rating:", view=view, ephemeral=True)
    timeout = await view.wait()

    if timeout or not view.product or not view.rating:
        await interaction.followup.send("⏰ Timed out or selection not made. Try again.", ephemeral=True)
        return

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO vouches (vouched_user_id, vouched_by_id, product, rating, feedback) VALUES (?, ?, ?, ?, ?)",
            (user.id, interaction.user.id, view.product, view.rating, feedback)
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        (vouch_id,) = await cursor.fetchone()

    embed = discord.Embed(
        title=f"📬 Feedback Received",
        description="We received feedback for your transaction!",
        color=discord.Color.green()
    )
    embed.add_field(name="Customer", value=f"<@{user.id}>", inline=True)
    embed.add_field(name="Rating", value=f"{view.rating} ⭐", inline=True)
    embed.add_field(name="Feedback", value=feedback, inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1214425023717169172/1236229832585263135/7E21D39E-ECDF-4C6C-B393-347F979B16CE.jpeg")
    embed.set_footer(text="❤ Thanks for your support! • Made by Kai")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send("✅ Your feedback has been submitted successfully!", ephemeral=True)

bot.run(TOKEN)
