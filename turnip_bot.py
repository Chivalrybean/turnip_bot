import discord


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
