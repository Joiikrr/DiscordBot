import json
import operator
import pandas as pd
from pandas import json_normalize
import discord 
from discord.ext import commands, tasks

client = commands.Bot(command_prefix='>')
general = 760654051443867660
admin = 760790658801205278



@client.event
async def on_ready():
    print("Bot is ready")

@client.command()
async def leader(ctx):
    with open('score.txt', 'r') as file:
        content = file.read()
        jContent = json.loads(content)
        big = 0
        leaders = []
        #print(jContent.items())
        for (k,v) in jContent.items():
            if v < big:
                pass
            elif v == big:
                leaders.append(k)
            elif v > big:
                big = v
                leaders.clear()
                leaders.append(k)
            #print(k,v)
        file.close()
        #print(leaders)
    await ctx.send(f"{leaders} had the most kills today with {big} kills")

@tasks.loop(hours=24)
async def called_once_a_day(): #actually once every two days
    message_channel = client.get_channel(general)
    print(f"Got channel {message_channel}")
    with open('score.txt', 'r') as file:
        content = file.read()
        jContent = json.loads(content)
        big = 0
        leaders = []
        #print(jContent.items())
        for (k,v) in jContent.items():
            if v < big:
                pass
            elif v == big:
                leaders.append(k)
            elif v > big:
                big = v
                leaders.clear()
                leaders.append(k)
            #print(k,v)
        file.close()
        #print(leaders)
    if leaders != []:
        # await message_channel.send(f"{leaders} has the most kills with {big} kills")
        # await message_channel.send("Don't forget to log your wins with >won [your_name]")
        pass
    leaders = []

@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()
    print("Finished waiting")


@client.command()
async def rules(ctx):
    with open('rules.txt', 'r') as f:
        await ctx.send(f.read())

@client.command()
async def hello(ctx):
    await ctx.send("Welcome to the Among Us discord server.")
    await ctx.send("I keep track of imposter wins and will help to schedule sessions :)")

@client.command()
async def add(ctx, *, names):
    with open('score.txt', 'r') as file:
        content = file.read()
        try:
            jContent = json.loads(content)
            #print(jContent)
        except Exception as e:
            jContent = {

            }
        file.close()
    arr = names.split(',')
    for name in arr:
        jContent[name] = 0 
    print(jContent)
    with open('score.txt', 'w') as file:
        file.write(json.dumps(jContent))
        file.close()

@client.command()
async def won(ctx,*,user):
    try: 
        with open('score.txt', 'r') as file:
            content = file.read()
            jContent = json.loads(content)
            print(jContent)
            file.close()
        jContent[user] += 1
        with open('score.txt', 'w') as file:
            file.write(json.dumps(jContent))
            file.close()
        await ctx.send(f"""Congrats {user}! Use >score to see master list""")
    except Exception as e:
        print(e)
        await ctx.send("You gave an invalid player name. Please check >score to see what players are registered")
        await ctx.send("If you haven't been registered use >add [your_name]")

@client.command()
async def score(ctx):
    try:
        with open('score.txt', 'r') as file:
            content = file.read()
            jContent = json.loads(content)
            jContent = dict(sorted(jContent.items(), key=operator.itemgetter(1),reverse=True))
            print(jContent) 
            file.close()
        print("{:<10} {:<10}".format('Name','Imposter Wins'))
        await ctx.send("{:<10} {:<10}".format('Name','Imposter Wins'))
        for k, v in jContent.items():
            print ("{:<10} {:<10} ".format(k, v))
            await ctx.send("{:<10} {:10} ".format(k, v))
    except Exception as e:
        await ctx.send(e)


@client.event
async def on_member_join(member):
    for channel in member.server.channels:
        if str(channel) == 'general':
            await channel.send_message(f"""Welcome to our Among US server {member.mention}!""")
            await channel.send_message(rules) 


@client.event
async def on_message(message):
    id_serv = client.get_guild(760654051443867658)
    channels = ['general', 'scoreboard', 'admin'] 
    if str(message.channel) in channels:
        if message.content.find("ready") != -1:
            pass
        elif message.content == ">users":
            await message.channel.send(f"""# of members: {id_serv.member_count}""")
        elif message.content == ">reset" and str(message.channel) == 'admin':
            open('score.txt', 'w').close()
            await message.channel.send('scoreboard was reset')
    await client.process_commands(message)



called_once_a_day.start()

client.run("NzYwNzUwNjIwMTAwOTE5MzE2.X3QmOQ.z5ND16JAvCiw_94BpG5VyhpOxw0")