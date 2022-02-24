import time
import discord
from discord.ext import commands
import sqlite3
import random

intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='?', description="Bot multifonctions ! Gaming, modération et tout",intents=intents)
conn = sqlite3.connect("M:/Dev/Projects/Wyn/wyn.db")

DAILYBONUS = 100 # 100
DAILYCOOLDOWN = 86400 # 86400
XPCOOLDOWN = 10 # 60
XPMIN = 15 # 4
XPMAX = 20 # 10
XPCURVE = 1.5 # 1.5

@bot.event
async def on_ready():
    print('Logged in as ' + str(bot.user) + ' !')
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS members(
                id INTEGER PRIMARY KEY UNIQUE,
                coins INTEGER,
                xp INTEGER,
                xptonextlvl INTEGER,
                level INTEGER)
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns(
                id INTEGER PRIMARY KEY UNIQUE,
                daily INTEGER,
                xp INTEGER)
        """)
    cursor.close()

    print("done!")

@bot.event
async def on_message(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False 
    if exists and ctx.author is not bot:
        cursor = conn.cursor()
        cursor.execute("""SELECT xp FROM cooldowns where id = :uuid""",{"uuid" : ctx.author.id})
        cd = cursor.fetchall()
        print(cd[0][0],time.time())
        if cd[0][0] <= time.time():
            cursor = conn.cursor()
            cursor.execute("""SELECT xp FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            xp = cursor.fetchall()
            cursor.execute("""SELECT level FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            level = cursor.fetchall()
            cursor.execute("""SELECT xptonextlvl FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            xptonextlvl = cursor.fetchall()
            print(xp[0][0],level[0][0])
            await ctx.channel.send(f"Tu as gagnes de l'xp !,{xp},{level},{xptonextlvl}")
            newxp = xp[0][0] + random.randint(XPMIN,XPMAX)
            if newxp >= xptonextlvl[0][0]:
                await ctx.channel.send("Level up !")
                cursor.execute("""UPDATE members SET xptonextlvl = :xptonextlevel""",{"xptonextlevel": xptonextlvl[0][0] * XPCURVE})
                cursor.execute("""UPDATE members SET level = :lvl where id = :uuid""",{"uuid":ctx.author.id,"lvl" : level[0][0] + 1})
                conn.commit()
            cursor.execute("""UPDATE members SET xp = :xp WHERE id = :uuid""",{"uuid" : ctx.author.id, "xp" : newxp})
            cursor.execute("""UPDATE cooldowns SET xp = :cd WHERE id = :uuid""",{"uuid" : ctx.author.id, "cd" : time.time() + XPCOOLDOWN})
            conn.commit()
            cursor.execute("""SELECT xp FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            xp = cursor.fetchall()
            cursor.execute("""SELECT level FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            level = cursor.fetchall()
            cursor.execute("""SELECT xptonextlvl FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            xptonextlvl = cursor.fetchall()
            await ctx.channel.send(f"Transacs validées,{xp},{level},{xptonextlvl}")

            
    else:
        print("wtf")
    await bot.process_commands(ctx)
        

@bot.command()
async def ping(ctx):
    """Responds with Pong!"""
    await ctx.send("Pong ! (" + str(round(bot.latency * 1000)) + " ms)")

@bot.command()
async def repeat(ctx,arg1):
    await ctx.send(arg1)

@bot.command()
async def coins(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        cursor = conn.cursor()
        cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
        bank = cursor.fetchall()
        await ctx.send("Tu as " + str(bank[0][0]) + " coins !")

@bot.command()
async def start(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if not exists:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO members(id,coins,xp,xptonextlvl,level) VALUES(?,?,?,?,?)""",(ctx.author.id,100,0,100,0))  
        cursor.execute("""INSERT INTO cooldowns(id,daily,xp) VALUES(?,?,?)""",(ctx.author.id,0,0))
        conn.commit()
        await ctx.send("Bienvenue ! Un petit tuto t'a été envoyé en MP :)")
        await ctx.author.send("e")
    else:
        await ctx.send("Désolé, tu es déjà inscrit !") 

@bot.command()
async def ts(ctx):
    ts = time.time()
    await ctx.send("Current timestamp : " + str(ts))
    ts += 86400
    await ctx.send("In 24 hours : " + str(ts))

@bot.command()
async def daily(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        cursor = conn.cursor()
        cursor.execute("""SELECT daily FROM cooldowns WHERE id = :uuid""",{"uuid" : ctx.author.id})
        cd = cursor.fetchall()
        print(cd)
        print(time.time())
        if cd[0][0] <= time.time():
            await ctx.send("Tu as récupéré ton daily ! + 100 Coins")
            cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            coins = cursor.fetchall()
            cursor.execute("""UPDATE members SET coins = :coins WHERE id = :uuid""",{"uuid" : ctx.author.id, "coins" : coins[0][0] + DAILYBONUS})
            cursor.execute("""UPDATE cooldowns SET daily = :cd WHERE id = :uuid""",{"uuid" : ctx.author.id, "cd" : time.time() + DAILYCOOLDOWN})
            conn.commit()
            await ctx.send("Transacs validées") 
        else:
            await ctx.send("Tu as déjà récupéré ton daily !")

@bot.command()
async def xp(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        cursor = conn.cursor()
        cursor.execute("""SELECT xp FROM members WHERE id = :uuid""",{"uuid":ctx.author.id})
        xp = cursor.fetchall()
        cursor.execute("""SELECT level FROM members WHERE id = :uuid""",{"uuid":ctx.author.id})
        lvl = cursor.fetchall()
        cursor.execute("""SELECT xptonextlvl FROM members WHERE id = :uuid""",{"uuid":ctx.author.id})
        xptonextlevel = cursor.fetchall()
        await ctx.send("Tu es actuellement niveau **" + str(lvl[0][0]) + "**, avec **" + str(xp[0][0]) + "** points d'xp. Pour atteindre le niveau suivant, il va te falloir **" + str(xptonextlevel[0][0]) + "** points d'xp.")        


@bot.command()
async def give_coins(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        pass

@bot.command()
async def shop(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        pass




bot.run("OTM4MDY4MTQzNTgxMDU3MDM1.Yfk6CQ.qGLYH1UGcFWcAbDrXIbCdA6ixpM")