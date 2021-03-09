import discord, json, asyncio, pymongo, random
from pymongo import MongoClient
from datetime import datetime

with open('config.json') as f:
    data = json.load(f)
    Token = data['DiscordToken']
    MongodbCredentials = data['MongodbCredentials']

client = discord.Client()
prefix = '%'
cluster = MongoClient(MongodbCredentials)
db = cluster["Suggestions"]
collection = db["Input"]
improvements = db["Bot_Suggestions"]
now = datetime.now()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game('Your Suggestions'))

@client.event
async def on_message(message):
    if message.content.startswith(prefix + "Suggestion"):
        await message.channel.send('Please type your coding suggestion')
        await asyncio.sleep(0.5)
        try:
            Suggestion = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        MessageID = random.randint(1, 10000000000)
        current_time = now.strftime("%H|%M|%S")
        IdMesid = str(MessageID)
        InputId = message.author.name + "-" + IdMesid
        await message.channel.send('The suggestion you are providing is\n' + '```' + Suggestion.content + '```' + "\n Your User Message ID is " + InputId)
        collection.insert_one({"_id" : InputId , "Suggestion": Suggestion.content, "Message": "Discord", "DiscordUserID": message.author.id, "Username": message.author.name, "MessageID": MessageID})

    if message.content.startswith(prefix + "GhostSuggestion"):
        await message.channel.send('Please type your coding suggestion')
        await asyncio.sleep(0.5)
        try:
            Suggestion = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        MessageID = random.randint(1, 10000000000)
        current_time = now.strftime("%H|%M|%S")
        IdMesid = str(MessageID)
        InputId = message.author.name + "-" + IdMesid
        await message.channel.send('The suggestion you are providing is\n' + '```' + Suggestion.content + '```' + "\n Your User Message ID is " + InputId)
        collection.insert_one({"_id" : InputId, "Suggestion": Suggestion.content, "Message": "Discord", "DiscordUserID": message.author.id, "Username": "Anonymous User", "MessageID": MessageID})

    if message.content.startswith(prefix + "DeleteEntry"):
        await message.channel.send("Please send the ID of the message you would like to delete")
        try:
            DeleteID = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        VerifyDelete = collection.find({"_id": DeleteID.content})

        for result in VerifyDelete:
            await message.channel.send("Are you sure you want to delete your suggestion:\n" + "```" + result["Suggestion"] + '```' + "Y/N")
        try:
            Answer = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        if Answer.content == "Y":
            collection.delete_one({"_id": DeleteID.content})
            await message.channel.send("Suggestion has been sucessfully deleted")
        if Answer.content == "N":
            await message.channel.send("Ok, request has been resolved")

    if message.content.startswith(prefix + "BotSuggestion"):
        await message.channel.send('Please type your suggestion for this bot')
        await asyncio.sleep(0.5)
        try:
            BotS = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        await message.channel.send("Are you sure you want to send your suggestion:\n" + "```" + BotS.content + '```' + "Y/N")
        try:
            Answer = await client.wait_for("message", timeout=30)
        except asyncio.Timeout:
            await message.channel.send('Timeout')
        if Answer.content == "Y":
            MessageID = random.randint(1, 10000000000)
            IdMesid = str(MessageID)
            InputId = message.author.name + "-" + IdMesid
            improvements.insert_one({"_id" : InputId, "DiscordUserID" : message.author.id, "BotSuggestion" : BotS.content})
            await message.channel.send("Suggestion has been sucessfully sent")
        if Answer.content == "N":
            await message.channel.send("Ok, request has been resolved")

        
    if message.content.startswith(prefix + "RandomSuggestion"):
        results = collection.find({"Message": "Discord"})
        count = collection.count_documents({"Message": "Discord"})
        count -= 1
        ranint = random.randint(0, count)
        AllSug = []
        AllUsers = []
        AllMessageID = []
        for result in results:
            Sug = result["Suggestion"]
            Name = result["Username"]
            MesID = result["MessageID"]
            AllSug.append(Sug)
            AllUsers.append(Name)
            AllMessageID.append(MesID)
        MessageIDstr = str(AllMessageID[ranint])
        AllSug0 = AllSug[ranint]
        embedSuggestionRan = discord.Embed(title= AllSug0, description= "This Idea was shared by the user: " + AllUsers[ranint])
        embedSuggestionRan.add_field(name="Report this", value="If this suggestion is at all offensive or insinuates violence, please DM the server admin and send them this MessageID: " + MessageIDstr)
        await message.channel.send(embed=embedSuggestionRan)

    if message.content.startswith(prefix + "Help"):
        helpembed = discord.Embed(title= "Help Menu", description= "This is the help menu for the Code Suggestion bot\n \nPrivacy Disclamer: Whenever this bot is sent a suggestion, it logs the user ID and the username of the author. This is because the bot is located on many servers and this is to insure all messages are free of profanity.")
        helpembed.add_field(name="%Suggestion", value="This command will send a suggestion to the bots database. After this, any user can access this by asking the bot for a suggestion.")
        helpembed.add_field(name="%" + "GhostSuggestion", value="This command will send a suggestion to the bots database. After this, any user can access this by asking the bot for a suggestion.")
        helpembed.add_field(name="%DeleteEntry", value="This command will delete an entry that you have sent, all that is required is the User Message ID.")
        helpembed.add_field(name="%RandomSuggestion", value="This command will allow you to get sent a random suggestion in this bots database.")
        helpembed.add_field(name="%BotSuggestion", value="This command will allow you to send a suggestion to the dev (Sam) that may be added in the future")
        await message.channel.send(embed=helpembed)
client.run(Token)

