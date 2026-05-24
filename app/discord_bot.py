import asyncio
import discord
from discord import app_commands
from rd_client import RDClient
from config import settings
from auth import generate_guest_token

_DISCORD_MSG_LIMIT = 2000


def create_bot(rd: RDClient) -> discord.Client:
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)
    tree = app_commands.CommandTree(bot)

    @tree.command(name="unrestrict", description="Unrestrict a download link")
    @app_commands.describe(link="The link to unrestrict")
    async def unrestrict(interaction: discord.Interaction, link: str):
        await interaction.response.defer()
        try:
            result = await asyncio.to_thread(rd.unrestrict, link)
            filename = result["filename"]
            token = generate_guest_token(result["download_url"], filename)
            base_url = settings.get("public_base_url")
            if not base_url:
                await interaction.followup.send("PUBLIC_BASE_URL is not set")
                return
            guest_page_url = f"{base_url}/download?t={token}"
            await interaction.followup.send(f"[{filename}]({guest_page_url})")
        except Exception as e:
            await interaction.followup.send(str(e))

    @tree.command(name="hosters", description="List supported hosters")
    async def hosters(interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            hosts = await asyncio.to_thread(rd.supported_hosts)
            lines = []
            for h in hosts:
                indicator = "🟢" if h.get("status") == "up" else "🔴"
                lines.append(f"{indicator} **{h['name']}** ({h['domain']})")
            text = "\n".join(lines) if lines else "No supported hosts found."
            if len(text) > _DISCORD_MSG_LIMIT:
                text = text[:_DISCORD_MSG_LIMIT - 1] + "…"
            await interaction.followup.send(text)
        except Exception as e:
            await interaction.followup.send(str(e))

    @bot.event
    async def on_ready():
        await tree.sync()

    return bot
