import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True
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

class ProductSelect(discord.ui.Select):
    def __init__(self, vouched_user, feedback, vouched_by):
        self.vouched_user = vouched_user
        self.feedback = feedback
        self.vouched_by = vouched_by

        options = [discord.SelectOption(label=label, value=value) for value, label in PRODUCTS]
        super().__init__(placeholder="Select the product", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        product = self.values[0]

        # Save to database
        conn = sqlite3.connect("vouches.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vouches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vouched_user_id TEXT,
            vouched_by_id TEXT,
            product TEXT,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute("INSERT INTO vouches (vouched_user_id, vouched_by_id, product, feedback) VALUES (?, ?, ?, ?)",
                  (str(self.vouched_user.id), str(self.vouched_by.id), product, self.feedback))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="New Vouch Received", color=discord.Color.purple())
        embed.add_field(name="Customer", value=self.vouched_user.mention, inline=False)
        embed.add_field(name="Product", value=product, inline=True)
        embed.add_field(name="Feedback", value=self.feedback, inline=False)
        embed.add_field(name="Vouched By", value=self.vouched_by.mention, inline=True)
        embed.set_thumbnail(url=self.vouched_by.avatar.url if self.vouched_by.avatar else None)
        embed.set_footer(text="Thanks for your support! | Made by Kai")

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Vouch submitted!", ephemeral=True)

class ProductView(discord.ui.View):
    def __init__(self, vouched_user, feedback, vouched_by):
        super().__init__(timeout=60)
        self.add_item(ProductSelect(vouched_user, feedback, vouched_by))

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot is online as {bot.user}")

@bot.tree.command(name="vouch", description="Vouch for a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to vouch for", feedback="Your feedback")
async def vouch(interaction: discord.Interaction, user: discord.Member, feedback: str):
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't vouch for yourself!", ephemeral=True)
        return

    await interaction.response.send_message(
        "Please select the product for the vouch:",
        view=ProductView(user, feedback, interaction.user),
        ephemeral=True
    )

bot.run(TOKEN)
