import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Setup database
conn = sqlite3.connect("vouches.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vouches (
    user_id INTEGER,
    product TEXT,
    feedback TEXT
)''')
conn.commit()

# Products dropdown
class ProductSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="grandrp-m0n3y", value="grandrp-m0n3y"),
            discord.SelectOption(label="grandrp-acc0unt5", value="grandrp-acc0unt5"),
            discord.SelectOption(label="gta5-modmenu", value="gta5-modmenu"),
            discord.SelectOption(label="valorant-points", value="valorant-points"),
            discord.SelectOption(label="nitro-basic", value="nitro-basic"),
            discord.SelectOption(label="nitro-boost", value="nitro-boost"),
            discord.SelectOption(label="spotify-premium", value="spotify-premium"),
            discord.SelectOption(label="netflix", value="netflix"),
            discord.SelectOption(label="custom-service", value="custom-service")
        ]
        super().__init__(placeholder="Select a product", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.product = self.values[0]
        await interaction.response.send_message("Please type your feedback (within 20 seconds):", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await bot.wait_for("message", check=check, timeout=20)
        except:
            await interaction.followup.send("Timed out. Please try again.", ephemeral=True)
            return

        conn = sqlite3.connect("vouches.db")
        c = conn.cursor()
        c.execute("INSERT INTO vouches (user_id, product, feedback) VALUES (?, ?, ?)",
                  (interaction.user.id, self.view.product, msg.content))
        conn.commit()

        embed = discord.Embed(title="New Vouch Received", color=0x9b59b6)
        embed.add_field(name="Customer", value=interaction.user.mention, inline=False)
        embed.add_field(name="Product", value=self.view.product, inline=False)
        embed.add_field(name="Feedback", value=msg.content, inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1236103002533548033/1236107636578709525/logo.jpg")
        embed.set_footer(text="Thanks for your support! | Made by Kai", icon_url="https://cdn.discordapp.com/attachments/1236103002533548033/1236107636578709525/logo.jpg")

        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(embed=embed)

class ProductView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.product = None
        self.add_item(ProductSelect())
        ProductSelect.view = self

@tree.command(name="vouch", description="Submit a vouch for a product")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def vouch(interaction: discord.Interaction):
    await interaction.response.send_message("Please select the product:", view=ProductView(), ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot is ready. Logged in as {bot.user}")

bot.run(TOKEN)
