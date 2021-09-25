""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
This is a template to create your own discord bot in python.
https://www.reddit.com/r/FTC/new/.json?count=20
Version: 3.0
"""

import json
import os
import platform
import sys
import math
import time
import requests as r

import discord
from discord.ext import tasks
from discord.ext.commands import Bot
import asyncio
sys.path.append('/opt/app-root/src/project')
import DataFind
"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False

Privileged Intents (Needs to be enabled on dev page), please use them only if you need them:
intents.presences = True
intents.members = True
"""

intents = discord.Intents.default()

bot = Bot(command_prefix='>', intents=intents)
#client = discord.Client()
last_time_checked=time.time()

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    last_time_checked=time.time()
    status_task.start()


# Setup the game status task of the bot
@tasks.loop(minutes=5.0)
async def status_task():
    global last_time_checked
    await bot.change_presence(activity=discord.Game(">help"))
    posts = r.get('https://www.reddit.com/r/FTC/new/.json', headers = {'User-agent': 'your bot 0.1'})
    posts = posts.json()
    posts = posts['data']['children']
    memes = [ x for x in posts if ( x['data']['link_flair_text'] == 'Meme' and x['data']['created_utc'] > last_time_checked ) ]
    memes.reverse()
    for meme in memes:
        embed=discord.Embed(title="New Meme on r/FTC", description="Behold, Meme!", color=0xe67e22, url="https://reddit.com" + meme['data']['permalink'])
        embed.set_author(name=meme['data']['author'], url='https://reddit.com/u/'+meme['data']['author'])
        embed.add_field(name=meme['data']['title'], value=":arrow_down: :arrow_down: :arrow_down:", inline=False)
        url = meme['data']['url']
        if url[-4:] == ".jpg" or url[-4:] == ".png" or url[-5:] == ".jpeg":
            embed.set_image(url=meme['data']['url'])
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="memes")
            if channel:
                await channel.send(embed=embed)
    last_time_checked = math.floor(time.time())


# Removes the default help command of discord.py to be able to create our custom help command.
# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    if message.content[0]=='>':
        out = DataFind.cmd(message.content)
        pages = []
        while len(out) > 5500:
            pages.append(out[:4499]+'-')
            out = out[4499:]
        pages.append( out )
        embs = []
        for page in pages:
            embed=discord.Embed(title="RoboTiger",description=message.content, color=0xe67e22)
            while len(page) > 1024:
                val = page[:1022]
                embed.add_field(name="\u200b",value=val+'-', inline=False)
                page = page[1022:]
            embed.add_field(name="\u200b",value=page, inline=False)
            embs.append( embed )
        buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end
        current = 0
        msg = await message.channel.send(embed=embs[current])
        if len(pages) > 1:
            for button in buttons:
                await msg.add_reaction(button)
                
            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == message.author and reaction.emoji in buttons, timeout=60.0)

                except asyncio.TimeoutError:
                    return print("test")

                else:
                    previous_page = current
                    if reaction.emoji == u"\u23EA":
                        current = 0
                        
                    elif reaction.emoji == u"\u2B05":
                        if current > 0:
                            current -= 1
                            
                    elif reaction.emoji == u"\u27A1":
                        if current < len(embs)-1:
                            current += 1

                    elif reaction.emoji == u"\u23E9":
                        current = len(embs)-1

                    for button in buttons:
                        await msg.remove_reaction(button, message.author)

                    if current != previous_page:
                        await msg.edit(embed=embs[current])

# Run the bot with the token
bot.run(os.environ.get('DISCORD'))
