import time
import discord
from discord.ext import commands
import sqlite3
import random
import os
from dotenv import load_dotenv
load_dotenv()

OS = "WINDOWS"
VARS = {
    "WINDOWS" : {
        "PATH" : "E:/Dev/Wyn/wyndb2.db"
    },
    "LINUX" : {
        "PATH" : "/home/Hosting/Wyn/wyndb2.db"

    }
}
OWNERS = [290482004435271680,245635263697518603]


intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='?', description="Bot multifonctions ! Gaming, modération et tout",intents=intents)
conn = sqlite3.connect(VARS[OS]["PATH"])

DAILYBONUS = 100 # 100
DAILYCOOLDOWN = 86400 # 86400
XPCOOLDOWN = 10 # 60
XPMIN = 15 # 4
XPMAX = 20 # 10
XPCURVE = 1.5 # 1.5

ALPHABET = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

@bot.event
async def on_ready():
    print('Logged in as ' + str(bot.user) + ' !')
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS members(
                id INTEGER,
                coins INTEGER,
                xp INTEGER,
                xptonextlvl INTEGER,
                level INTEGER)
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns(
                id INTEGER,
                daily INTEGER,
                xp INTEGER)
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory(
                id INTEGER,
                item TEXT,
                quantity INTEGER)
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS itemdata(
                id INTEGER,
                ticket TEXT)
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot(
                itemidcounter INTEGER)
        """)
    cursor.close()

    print("done!")

@bot.event
async def on_message(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False 
    if exists and ctx.author is not bot and not 'Direct' in str(ctx.channel):
        print(ctx.channel)
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
        cursor.execute("""INSERT INTO inventory(id,item,quantity) VALUES(?,?,?)""",(ctx.author.id,"ticket",0))    
        cursor.execute("""INSERT INTO cooldowns(id,daily,xp) VALUES(?,?,?)""",(ctx.author.id,0,0))  
        cursor.execute("""INSERT INTO itemdata(id,ticket) VALUES(?,?)""",(ctx.author.id,"No ticket"))  
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
        await ctx.send("Niveau : **" + str(lvl[0][0]) + "** (Points d'xp : **" + str(xp[0][0]) + "**)\nNiveau suivant dans : **" + str(xptonextlevel[0][0]) + "** points d'xp.")        


@bot.command()
async def give_coins(ctx,receiver,amount):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        sender = ctx.author
        await ctx.send("sender : " + str(sender) + "receiver : " + str(receiver))
        print(sender)
        print(receiver)
        cursor = conn.cursor()
        cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
        sender_coins = cursor.fetchall()
        print(amount)
        print(sender_coins[0][0])
        if sender_coins[0][0] >= int(amount):
            print("YES")
            cursor = conn.cursor()
            cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
            receiver_coins = cursor.fetchall()
            cursor.execute("""UPDATE members SET coins = :coins WHERE id = :uuid""",{"uuid" : receiver.id, "coins" : receiver_coins[0][0] + amount})
            cursor.execute("""UPDATE members SET coins = :coins WHERE id = :uuid""",{"uuid" : ctx.author.id, "coins" : sender_coins[0][0] - amount})
        else:
            print("NO ")


@bot.command()
async def shop(ctx,item):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        cursor = conn.cursor()
        cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
        coins = cursor.fetchall()
        if item.lower() == "ticket" and coins[0][0] >= 100:
            cursor.execute("""UPDATE members SET coins = :coins WHERE id = :uuid""",{"uuid" : ctx.author.id, "coins" : coins[0][0] - 100})
            await ticket_gen(ctx.author.id)


@bot.command()
async def ticket(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists:
        cursor = conn.cursor()
        cursor.execute("""SELECT ticket FROM itemdata WHERE id = :uuid""",{"uuid" : ctx.author.id})
        a = cursor.fetchone()
        await ctx.send("Voici ton ticket : " + str(a[0]))
        

@bot.command()
async def tirage(ctx):
    try:
        exists = ctx.author.id in conn.cursor().execute("""SELECT id FROM members where id = :uuid""",{"uuid" : ctx.author.id}).fetchone()
    except TypeError:
        exists = False
    if exists and ctx.author.id in OWNERS:
        preticket = [ALPHABET[random.randint(0,0)] for i in range(7)]
        ticket = ''.join(preticket)
        ticketdisplay = ' '.join(preticket)
        cursor = conn.cursor()
        cursor.execute("""SELECT ticket,id FROM itemdata""")
        all_tickets = cursor.fetchall()
        print(all_tickets)
        await ctx.send("Le résultat du tirage est : " + str(ticketdisplay))
        for entry in all_tickets:
            if entry[0] != "NO":
                if entry[0] == ticket:
                    print(str(entry[1]) + " wons !")
                    await ctx.send(str(bot.get_user(entry[1])) + " gagne le loto OMG !")
                    cursor = conn.cursor()
                    cursor.execute("""SELECT coins FROM members WHERE id = :uuid""",{"uuid" : ctx.author.id})
                    coins = cursor.fetchall()
                    cursor.execute("""UPDATE members SET coins = :coins WHERE id = :uuid""",{"uuid" : entry[1], "coins" : coins[0][0] + 10000})
                    conn.commit()
                cursor.execute("""UPDATE inventory SET quantity = :quantity WHERE id = :uuid and item = :item""",{"uuid" : entry[1], "item" : "ticket", "quantity" : 0})
                cursor.execute("""UPDATE itemdata SET ticket = :tick WHERE id = :uuid""",{"uuid" : entry[1], "tick" : "NO"})
                print("on suppr")
                conn.commit()
                print("et on commit")

        await ctx.send("Merci a tous")






async def ticket_gen(id):
    cursor = conn.cursor()
    cursor.execute("""SELECT quantity FROM inventory WHERE id = :uuid and item = :item""",{"uuid" : id, "item" : "ticket"})
    print(cursor.fetchall())
    preticket = [ALPHABET[random.randint(0,0)] for i in range(7)]
    ticket = ''.join(preticket)
    print("ticket is" + str(ticket))
    #newitemid = await generate_item_id()
    cursor = conn.cursor()
    #cursor.execute("""UPDATE inventory SET itemid = :id WHERE id = :uuid""",{"uuid" : id, "itemid" : newitemid})
    cursor.execute("""UPDATE inventory SET quantity = :quantity WHERE id = :uuid and item = :item""",{"uuid" : id, "item" : "ticket", "quantity" : 1})
    print("ok done")
    cursor = conn.cursor()
    cursor.execute("""UPDATE itemdata SET ticket = :tick WHERE id = :uuid""",{"uuid" : id, "tick" : str(ticket)})
    conn.commit()
    cursor.execute("""SELECT ticket FROM itemdata WHERE id = :uuid""",{"uuid" : id})
    a = cursor.fetchone()
    print("rrrrrrr" + str(a[0]))




#async def generate_item_id():
#    cursor = conn.cursor()
#    cursor.execute("""SELECT itemidcounter FROM bot""")
#    res = cursor.fetchall()
#    maxid = res[0][0]
#    cursor = conn.cursor()
#    cursor.execute("""UPDATE bot SET itemidcounter = :itemid""",{"itemid" : maxid + 1})
#    return maxid + 1


bot.run(os.getenv("TOKEN"))