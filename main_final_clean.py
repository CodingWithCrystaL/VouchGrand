import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import aiosqlite
import os
from flask import Flask
from threading import Thread

# === KEEP ALIVE ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

def keep_alive():
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080}).start()

keep_alive()

# === DISCORD BOT SETUP ===
TOKEN = os.getenv("TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

DB_FILE = "vouches.db"

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

class ProductRatingView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.product_select = Select(
            placeholder="Select a product",
            options=[discord.SelectOption(label=label, value=value) for value, label in products[:25]],
            custom_id="product"
        )
        self.rating_select = Select(
            placeholder="Select a rating",
            options=[
                discord.SelectOption(label="5/5 ⭐⭐⭐⭐⭐", value="5"),
                discord.SelectOption(label="4/5 ⭐⭐⭐⭐", value="4"),
                discord.SelectOption(label="3/5 ⭐⭐⭐", value="3"),
                discord.SelectOption(label="2/5 ⭐⭐", value="2"),
                discord.SelectOption(label="1/5 ⭐", value="1")
            ],
            custom_id="rating"
        )
        self.add_item(self.product_select)
        self.add_item(self.rating_select)
        self.selected_product = None
        self.selected_rating = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        await interaction.response.send_message("❌ Something went wrong.", ephemeral=True)
        self.stop()

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

@tree.command(name="vouch", description="Vouch for a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to vouch for", feedback="Your feedback message")
async def vouch(interaction: discord.Interaction, user: discord.Member, feedback: str):
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't vouch for yourself!", ephemeral=True)
        return

    view = ProductRatingView()
    await interaction.response.send_message("Please select the product and rating:", view=view, ephemeral=True)
    timeout = await view.wait()

    if timeout or not view.product_select.values or not view.rating_select.values:
        await interaction.followup.send("⏰ Timed out or selection not made. Try again.", ephemeral=True)
        return

    product = view.product_select.values[0]
    rating = int(view.rating_select.values[0])

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO vouches (vouched_user_id, vouched_by_id, product, rating, feedback) VALUES (?, ?, ?, ?, ?)",
            (user.id, interaction.user.id, product, rating, feedback)
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        vouch_id = (await cursor.fetchone())[0]

    embed = discord.Embed(title="Feedback Received", description="We received feedback for your transaction!", color=discord.Color.purple())
    embed.add_field(name="Customer", value=f"<@{user.id}>", inline=False)
    embed.add_field(name="Rating", value=f"{rating} ⭐", inline=False)
    embed.add_field(name="Feedback", value=f"+rep <@{user.id}> {feedback}", inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123456789/logo.png")  # Replace with your actual hosted image
    embed.set_footer(text="Thanks for your support! | Made by Kai")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send("✅ Your vouch has been submitted successfully!", ephemeral=True)

bot.run(TOKEN)
