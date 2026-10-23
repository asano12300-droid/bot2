import discord
from discord.ui import Select, View

commands = {
    "basic": {
        "`/help`": "このヘルプメニューを表示します。",
        "`/ping`": "Botの応答速度（レイテンシ）を計測します。",
        "`/setup_status`": "[管理者用] 管理者の対応状況を表します。",
    },
    "game": {
        "`/game tetris`": "Discord内でテトリスを遊びます。",
        "`/game tictactoe`": "Discord内でマルバツゲームを遊べます",
    },
    "quiz": {
        "`/quiz integral`": "Discord内で積分計算ができます",
        "`/quiz english`": "Discord内で英単語のチェックができます",
    }
}

sorts = {
    "basic": "全般コマンド一覧",
    "game": "🎮 お楽しみコマンド一覧",
    "quiz": "クイズ一覧",
}

class HelpDropdown(Select):
    def __init__(self):
       options = [
           discord.SelectOption(label="basic", description="誰でも使える基本コマンド"),
           discord.SelectOption(label="game", description="テトリスなどのゲーム機能"),
           discord.SelectOption(label="quiz", description="積分計算などのクイズ機能"),
       ]
       super().__init__(placeholder="確認したいカテゴリーを選択してください．．．", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        sort = self.values[0]
        command = commands[sort]
        embed = discord.Embed(title=sorts[sort], color=discord.Color.blue())
        for name, value in command.items():
            embed.add_field(name=name, value=value, inline=False)
        await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=self.view)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown())

def help():
    embed = discord.Embed(title="📚 Bot ヘルプメニュー", description="下のドロップダウンメニューから、調べたい機能のカテゴリーを選択してください。", color=discord.Color.light_gray())
    embed.add_field(name="現在のバージョン", value="`v2.0.0` (Py-cord 2026)", inline=True)
    view = HelpView()
    return embed, view
