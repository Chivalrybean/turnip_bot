import discord
import pickle
import re
import asyncio

import local_settings as ls

turnip_data = {}
# structure {server:{channel:[{islands}], channel:[{islands}]}, server:{channel: {[{islands}]}}}
island_questions = ["What is your invite code?", "What is your turnip price?",
"Is your price forcast rising or falling?", "Do you have a short note for visitors?"]

class Island:
    def __init__(self, username, island_name, code, turnip_price, forecast, note):
        self.username = username
        self.island_name = island_name
        self.code = code
        self.turnip_price = turnip_price
        self.forecast = forecast
        self.note = note

    def get_island(self):
        response = "{} {} {} {} {} {}".format(
            self.username, self.island_name, self.code, self.turnip_price, self.forecast, self.note)
        return response

    def __repr__(self):
        return self.get_island()


def save_data():
    global turnip_data
    """Saves turnip_data to pickle file"""
    with open('turnip_file', 'wb') as f:
        pickle.dump(turnip_data, f)


def load_data():
    global turnip_data
    """Loads pickle file data to turnip_data, unless no file present, then it creates a new file and puts current data into it."""
    try:
        with open('turnip_file', 'rb') as f:
            turnip_data = pickle.load(f)
    except FileNotFoundError:
        with open('turnip_file', 'wb') as f:
            pickle.dump(turnip_data, f)
        print("New data file created")


def generate_list(server, channel):
    global turnip_data
    """Creates a response to return to a Discord server and channel of the listed island to visit, if any.
    Will also generate list to edit when updated when island invites expire."""
    response = "-" * 40 + "\n"
    try:
        this_list = turnip_data[server][channel]
    except KeyError:
        response = "There are no inslands listed on this server for this channel"
        return response
    for island in this_list:
        response = response + "{}\n".format(island.get_island())
    response = response + "-----www.patreon.com/spaceturtletools---"


def add_island(server, channel, island):
    """Adds an island to the data under the server and channel name"""
    global turnip_data
    if channel in turnip_data.keys():
        if server in turnip_data[server].keys():
            turnip_data[server][channel].append(island)
            save_data()
        else:
            turnip_data[server][channel] = [island]
            save_data()
    else:
        turnip_data[server] = {channel: [island]}
        save_data()


# load_data()

# test_island = Island('Blubber', '2342S', 75, 'Falling', 'WHERESDABEEF')

# add_island(5555, 12121, test_island)
# print(turnip_data)

client = discord.Client()


@client.event
async def on_ready():
    print('The bot has logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    temp_msgs = []

    async def delete_temp_messages():
        for message in temp_msgs:
            await message.delete(delay=60)

    if message.author == client.user:
        return
    elif message.content.startswith("&island"):
        channel = message.channel
        user = message.author
        tmp_msg = await channel.send("What is your Island name?")
        temp_msgs.append(tmp_msg) 

        def check(msg):
            print(msg.channel == channel and msg.author == user)
            if msg.channel == channel and msg.author == user:
                temp_msgs.append(msg)
            return msg.channel == channel and msg.author == user

        island_info = [user.name] 
        for question in island_questions:
            try:
                msg = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                timeout_msg = await channel.send("Island listing timed out")
                temp_msgs.append(timeout_msg)
                await delete_temp_messages()
                return
            else:
                island_info.append(msg.content)
                print(island_info)
                tmp_msg = await channel.send(question)
                temp_msgs.append(tmp_msg)

        try:
            msg = await client.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
                timeout_msg = await channel.send("Island listing timed out")
                temp_msgs.append(timeout_msg)
                await delete_temp_messages()
                return
        else:
            island_info.append(msg.content)
            print(island_info)
            new_island = Island(*island_info)
            temp_msgs.append(message)
            await delete_temp_messages()
            add_island(message.guild, channel, new_island)
            await channel.send(generate_list())

        
        
        # try:
        #     msg = await client.wait_for('message', timeout=60.0, check=check)
        # except asyncio.TimeoutError:
        #     timeout_msg = await channel.send("Island listing timed out")
        #     temp_msg.append(timeout_msg)
        #     await delete_temp_messages()
        # else:
        #     island_code = msg.content
        #     print(island_code)
        #     turnip_msg = await channel.send("What is your turnip price?")

client.run(ls.token)