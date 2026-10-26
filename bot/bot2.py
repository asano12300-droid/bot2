import discord
import plugins
import os
from dotenv import load_dotenv
from discord.ext import tasks
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text)

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    original_error = getattr(error, "original", error)
    print(f"エラーが発生しました{original_error}")
    await ctx.respond(f"エラーが発生しました。`{original_error}`", ephemeral=True)

bot.run(token)
