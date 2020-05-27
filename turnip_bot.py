import discord
import json

turnip_data = {}


class island:
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


def save_data():
    with open('turnip_file.json', 'w') as f:
        json.dump(turnip_data, f)


def load_data():
    try:
        with open('turnip_file.json', 'r') as f:
            turnip_data = json.load(f)
    except FileNotFoundError:
        with open('turnip_file.json', 'w') as f:
            json.dump(turnip_data, f)
        print("New data file created")
