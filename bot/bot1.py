import discord, plugins, os, aiohttp, time
from discord import default_permissions
from discord.ext import tasks
from discord.ui import Button, View, Select, Modal, InputText
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("bot1")
bot = discord.Bot(intents=discord.Intents.all())
name1 = plugins.groups(bot,name="setup", description="管理者限定です")
name2 = plugins.groups(bot,name="quiz", description="クイズ集です")

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    update_status.start()

@tasks.loop(seconds=10)
async def update_status():
    status_text = plugins.bstatus(bot=bot)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=status_text))

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext,error: discord.DiscordException):
    original_error = getattr(error, "original", error)
    print(f"エラーが発生しました{original_error}")
    await ctx.respond(f"エラーが発生しました。`{original_error}`", ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user: return
    if message.content == "挨拶して":
        await message.channel.send(f"{message.author.mention}、こんにちは")
        
@bot.slash_command(name="help", description="Botの使い方")
async def help_command(ctx: discord.ApplicationContext):
    embed, view = plugins.help()
    await ctx.respond(embed=embed, view=view, ephemeral=True)

@bot.slash_command(name="rule", description="ルール")
@default_permissions(administrator=True)
async def rule(ctx: discord.ApplicationContext):
    text = "１．荒らしはしないでください\n２．相手が傷つく言葉はしないでください\n３．楽しくやりましょう。"
    await ctx.respond(text)

@bot.slash_command(name="ticket", description="問い合わせチケットを作成")
async def status(ctx: discord.ApplicationContext):
    await ctx.send_modal(plugins.setup(select="ticket"))

# 1. 単語検索用のモーダルクラスを定義
class WordSearchModal(Modal):
    def __init__(self):
      # モーダルのタイトルを設定
      super().__init__(title="英単語検索")

      # 入力フィールドを追加
      self.add_item(
          InputText(
              label="検索したい英単語",
              placeholder="例: apple, python, developer...",
              style=discord.InputTextStyle.short,  # short または paragraph
              required=True,
              max_length=50,
         )
     )

    #callback内でのAPI利用例
    async def callback(self, interaction: discord.Interaction):
        word = self.children[0].value.strip().lower()
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        await interaction.response.defer(ephemeral=False)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entry = data[0]

                    meanings = entry.get("meanings", [])
                    description = ""
                    for m in meanings[:2]:
                        part_of_speech = m.get("partOfSpeech", "")
                        definitions = m.get("definitions", [])
                        if definitions:
                            def_text = definitions[0].get("definition", "")
                            description += (
                                f"**【品詞】** {part_of_speech}\n**【意味】**{def_text}\n\n"
                            )
                    embed = discord.Embed(
                        title=f"📖 検索結果: {entry.get('word')}",
                        description=description,
                        color=discord.Color.blue(),
                    )
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(
                        f"「{word}」が見つからなっかたよ。スペルを確認してね!"
                    )

# 2. スラッシュコマンドでモーダルを呼び出す
@bot.slash_command(name="search", description="英単語を検索するための入力フォームを開きます")
async def search_modal_command(ctx: discord.ApplicationContext):
    # モーダルをインスタンス化して送信
    modal = WordSearchModal()
    await ctx.send_modal(modal)

@name1.command(name="status", description="ステータス")
@default_permissions(administrator=True)
async def status(ctx: discord.ApplicationContext):
    embed, view = plugins.setup(select="status")
    await ctx.respond("作成しました",ephemeral=True)
    await ctx.channel.send(embed=embed, view=view)

@name2.command(name="integral", description="積分の計算問題を出題")
async def integral(ctx: discord.ApplicationContext):
    embed, view = plugins.quiz(select="integral")
    await ctx.respond(embed=embed, view=view)

bot.run(token)
