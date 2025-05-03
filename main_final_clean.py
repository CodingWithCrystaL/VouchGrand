import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os
import asyncio

TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])
VOUCH_CHANNEL_ID = int(os.environ['VOUCH_CHANNEL_ID'])

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
conn = sqlite3.connect("vouches.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vouches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    customer TEXT,
    product TEXT,
    feedback TEXT
)''')
conn.commit()

class ProductSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="grandrp-m0n3y"),
            discord.SelectOption(label="grandrp-acc0unt5"),
            discord.SelectOption(label="gta5-m0d"),
            discord.SelectOption(label="fortnite-vbux"),
            discord.SelectOption(label="gta5-outfit"),
            discord.SelectOption(label="discord-nitro"),
            discord.SelectOption(label="gta5-account"),
            discord.SelectOption(label="spotify-premium"),
            discord.SelectOption(label="netflix-premium"),
            discord.SelectOption(label="telegram-members")
        ]
        super().__init__(placeholder="Select a product", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_product = self.values[0]
        await interaction.response.send_message("Now type your feedback:", ephemeral=True)

class ProductView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.selected_product = None
        self.add_item(ProductSelect())

@bot.tree.command(name="vouch", description="Vouch for a user")
@app_commands.describe(user="User to vouch for")
async def vouch(interaction: discord.Interaction, user: discord.User):
    view = ProductView()
    await interaction.response.send_message("Please select a product:", view=view, ephemeral=True)

    timeout = await view.wait()
    if timeout or not view.selected_product:
        await interaction.followup.send("Timed out or no product selected.", ephemeral=True)
        return

    await interaction.followup.send("Type your feedback:", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await bot.wait_for("message", timeout=60, check=check)
    except asyncio.TimeoutError:
        await interaction.followup.send("Feedback not received in time.", ephemeral=True)
        return

    customer = interaction.user.mention
    product = view.selected_product
    feedback = msg.content

    c.execute("INSERT INTO vouches (user_id, customer, product, feedback) VALUES (?, ?, ?, ?)",
              (str(user.id), customer, product, feedback))
    conn.commit()

    embed = discord.Embed(title="New Vouch Received", color=discord.Color.dark_magenta())
    embed.add_field(name="Customer", value=customer, inline=False)
    embed.add_field(name="Product", value=product, inline=False)
    embed.add_field(name="Feedback", value=feedback, inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1230847784354521118/1225712406036998204/6EAA5AB2-0DC4-445A-AF89-0B5A3823D21B.jpeg")
    embed.set_footer(text="Thanks for your support! | Made by Kai", icon_url="https://cdn.discordapp.com/attachments/1230847784354521118/1225712406036998204/6EAA5AB2-0DC4-445A-AF89-0B5A3823D21B.jpeg")

    channel = bot.get_channel(VOUCH_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send("Vouch submitted successfully!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot is ready. Logged in as {bot.user}")

bot.run(TOKEN)
