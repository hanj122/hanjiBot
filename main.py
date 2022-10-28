from distutils.log import debug, error
from nextcord.ext import commands
import json
import random
import datetime
import asyncio
import textwrap
from nextcord import File, ButtonStyle, Embed, Color, SelectOption, Intents, Interaction, SlashOption, Member
from nextcord.ui import Button, View, Select
import json, random, datetime, asyncio
import nextcord
import wavelink
from wavelink.ext import spotify
import ffmpeg
import youtube_dl
from gtts import gTTS
import discord
import os
from discord.ext import commands
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)


import Bot_token

# embeded commands
@client.command(name='commands')
async def embed(ctx):
    embed = nextcord.Embed(title = "Commands",)
    embed.add_field(name= "School Schedule:", value = "!schedule", inline = True)
    embed.add_field(name= "Owner profile:", value = "!owner", inline = True)
    embed.add_field(name= "User profile:", value= "!userprofile", inline = True)
    embed.add_field(name= "User profile picture:", value= "!userpfp", inline = True)
    embed.add_field(name= "Listen to music (YT ONLY):", value= "!stream **search**", inline = True)
    embed.add_field(name= "Stop music:", value= "!stop", inline = True)
    embed.add_field(name= "Change music volume:", value= "!volume **NUMBER**", inline = True)
    embed.add_field(name= "Google TTS:", value= "!tts **your text**", inline = True)
    embed.add_field(name= "Leave:", value= "!leave", inline = True)
    embed.set_footer(text = "made by hanji", icon_url = "wont put any links here lol")
    await ctx.send(embed=embed)
wont put any links here lol

# owner discord #'s
@client.command(name="owner")
async def SendMessage(ctx):
    await ctx.reply('hanj¡#8190 or hanji#7673')

# user profile command
@client.command(name="userprofile")
async def Profile(ctx, user: Member=None):
	if user == None:
		user = ctx.message.author
	inline = True
	embed=Embed(title=user.name+"#"+user.discriminator, color=0xFFFFFF)
	userData = {
		"Mention" : user.mention,
		"Nickname" : user.nick,
		"Account Created" : user.created_at.strftime("%b %d, %Y, %T"),
		"Joined this server" : user.joined_at.strftime("%b %d, %Y, %T"),
		"Server" : user.guild,
		"Top role" : user.top_role
	}
	for [fieldName, fieldVal] in userData.items():
		embed.add_field(name=fieldName+":", value=fieldVal, inline=inline)
	embed.set_footer(text=f"id: {user.id}")
	
	embed.set_thumbnail(user.display_avatar)
	await ctx.send(embed=embed)

# userpfp 
@client.command(name="userpfp")
async def Profile(ctx, user: Member=None):
	if user == None:
		user = ctx.message.author
	inline = True
	embed=Embed(title=user.name+"#"+user.discriminator, color=0xFFFFFF)
	
	embed.set_thumbnail(user.display_avatar)
	await ctx.send(embed=embed)


# tts
@client.command(name='tts')
async def tts(ctx, *args):
    text = " ".join(args)
    user = ctx.message.author
    if user.voice != None:
        try:
            vc = await user.voice.channel.connect()
        except:
            vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()

        myobj = gTTS(text=text, lang="en", slow=False)
        myobj.save("tts-audio.mp3")

        source = await nextcord.FFmpegOpusAudio.from_probe("tts-audio.mp3", method='fallback')
        vc.play(source)
    else:
        await ctx.send('You need to be in a vc to run this command!')

# tts leave
@client.command(name='leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("Bye! 👋")

#musicbot
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0", 
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: nextcord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        source = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)

        await ctx.send(f"Now playing: {query}")

    @commands.command()
    async def yt(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def stream(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: **{player.title}**")

    @commands.command()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

client.add_cog(Music(client))

#buttons for schedule
    
@client.command(name='schedule')
# async def embed(ctx,):
#     embed = nextcord.Embed(title = "choose your section",)
#     embed.set_image(url = "https://cdn.discordapp.com/attachments/934074316914577459/1031496747253501962/unknown.png" )
#     await ctx.send(embed=embed)

async def support(ctx,):
    Section1 = Button(label="10-C (Tech High)", style=ButtonStyle.success)
    Section2 = Button(label="A10A", style=ButtonStyle.success)
    Section3 = Button(label="A10B", style=ButtonStyle.success)
    Section4 = Button(label="A10C", style=ButtonStyle.success)
    Section5 = Button(label="H10A", style=ButtonStyle.success)
    Section6 = Button(label="H10B", style=ButtonStyle.success)
    Section7 = Button(label="H10C", style=ButtonStyle.success)
    Section8 = Button(label="S10A", style=ButtonStyle.success)
    Section9 = Button(label="S10B", style=ButtonStyle.success)
    Section10 = Button(label="S10C", style=ButtonStyle.success)
    Section11 = Button(label="S10D", style=ButtonStyle.success)
    Section12 = Button(label="S10E", style=ButtonStyle.success)
    Section13 = Button(label="S10F", style=ButtonStyle.success)
    Section14 = Button(label="S10G", style=ButtonStyle.success)
    supportme = Button(label= "Support me!" , url="wont put any links here lol")

    async def Section2_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section3_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")
    
    async def Section5_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section6_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section7_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section8_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")
    
    async def Section9_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section10_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section11_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section14_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section4_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section1_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")

    async def Section12_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")
    
    async def Section13_callback(interaction):
        await interaction.response.send_message("wont put any links here lol")
    
    Section1.callback = Section1_callback
    Section2.callback = Section2_callback
    Section3.callback = Section3_callback
    Section4.callback = Section4_callback
    Section5.callback = Section5_callback
    Section6.callback = Section6_callback
    Section7.callback = Section7_callback
    Section8.callback = Section8_callback
    Section9.callback = Section9_callback
    Section10.callback = Section10_callback
    Section11.callback = Section11_callback
    Section12.callback = Section12_callback
    Section13.callback = Section13_callback
    Section14.callback = Section14_callback

    myview = View(timeout=20)
    myview.add_item(Section1)
    myview.add_item(Section2)
    myview.add_item(Section3)
    myview.add_item(Section4)
    myview.add_item(Section5)
    myview.add_item(Section6)
    myview.add_item(Section7)
    myview.add_item(Section8)
    myview.add_item(Section9)
    myview.add_item(Section10)
    myview.add_item(Section11)
    myview.add_item(Section12)
    myview.add_item(Section13)
    myview.add_item(Section14)
    myview.add_item(supportme)

    await ctx.send("**Sections:**", view=myview)

@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Game(name= '!commands'))
    
client.run(Bot_token.TOKEN)