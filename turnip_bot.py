import discord
import json

turnip_data = {}
# structure {server:{channel:[{islands}], channel:[{islands}]}, server:{channel: {[{islands}]}}}

# TODO Convert to using pickle to save data


class Island:
    def __init__(self, name, code, turnip_price, forecast='unknown', note=''):
        self.name = name
        self.code = code
        self.turnip_price = turnip_price
        self.forecast = forecast
        self.note = note

    def get_island(self):
        response = "{} {} {} {} {}".format(
            self.name, self.code, self.turnip_price, self.forecast, self.note)
        return response

    def __repr__(self):
        return self.get_island()


def save_data():
    global turnip_data
    """Saves turnip_data to .json file"""
    with open('turnip_file.json', 'w') as f:
        json.dump(turnip_data, f)


def load_data():
    global turnip_data
    """Loads .json file data to turnip_data, unless no file present, then it creates a new file and puts current data into it."""
    try:
        with open('turnip_file.json', 'r') as f:
            turnip_data = json.load(f)
    except FileNotFoundError:
        with open('turnip_file.json', 'w') as f:
            json.dump(turnip_data, f)
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

# test_island = Island('Turnipceratops', '949DSY', 75, 'Rising', 'Eat mor chikn')

# add_island(1234, 3425, test_island)
# print(turnip_data)
