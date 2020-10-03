import json
import operator
import pandas as pd
from pandas import json_normalize
import discord 
from discord.ext import commands, tasks

client = commands.Bot(command_prefix='>') #functions will be triggered with this prefix in chat

#channel ID's 
general = 760654051443867660
admin = 760790658801205278
daScore = 760654051443867661
lobby = 760654051443867663


def readJSON(f): 
    #reads content of a .txt file and converts to JSON and returns content. All table data is stored in jSON
    with open(f, 'r') as file:
        content = file.read()
        jContent = json.loads(content)
    file.close()
    return jContent

def writeJSON(f, info):
    #writes json to .txt file
    with open(f, 'w') as file:
        file.write(json.dumps(info))
        file.close()
#.JSON NEST JSON IN JSON

@client.event
async def on_ready():
    print("Bot is ready")

@tasks.loop(hours=168) #every week this triggers
async def weekly():
    jContent = readJSON('tst.txt')
    for user in jContent:
        jContent[user][0] = 0 #resets weekly scores to 0
    writeJSON('tst.txt', jContent)

    message_channel = client.get_channel(daScore)
    print(f"Got channel {message_channel}")

    await message_channel.send("Weekly kills reseted.") 

@weekly.before_loop
async def beforeWeek():
    await client.wait_until_ready()
    print("Finished waiting")

@tasks.loop(hours=40)
async def called_once_a_day(): #actually once every two days or so
    message_channel = client.get_channel(daScore)
    print(f"Got channel {message_channel}")
    try:
        jContent = readJSON('tst.txt') 
    except:
        jContent = { 

        } 

    big = 0
    leaders = []
    print(jContent.items())
    for (k,v) in jContent.items(): #finds user with the most wins in scoreboard
        if v[1] == big:
            leaders.append(k)
        elif v[1] > big:
            big = v[1]
            leaders.clear()
            leaders.append(k)
        if v[1] >= 10:
            pass
    if leaders != []:
        await message_channel.send(f"{leaders} got the most Alltime winss with {big} wins")
        await message_channel.send("If you're ever not sure of the commands use >rules")
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
async def ad(ctx):
    try:
        jContent = readJSON('tst.txt')
    except:
        jContent = {

        }
    player = ctx.message.author.name
    if jContent[player]:
        await ctx.send("You are already registered!")
    else:
        jContent[player] = [0, 0]
        writeJSON('tst.txt', jContent)
    print(jContent)
    

@client.command()
async def win(ctx, *, num='1'):
    jContent = readJSON('tst.txt')
    try:
        user = ctx.message.author.name
        jContent[user][0] += int(num)
        jContent[user][1] += int(num)
        writeJSON('tst.txt', jContent)
        await ctx.send(f"Nice work {user}!")
    except Exception as e:
        print(e)
        await ctx.send("You gave an invalid number or you are not registered. Please check >board to see what players are registered")
        await ctx.send("If you haven't been registered use >add")   


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name= "general")
    await channel.send_message(f"""Welcome to our Among US server {member.mention}!""")
    with open('rules.txt', 'r') as f:
        await channel.send_message(f.read())


@client.event
async def on_message(message):
    id_serv = client.get_guild(760654051443867658)
    channels = ['general', 'scoreboard', 'admin'] 
    if str(message.channel) in channels:
        if message.content.find("ready") != -1:
            pass
        elif message.content == ">users":
            await message.channel.send(f"""# of members: {id_serv.member_count}""")
            await message.channel.send(message.channel)
        elif message.content == ">reset" and str(message.channel) == 'admin':
            open('tst.txt', 'w').close()
            await message.channel.send('scoreboard was reset')
        elif message.content.startswith(">lila"):
            msg = message.content[6:]
            print(msg)
            if str(message.channel) == 'admin':
                channel = client.get_channel(general)
                await channel.send(msg)
        elif message.content.startswith(">role"):
            role_list = ["Killer", "Slick", "Anansi the Spider"]
            role_entered= message.content[6:]
            role = discord.utils.get(message.guild.roles, name=role_entered)
            #print("roles:", message.guild.roles)
            wins = {role_list[0]: 10, role_list[1]: 20, role_list[2]: 50}
            if role is None or role.name not in role_list:
                # If the role wasn't found by discord.utils.get() or is a role that we don't want to add:
                #print(role_entered)
                await message.channel.send( "Role doesn't exist. Valid roles are `Killer`, `Slick`, and `Anansi the Spider`.")
                return
            elif role in message.author.roles:
                # If they already have the role
                await message.channel.send( "You already have this role.")
            else:
                try: 
                    jContent = readJSON('tst.txt')
                    if jContent[message.author.name][1] >= wins[role_entered]:
                        try:
                            await message.author.add_roles(role)
                            await message.channel.send(f"Congratulations! You now have the role: {role.name}")
                        except discord.Forbidden:
                            await message.channel.send( "I cannot give out roles. Either my role is lower in the heirachy or I don't have admin privileges")
                    else:
                        await message.channel.send(f"You need atleast {wins[role_entered]} wins to be rewarded this role!")
                except:
                    await message.channel.send('The leaderbord file is either empty or not .jSON formatted')
        elif message.content == ">board":
            embed = discord.Embed(title = 'Among Us Leaderboard',
            description = 'This leaderboard is a record of Imposter wins.',
            colour = discord.Colour.blue()
            )

            embed.set_footer(text = '>ad to register to leaderboard')

            jContent = readJSON('tst.txt')
            sort = dict(sorted(jContent.items(), key=lambda x: x[1][1], reverse=True))
            #sort = dict(sorted(jContent.items(), key=lambda x: x[1][0], reverse=True))
            print(sort)
            for user in sort:
                embed.add_field(name=f'**{user}**', value=f'> Wins this week: {sort[user][0]}\n> Alltime Wins: {sort[user][1]}\n',inline=False)

            embed.set_image(url = 'https://zipfm.net/wp-content/uploads/2019/07/p0631vc4.jpg')
            embed.set_thumbnail(url = 'https://gamespot1.cbsistatic.com/uploads/screen_kubrick/1581/15811374/3740702-amongusthumb.jpg')
            embed.set_author(name='Lila Iké', 
            icon_url = 'https://i.redd.it/t48povvc80941.jpg')

            await message.channel.send(content = "None", embed=embed)
        elif message.content == ">board info":
            embed = discord.Embed(title = 'Roles',
            description = '`Lame`, `Active` and `Addicted` are not included as they are roles rewarded by how active you are in the discord voice lobby when playing',
            colour = discord.Colour.red()
            )

            embed.set_footer(text = 'use >role [role_here] to request for a role')

            jContent = {'Killer': 10, 'Slick': 20, 'Anansi The Spider': 50}
            for user in jContent:
                embed.add_field(name=f'**{user}**', value=f'> Wins needed: {jContent[user]}', inline=False)

            embed.set_image(url = 'https://caribbeanposh.com/wp-content/uploads/2019/08/Lila-3.jpg')
            embed.set_thumbnail(url = 'https://imgix.bustle.com/uploads/image/2020/9/10/6a993162-9b54-498a-879f-d1d6f13ad68e-topbanner_cominnerslothspacemafia.jpg')
            embed.set_author(name='Lila Iké', 
            icon_url = 'https://i.redd.it/t48povvc80941.jpg')

            await message.channel.send(content = None, embed=embed)

    await client.process_commands(message)



called_once_a_day.start()
weekly.start()

client.run("NzYwNzUwNjIwMTAwOTE5MzE2.X3QmOQ.z5ND16JAvCiw_94BpG5VyhpOxw0")#bot token goes here. never reveal to anyone. dont worry mine has changed
