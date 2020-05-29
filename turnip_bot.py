import discord
import pickle
import re
import asyncio
import datetime

import local_settings as ls

turnip_data = {}
# structure {server:{channel:[{islands}], channel:[{islands}]}, server:{channel: {[{islands}]}}}
island_questions = ["What is your invite code?", "What is your turnip price?",
                    "Is your price forcast rising or falling?", "Do you have a short note for visitors?", "In how many hours do you want this invite to expire?\n(Use digits)"]


class Island:
    def __init__(self, username, island_name, code, turnip_price, forecast, note, expire_time):
        self.username = username
        self.island_name = island_name
        self.code = code
        self.turnip_price = turnip_price
        self.forecast = forecast
        self.note = note
        self.expire_time = datetime.datetime.now() + datetime.timedelta(hours=int(expire_time))

    def get_island(self):
        response = "{} {} {} {} {} {}".format(
            self.username, self.island_name, self.code, self.turnip_price, self.forecast, self.note)
        return response

    def __repr__(self):
        return self.get_island()


def save_data(data):
    """Saves turnip_data to pickle file"""
    with open('turnip_file', 'wb') as f:
        pickle.dump(data, f)


def load_data(data):
    """Loads pickle file data to turnip_data, unless no file present, then it creates a new file and puts current data into it."""
    try:
        with open('turnip_file', 'rb') as f:
            print('Loading data')
            data = pickle.load(f)
            # print(pickle.load(f))
    except FileNotFoundError:
        with open('turnip_file', 'wb') as f:
            pickle.dump(data, f)
        print("New data file created")


def generate_list(server, channel, data):
    """Creates a response to return to a Discord server and channel of the listed island to visit, if any.
    Will also generate list to edit when updated when island invites expire."""
    response = "-" * 40 + "\n"
    try:
        this_list = data[server][channel]
    except KeyError:
        response = "There are no islands listed on this server for this channel"
        return response
    for island in this_list:
        response = response + "{}\n".format(island.get_island())
    response = response + "-----www.patreon.com/spaceturtletools---"
    return response


def add_island(server, channel, island, data):
    """Adds an island to the data under the server and channel name"""
    if server in data.keys():
        print()
        if channel in data[server].keys():
            data[server][channel].append(island)
            # save_data(data)
        else:
            data[server][channel] = [island]
            # save_data(data)
    else:
        data[server] = {channel: [island]}
        # save_data(data)


# load_data(turnip_data)

# test_island = Island('Blubber', '2342S', 75, 'Falling', 'WHERESDABEEF')

# add_island(5555, 12121, test_island)
# print(turnip_data)

client = discord.Client()


async def remove_expired_island(data):
    await client.wait_until_ready()
    while not client.is_closed():
        for server in data.keys():
            for channel in data[server].keys():
                for item in data[server][channel]:
                    for island in item:
                        if island.expire_time < datetime.datetime.now():
                            item.remove(island)
        print(data)
        await asyncio.sleep(600)


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
            add_island(message.guild.id, channel.id, new_island, turnip_data)
            await channel.send(generate_list(message.guild.id, channel.id, turnip_data))

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

client.loop.create_task(remove_expired_island(turnip_data))
client.run(ls.token)
