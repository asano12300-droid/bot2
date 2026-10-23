import discord, plugins, os
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("bot2")
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    update_status.start()

@tasks.loop(seconds=10)
async def update_status():
    status_text = plugins.bstatus(bot=bot)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=status_text))

bot.run(token)