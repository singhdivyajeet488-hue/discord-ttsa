import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import tempfile
from gtts import gTTS

# ── Config ────────────────────────────────────────────────────────────────────
TOKEN  = os.environ["DISCORD_TOKEN"]   # Set in Railway environment variables
PREFIX = os.getenv("PREFIX", "!")
# ─────────────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

LANGUAGES = {
    "english":  "en",
    "hindi":    "hi",
    "french":   "fr",
    "spanish":  "es",
    "german":   "de",
    "japanese": "ja",
    "korean":   "ko",
    "arabic":   "ar",
    "russian":  "ru",
    "italian":  "it",
    "portuguese": "pt",
    "chinese":  "zh",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def generate_tts(text: str, lang: str = "en") -> str:
    """Generate TTS mp3, return temp file path."""
    loop = asyncio.get_event_loop()
    def _gen():
        tts = gTTS(text=text, lang=lang)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir="/tmp")
        tts.save(tmp.name)
        return tmp.name
    return await loop.run_in_executor(None, _gen)


async def ensure_voice(ctx_or_interaction) -> discord.VoiceClient | None:
    """Connect to the author's voice channel if needed. Returns VoiceClient or None."""
    if isinstance(ctx_or_interaction, commands.Context):
        author = ctx_or_interaction.author
        guild  = ctx_or_interaction.guild
    else:
        author = ctx_or_interaction.user
        guild  = ctx_or_interaction.guild

    if not author.voice:
        return None

    channel = author.voice.channel
    vc = guild.voice_client

    if vc and vc.channel != channel:
        await vc.move_to(channel)
    elif not vc:
        vc = await channel.connect()
    return vc


def play_file(vc: discord.VoiceClient, filepath: str):
    if vc.is_playing():
        vc.stop()

    def after(err):
        try:
            os.remove(filepath)
        except Exception:
            pass

    vc.play(discord.FFmpegPCMAudio(filepath), after=after)


# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅  {bot.user} is online  |  Servers: {len(bot.guilds)}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{PREFIX}tts | /tts"
    ))
    try:
        synced = await bot.tree.sync()
        print(f"   Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"   Slash sync error: {e}")


# ── Prefix Commands ───────────────────────────────────────────────────────────

@bot.command(name="join", help="Join your voice channel.")
async def join(ctx: commands.Context):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first.")
    vc = await ensure_voice(ctx)
    await ctx.send(f"🔊 Joined **{vc.channel.name}**")


@bot.command(name="leave", aliases=["dc", "disconnect"], help="Leave the voice channel.")
async def leave(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")
    else:
        await ctx.send("❌ Not in a voice channel.")


@bot.command(name="tts", help="Speak text. Usage: !tts [language] <text>")
async def tts(ctx: commands.Context, *, args: str):
    vc = await ensure_voice(ctx)
    if not vc:
        return await ctx.send("❌ You must be in a voice channel.")

    # Optional language prefix
    lang = "en"
    parts = args.split(maxsplit=1)
    if len(parts) > 1 and parts[0].lower() in LANGUAGES:
        lang = LANGUAGES[parts[0].lower()]
        text = parts[1]
    else:
        text = args

    if not text.strip():
        return await ctx.send("❌ Please provide some text.")

    async with ctx.typing():
        filepath = await generate_tts(text, lang)
        play_file(vc, filepath)
        await ctx.message.add_reaction("🔊")


@bot.command(name="stop", help="Stop current TTS playback.")
async def stop(ctx: commands.Context):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped.")
    else:
        await ctx.send("❌ Nothing is playing.")


@bot.command(name="langs", help="Show supported languages.")
async def langs(ctx: commands.Context):
    desc = "\n".join(f"`{k}` → `{v}`" for k, v in LANGUAGES.items())
    embed = discord.Embed(title="🌐 Supported Languages", description=desc, color=0x5865F2)
    await ctx.send(embed=embed)


@bot.command(name="ping", help="Check bot latency.")
async def ping(ctx: commands.Context):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


# ── Slash Commands ────────────────────────────────────────────────────────────

@bot.tree.command(name="tts", description="Convert text to speech in your voice channel.")
@app_commands.describe(
    text="Text to speak",
    language="Language (e.g. english, hindi, french). Default: english"
)
async def slash_tts(interaction: discord.Interaction, text: str, language: str = "english"):
    await interaction.response.defer(ephemeral=False)
    vc = await ensure_voice(interaction)
    if not vc:
        return await interaction.followup.send("❌ You must be in a voice channel.")

    lang = LANGUAGES.get(language.lower(), "en")
    filepath = await generate_tts(text, lang)
    play_file(vc, filepath)
    await interaction.followup.send(f"🔊 **[{language}]** {text}")


@bot.tree.command(name="join", description="Join your voice channel.")
async def slash_join(interaction: discord.Interaction):
    vc = await ensure_voice(interaction)
    if not vc:
        return await interaction.response.send_message("❌ You must be in a voice channel.")
    await interaction.response.send_message(f"🔊 Joined **{vc.channel.name}**")


@bot.tree.command(name="leave", description="Disconnect from voice.")
async def slash_leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Disconnected.")
    else:
        await interaction.response.send_message("❌ Not in a voice channel.")


@bot.tree.command(name="stop", description="Stop current TTS playback.")
async def slash_stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏹️ Stopped.")
    else:
        await interaction.response.send_message("❌ Nothing is playing.")


# ── Run ───────────────────────────────────────────────────────────────────────

bot.run(TOKEN)
