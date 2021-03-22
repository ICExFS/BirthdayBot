import discord 
from discord.ext import commands

import datetime 
import time
import calendar

import os
import sys

import asyncio
import aiohttp

import json 
import sqlite3

#####################

intents = discord.Intents.default()
intents.members = True 
bot = commands.Bot(command_prefix="b$", intents=intents)

#####################

TOKEN = 'Your bot token goes here'

#####################

class Database:
    def __init__(self):
        self._conn = sqlite3.connect('data.db', check_same_thread=False)
        self._c = self._conn.cursor()
        
        self._xconn = sqlite3.connect("channels.db", check_same_thread=False)
        self._xc = self._xconn.cursor()
        
    def get_today(self, month, day, current_year):
        self._c.execute(f"SELECT user_id FROM birthdays WHERE month={int(month)} AND day={int(day)} AND wished={int(current_year)}")
        r = self._c.fetchall()
        return r
    
    def get_cyear(self, user_id: int):
        self._c.execute(f"SELECT wished FROM birthdays WHERE user_id={int(user_id)}")
        r = self._c.fetchone()
        return r[0]
    
    def edit_cyear(self, user_id: int, newcyear: int):
        self._c.execute(f"UPDATE birthdays SET wished={int(newcyear)} WHERE user_id={int(user_id)}")
        self._conn.commit()
        return
    
    def get_hb(self, guild_id: int):
        self._xc.execute(f"SELECT channel_id FROM database WHERE guild_id={int(guild_id)}")
        r = self._xc.fetchone()
        if r is None:
            return 0
        return r[0]
    
    def get_month(self, user_id: int):
        self._c.execute(f"SELECT month FROM birthdays WHERE user_id={int(user_id)}")
        r = self._c.fetchone()
        if r is None:
            return 0
        return r[0]
    
    def get_day(self, user_id: int):
        self._c.execute(f"SELECT day FROM birthdays WHERE user_id={int(user_id)}")
        r = self._c.fetchone()
        if r is None:
            return 0
        return r[0]

    def set_hb(self, user_id: int, month: int, day: int):
        if self.get_month(user_id) == 0:
            year = datetime.datetime.utcnow().year
            self._c.execute("INSERT INTO birthdays VALUES (?, ?, ?, ?, ?)", (user_id, year, month, day, year))
            self._conn.commit()
            return
        
        self._c.execute(f"UPDATE birthdays SET month={int(month)}, day={int(day)} WHERE user_id={int(user_id)}")
        self._conn.commit()
        return 
    
    def set_channel(self, guild_id: int, channel_id: int):
        if self.get_hb(guild_id) == 0:
            self._c.execute("INSERT INTO database VALUES (?, ?", (guild_id, channel_id))
            self._conn.commit()
            return 
        
        self._c.execute(f"UPDATE database SET channel_id={int(channel_id)} WHERE guild_id={int(guild_id)}")
        self._conn.commit()
        return 
    
d = Database()

#####################

@bot.event
async def on_ready():
    print('Bot Ready')
    while True:
        obj = datetime.datetime.now()
        date = d.get_today(obj.month, obj.day, obj.year)
        await asyncio.sleep(3)
        
        for element in date:
            user_id = element[0]
            try:
                usro = bot.get_user(user_id)
                for guild in bot.guilds:
                    if usro in guild.members:
                        ch = d.get_hb(guild.id)
                        embed = discord.Embed(
                            color = discord.Color.gold()
                        )
                        embed.add_field(name="Happy Birthday! <:Cake:823444405205205054>", value = f"It's {usro.mention} birthday today! <a:Birthday:823447370917609473>")
                        embed.set_footer(text=f'Happy Birthday {usro.name}!', icon_url=usro.avatar_url)
                        if ch == 0:
                            continue 
                        chobj = guild.get_channel(ch)
                        await chobj.send(embed=embed)
                        
                embed = discord.Embed(
                    color = discord.Color.gold(),
                    title = "Happy Birthday! <:Cake:823444405205205054>",
                    description = "Enjoy your day!"
                )
                        
                await usro.send(embed=embed)
                year = d.get_cyear(user_id)
                new_year = year + 1
                d.edit_cyear(user_id, new_year)
            except Exception as e:
                print(e)
                continue
                            
        await asyncio.sleep(3)
    
@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    
@bot.command()
async def set_birthday(ctx, month: int, day: int):
    e = discord.Embed(
        color = discord.Color.red(),
        title = "Error",
        description = "Incorrect date"
    )
    
    if month <= 0 or month >= 13:
        await ctx.send(e)
        return 
    
    if day <= 0 or day >= 32:
        await ctx.send(e)
        return
    
    d.set_hb(ctx.author.id, month, day)
    embed = discord.Embed(
        color = discord.Color.gold(),
        title = "Birthday successfuly registered! <a:Birthday:823447370917609473>",
        description = f"{ctx.author.mention}'s Birthday:\n<:Cake:823444405205205054> Year: *xxxx*\n<:Cake:823444405205205054> Month: {month}\n<:Cake:823444405205205054> Day: {day}"
    )
    await ctx.send(embed=embed)
    
@bot.command()
async def set_channel(ctx, channel: discord.Channel = None):
    if channel is None:
        embed = discord.Embed(
            color = discord.Color.red(),
            title = "Error",
            description = "You didn't specified any channels"
        )
        await ctx.send(embed=embed)
        return 
    if ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            color = discord.Color.green(),
            title = "Succes",
            description = "Successfuly changed birthday channel"
        )
        await ctx.send(embed=embed)
    
@bot.command()
async def bh(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author 
        
    month = d.get_month(member.id)
    day = d.get_day(member.id)
    
    if month == 0 or day == 0:
        embed = discord.Embed(
            color = discord.Color.red(),
            title = "Error",
            description = "This user isn't registered on the database"
        )
        await ctx.send(embed=embed)
        return 
    
    embed = discord.Embed(
        color = discord.Color.gold(),
        title = f"{member.name}'s Birthday: <a:Birthday:823447370917609473>",
        description = f"<:Cake:823444405205205054> Month: {month}\n<:Cake:823444405205205054> Day: {day}"
    )
    await ctx.send(embed=embed)
    
if __name__ == '__main__':
    bot.run(TOKEN)