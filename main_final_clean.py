import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import aiosqlite
import os
from flask import Flask
from threading import Thread

# === Flask Keep Alive ===
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ Bot is alive!"
def keep_alive():
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080}).start()
keep_alive()

# === Get Vars from Railway Secrets ===
TOKEN = os.getenv("TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree
DB_FILE = "vouches.db"

# === Product List (MAX 25) ===
products = [
    ("grandrp-m0n3y", "grandrp-m0n3y"),
    ("grandrp-acc0unt5", "grandrp-acc0unt5"),
    ("1337-ch3at5", "1337-ch3at5"),
    ("custom-discord-bot", "custom-discord-bot"),
    ("custom-ch3at3r", "custom-ch3at3r"),
    ("tr1gg3r-b0t", "tr1gg3r-b0t"),
    ("shax-cl3an3r", "shax-cl3an3r"),
    ("FreeFire-P4N3LS", "FreeFire-P4N3LS"),
    ("FreeFire-D14MONDS", "FreeFire-D14MONDS"),
    ("FreeFire-ACC0UN7S", "FreeFire-ACC0UN7S"),
    ("BGMI-ACC0UN7S", "BGMI-ACC0UN7S"),
    ("BGMI-UC", "BGMI-UC"),
    ("4M4ZON-SHOP", "4M4ZON-SHOP"),
    ("V4LOR4NT-SHOP", "V4LOR4NT-SHOP"),
    ("OTHER PRODUCT", "OTHER PRODUCT")
]

# === Product Select View ===
class ProductSelect(Select):
    def __init__(self, view):
        self.view = view
        options = [discord.SelectOption(label=label, value=value) for value, label in products]
        super().__init__(placeholder="Select a product", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_product = self.values[0]
        await interaction.response.defer()
        self.view.stop()

class ProductView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.selected_product = None
        self.add_item(ProductSelect(self))

# === Rating Select View ===
class RatingSelect(Select):
    def __init__(self, view):
        self.view = view
        options = [
            discord.SelectOption(label="5/5 ⭐⭐⭐⭐⭐", value="5"),
            discord.SelectOption(label="4/5 ⭐⭐⭐⭐", value="4"),
            discord.SelectOption(label="3/5 ⭐⭐⭐", value="3"),
            discord.SelectOption(label="2/5 ⭐⭐", value="2"),
            discord.SelectOption(label="1/5 ⭐", value="1")
        ]
        super().__init__(placeholder="Select a rating", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_rating = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()

class RatingView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.selected_rating = None
        self.add_item(RatingSelect(self))

# === On Ready ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    await bot.change_presence(activity=discord.Game("Vouching Service"))

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

# === /vouch Command ===
@tree.command(name="vouch", description="Vouch for a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to vouch for", feedback="Your feedback")
async def vouch(interaction: discord.Interaction, user: discord.Member, feedback: str):
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't vouch for yourself!", ephemeral=True)
        return

    # Step 1: Select product
    product_view = ProductView()
    await interaction.response.send_message("Please select the product:", view=product_view, ephemeral=True)
    await product_view.wait()
    if not product_view.selected_product:
        await interaction.followup.send("⏰ Timed out or selection not made. Try again.", ephemeral=True)
        return

    # Step 2: Select rating
    rating_view = RatingView()
    await interaction.followup.send("Now select a rating:", view=rating_view, ephemeral=True)
    await rating_view.wait()
    if not rating_view.selected_rating:
        await interaction.followup.send("⏰ Timed out or selection not made. Try again.", ephemeral=True)
        return

    # Save to DB
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO vouches (vouched_user_id, vouched_by_id, product, rating, feedback) VALUES (?, ?, ?, ?, ?)",
            (user.id, interaction.user.id, product_view.selected_product, rating_view.selected_rating, feedback)
        )
        await db.commit()

    # Send Embed to Log Channel
    embed = discord.Embed(title="Feedback Received", description="We received feedback for your transaction!", color=discord.Color.blue())
    embed.add_field(name="Customer", value=f"<@{user.id}>", inline=False)
    embed.add_field(name="Rating", value=f"{rating_view.selected_rating} ⭐", inline=False)
    embed.add_field(name="Feedback", value=f"+rep <@{user.id}> {feedback}", inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123456789/logo.png")  # You can change the image URL
    embed.set_footer(text="Thanks for your support! | Made by Kai")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send("✅ Your vouch has been submitted!", ephemeral=True)

# === Run Bot ===
bot.run(TOKEN)
