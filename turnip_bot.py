import discord
import pickle
import re
import asyncio
import datetime

import local_settings as ls

turnip_data = {}
# structure {server:{channel:[{islands}], channel:[{islands}]}, server:{channel: {[{islands}]}}}
island_questions = ["What is your invite code?", "What is your turnip price?",
                    "Do you have a turnip price forecast?\nhttps://artem6.github.io/acnh_turnips/", "Do you have a short note for visitors? (50 chars)", "In how many hours do you want this invite to expire?\n(Use digits)"]

message_log = {}


class Island:
    def __init__(self, username, island_name, code, turnip_price, forecast, note, expire_time):
        self.username = username
        self.island_name = island_name
        self.code = code
        self.turnip_price = turnip_price
        self.forecast = forecast
        self.note = note
        self.expire_time = datetime.datetime.now(
        ) + datetime.timedelta(hours=float(expire_time))
        self.expire_time = datetime.datetime.now() + datetime.timedelta(hours=float(expire_time))

    def get_island(self):
        response = "{} - {} - {} - {} - {} - {}".format(
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
            return data
    except FileNotFoundError:
        with open('turnip_file', 'wb') as f:
            pickle.dump(data, f)
        print("New data file created")
        return data


def generate_list(server, channel, data):
    """Creates a response to return to a Discord server and channel of the listed island to visit, if any.
    Will also generate list to edit when updated when island invites expire."""
    response = "-" * 61 + "\n"
    response = response + "Username - Island - Invite code - Turnip price - Forecast - Note\n"
    try:
        this_list = data[server][channel]
        if len(this_list) == 0:
            response = response + "There are no islands listed on this server for this channel\n"
            response = response + \
                "{}www.patreon.com/spaceturtletools{}".format(
                    "-" * 10, "-" * 10)
            return response
    except KeyError:
        response = "There are no islands listed on this server for this channel\n"
        return response
    for island in this_list:
        response = response + "{}\n".format(island.get_island())
    response = response + \
        "{}www.patreon.com/spaceturtletools{}".format("-" * 10, "-" * 10)
    return response


def add_island(server, channel, island, data):
    """Adds an island to the data under the server and channel name"""
    if server in data.keys():
        print()
        if channel in data[server].keys():
            data[server][channel].append(island)
            save_data(data)
        else:
            data[server][channel] = [island]
            save_data(data)
    else:
        data[server] = {channel: [island]}
        save_data(data)


turnip_data = load_data(turnip_data)

# test_island = Island('Blubber', '2342S', 75, 'Falling', 'WHERESDABEEF')

# add_island(5555, 12121, test_island)
# print(turnip_data)

client = discord.Client()


async def remove_expired_island(message_log, data):
    await client.wait_until_ready()
    while not client.is_closed():
        for server in data.keys():
            for channel in data[server].keys():
                for item in data[server][channel]:
                    if item.expire_time < datetime.datetime.now():
                        data[server][channel].remove(item)
                        await update_messages(server, channel, message_log, data) 
        print(data)
        await asyncio.sleep(600)


async def update_messages(server_id, channel_id, message_log, data, server=None, channel=None):
    if channel == None:
        try:
            channel = message_log[server_id][channel_id].channel 
        except KeyError:
            if len(message_log) == 0:
                return
        
    try:        
        await message_log[server_id][channel_id].delete()
        message_log[server_id] = {channel_id: await channel.send(generate_list(server_id, channel_id, data))}
        try:
            await message_log[server_id][channel_id].pin()
        except:
            pass
    except (KeyError, AttributeError):
        # message_log[server][channel] = await client.server.channel.send(generate_list(server, channel, data))
        print('Message does not exist, making new one')
        message_log[server_id] = {channel_id: await channel.send(generate_list(server_id, channel_id, data))}
        try:
            await message_log[server_id][channel_id].pin()
        except:
            pass
    except (discord.HTTPException, discord.NotFound):
        print('Message deleted, making new')
        message_log[server_id] = {channel_id: await channel.send(generate_list(server_id, channel_id, data))}
        try:
            await message_log[server_id][channel_id].pin()
        except:
            pass


@client.event
async def on_ready():
    print('The bot has logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("&island to create invite"))


@client.event
async def on_message(message):
    # print(message)
    if message.type == discord.MessageType.pins_add and message.author == client.user:
        await message.delete()

    temp_msgs = []

    async def delete_temp_messages():
        for message in temp_msgs:
            await message.delete(delay=10)

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
                temp_msgs.append(message)
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
            try:
                number_check = float(island_info[6])
            except ValueError:
                timeout_msg = await channel.send("Please enter digits for your timeout.")
                await delete_temp_messages()
                return
            for info in island_info:
                if info == island_info[0]: #skip truncating ID
                    continue
                if info == island_info[5]: #Allow note to be longer
                    info = info[0:49]
                    continue
                info = info[0:14]
            new_island = Island(*island_info)
            temp_msgs.append(message)
            await delete_temp_messages()
            add_island(message.guild.id, channel.id, new_island, turnip_data)
            # await channel.send(await update_messages(message.guild.id, channel.id, message_log, turnip_data))
            await update_messages(message.guild.id, channel.id, message_log, turnip_data, message.guild, channel)


client.loop.create_task(remove_expired_island(message_log, turnip_data))
client.run(ls.token)
