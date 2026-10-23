import discord
from discord.ui import View, Button, Modal
import asyncio

ADMIN_ROLE_ID = 1554309276200337418
TICKET_CATEGORY_ID = 1554363808707776602
user_statuses = {}
STATUS_CONFIG = {
    "available": {"label": "対応可能", "emoji": "🟢", "embed_text": "🟢 **対応可能**"},
    "away": {"label": "離席中", "emoji": "🟡", "embed_text": "🟡 **離席中**"},
    "busy": {"label": "対応不可", "emoji": "🔴", "embed_text": "🔴 **対応不可**"},
}

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # タイムアウトなし

    @discord.ui.button(
        label="チケットを閉じる", style=discord.ButtonStyle.danger, emoji="🔒"
    )
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("このチケットチャンネルを5秒後に削除します...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

def create_status_embed() -> discord.Embed:
    """現在の全体対応状況をまとめた Embed を作成する関数"""
    embed = discord.Embed(title="📋 メンバー対応状況", description="下のボタンを押して、あなたの対応状況を切り替えてください。", color=discord.Color.blue())
    if not user_statuses:
        embed.add_field(name="現在の状況", value="登録されているステータスはありません。", inline=False)
    else:
        status_lines = []
        for user_id, info in user_statuses.items():
            status_text = STATUS_CONFIG.get(info["status"], {}).get("embed_text", info["status"])
            status_lines.append(f"• **{info['name']}**: {status_text}")    
        embed.add_field(name="現在の状況", value="\n".join(status_lines), inline=False)
    return embed

class StatusView(discord.ui.View):
    """対応状況変更用のボタン付き View"""
    def __init__(self):
        super().__init__(timeout=None)  # 永続化（タイムアウトなし）にする場合
    async def update_user_status(self, interaction: discord.Interaction, status_key: str):
        """ステータスを更新し、メッセージを再描画する処理"""
        user = interaction.user
        display_name = user.display_name

        # ステータス辞書を更新
        user_statuses[user.id] = {"name": display_name, "status": status_key}

        # 新しいEmbedを作成してメッセージを更新
        new_embed = create_status_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)

    @discord.ui.button(label="対応可能", style=discord.ButtonStyle.green, emoji="🟢", custom_id="status_available")
    async def available_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.update_user_status(interaction, "available")
    @discord.ui.button(label="離席中", style=discord.ButtonStyle.secondary, emoji="🟡", custom_id="status_away")
    async def away_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.update_user_status(interaction, "away")

    @discord.ui.button(label="対応不可", style=discord.ButtonStyle.danger, emoji="🔴", custom_id="status_busy")
    async def busy_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.update_user_status(interaction, "busy")

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="チケットを閉じる", style=discord.ButtonStyle.danger, emoji="🔒️")
    async def close(
        self, button: Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message("このチケットチャンネルを5病後に削除します...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketModal(Modal):
    def __init__(self):
        super().__init__(title="サポートチケットの作成")
        self.add_item(discord.ui.InputText(label="件名", placeholder="例: ファイルのダウンロードができません", max_length=100))
        self.add_item(discord.ui.InputText(label="お問い合わせ内容", style=discord.InputTextStyle.long, placeholder="詳細をご記入ください...", max_length=1000))
    async def callback(self, interaction: discord.Interaction):
        await interaciton,response,defer(ephemeral=True)
        guild = interaction.guild
        title = self.children[0].value
        description = self.children[1].value

        category = guild.get_channel(TICKET_CATEGORY_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)

        if not category or not admin_role:
            await interaction.followup.send("設定エラー: カテゴリーまたは管理者ロールが見つかりません", ephemeral=True)
            return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_message=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }

        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        embed = discord.Embed(
            title=f"🎫 お問い合わせ {title}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="申請者", value=interaction.user.mention, inline=True)
        embed.add_field(name="内容", value=description, inline=False)
        embed.set_footer(
            text="対応が完了したら「チケットを閉じる」を押してください。"
        )

        await ticket_channel.send(
            context=f"{interaction.user.mention} {admin_role.mention}\nサーポートチケットが作成されました。",
            embed=embed,
            view=CloseButton()
        )
        await interaction.followup.send(
            f"専用チケットチャンネルを作成しました: {ticket_channel.mention}",
            ephemeral=True
        )

def setup(select: str):
    if select == "status":
        embed = create_status_embed()
        view = StatusView()
        return embed, view
    elif select == "ticket":
        return TicketModal()