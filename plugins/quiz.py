import discord
import random
import sympy as sp
import matplotlib
import asyncio
import io
import matplotlib.pyplot as plt
from discord.ui import View, Button

matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'stix'

QUIZ_POOL = {
    "easy": [
        ("x**2", "x", 0, 3),
        ("x**3", "x", 0, 2),
        ("2*x + 1", "x", 1, 3),
        ("x**2 + x", "x", 0, 2),
        ("x**2 + 3x + 6", "x", 0, 3),
        ("x**2 + x + 6", "x", 0, 2),
    ],
    "normal": [
        ("sin(x)", "x", 0, sp.pi),
        ("cos(x)", "x", 0, sp.pi / 2),
        ("exp(x)", "x", 0, 1),
        ("x * cos(x)", "x", 0, sp.pi / 2),
    ],
    "hard": [
        ("x * exp(x**2)", "x", 0, 1),
        ("log(x)", "x", 1, sp.E),
        ("1 / (x**2 + 1)", "x", 0, 1),
        ("x**2 * exp(x)", "x", 0, 1),
    ]
}

def generate_integral_image_sync(f_str, var_str, lower, upper):
    x = sp.Symbol(var_str)
    f = sp.sympify(f_str)

    # 積分計算
    result = sp.integrate(f, (x, lower, upper))
    
    # SymPyでLaTeX文字列を生成
    latex_code = sp.latex(sp.Integral(f, (x, lower, upper)))
    
    # Matplotlibが対応していない '\limits' を除去
    latex_code = latex_code.replace(r'\limits', '')
    latex_string = f"${latex_code}$"

    # Matplotlib 描画設定
    fig, ax = plt.subplots(figsize=(4.5, 1.5), facecolor='#313338')
    ax.axis('off')
    ax.text(0.5, 0.5, latex_string, fontsize=22, ha='center', va='center', color='white')
    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)  
    buf.seek(0)
    plt.close(fig)
    return buf, result

class AnswerModal(discord.ui.Modal):
    def __init__(self, correct_answer, parent_view: View):
        super().__init__(title="積分の答えを入力")
        self.correct_answer = correct_answer
        self.parent_view = parent_view
        self.answer_input = discord.ui.InputText(
            label="計算結果を入力してください（分数・e・pi対応）",
            placeholder="例: 9, 15/2, exp(1)-1, pi/4 など",
            required=True
        )
        self.add_item(self.answer_input)

    async def callback(self, interaction: discord.Interaction):
        if getattr(self.parent_view, "answered", False):
            await interaction.response.send_message("この問題は既に解答されています。", ephemeral=True)
            return
        self.parent_view.answered = True
        user_answer_str = self.answer_input.value.strip()
        try:
            # 入力文字列をSymPy数式として評価
            user_ans = sp.sympify(user_answer_str)
            correct_ans = self.correct_answer

            for child in self.parent_view.children:
                child.disabled = True

            # 差分が0（数学的同値）か判定
            if sp.simplify(user_ans - correct_ans) == 0:
                embed = discord.Embed(title="🎉 正解!", description=f"{interaction.user.mention} さん、正解です！\n答え: `{sp.pretty(correct_ans)}`",color=discord.Color.green())
            else:
                embed = discord.Embed(
                    title="❌ 不正解...",
                    description=f"{interaction.user.mention} さん、残念ながら不正解です。\n**正解:** `{correct_ans}`",
                    color=discord.Color.red()
                )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

        except Exception:
            for child in self.parent_view.children:
                child.disabled = True
            embed = discord.Embed(
                title="⚠️ エラー",
                description="入力された数式・数値の形式を解析できませんでした。",
                color=discord.Color.orange()
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

# クイズ出題後の「解答する」ボタンを持つView
class IntegralStartView(View):
    def __init__(self, correct_answer):
        super().__init__(timeout=120)
        self.correct_answer = correct_answer
        self.answered = False

    @discord.ui.button(label="解答する", style=discord.ButtonStyle.primary, emoji="✍")
    async def answer_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.answered:
            await interaction.response.send_message("この問題は既に終了しています。", ephemeral=True)
            return
        modal = AnswerModal(self.correct_answer, parent_view=self)
        await interaction.response.send_modal(modal)

# 難易度選択ボタンを表示するView
class DifficultySelectView(View):
    def __init__(self):
        super().__init__(timeout=60)

    async def start_quiz_by_difficulty(self, interaction: discord.Interaction, difficulty_key: str, diff_label: str):
        # 1. インタラクションの処理を開始（ローディング状態にする）
        await interaction.response.defer()

        # 難易度に応じたプールから選択
        f_str, var_str, lower, upper = random.choice(QUIZ_POOL[difficulty_key])

        try:
            # 別スレッドで画像と正解を生成
            img_buf, correct_ans = await asyncio.to_thread(generate_integral_image_sync, f_str, var_str, lower, upper)

            filename = "integral.png"
            file = discord.File(fp=img_buf, filename=filename)

            embed = discord.Embed(title=f"📐 積分計算クイズ 【難易度: {diff_label}】", description="以下の定積分を計算してください。下の「解答する」ボタンを押して答えを入力できます。", color=discord.Color.blurple())
            embed.set_image(url=f"attachment://{filename}")
            view = IntegralStartView(correct_ans)

            # 元の「難易度選択メッセージ」をクイズ画面に上書き更新
            await interaction.edit_original_response(content=None, embed=embed, file=file, view=view)
        except Exception as e:
            print(f"[ERROR] 積分画像生成エラー: {e}")
            await interaction.followup.send("⚠️ 画像の生成中にエラーが発生しました。", ephemeral=True)

    @discord.ui.button(label="かんたん", style=discord.ButtonStyle.success, emoji="🟢")
    async def easy_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.start_quiz_by_difficulty(interaction, "easy", "かんたん")

    @discord.ui.button(label="ふつう", style=discord.ButtonStyle.primary, emoji="🟡")
    async def normal_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.start_quiz_by_difficulty(interaction, "normal", "ふつう")

    @discord.ui.button(label="むずかしい", style=discord.ButtonStyle.danger, emoji="🔴")
    async def hard_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.start_quiz_by_difficulty(interaction, "hard", "むずかしい")

def quiz(select: str):
    if select == "integral":
        embed = discord.Embed(title="📐 積分計算クイズ", description="チャレンジする難易度を選択してください！", color=discord.Color.blue())
        view = DifficultySelectView()
    return embed, view