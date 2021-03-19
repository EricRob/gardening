#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os
import pdb
from termcolor import cprint

# Global variables

# Class declarations
class Player(object):
    """docstring for PlayerConfig"""
    def __init__(self):
        self.money = 500 # This is the buy-in
        self.max = self.money
        self.cashout = 1000

        self.broke = False

        self.passline = 10
        self.dontpassline = 0
        self.dontcome = 100
        self.place = 5
        self.lay = 5
        self.come = 10
        self.field = 5

        self.lay_numbers = [4, 5, 6, 8, 9, 10]
        self.place_numbers = [4, 5, 6 ,8, 9, 10]

        self.caps = {
            "four_comebet": 3,
            "five_comebet": 4,
            "six_comebet": 5,
            "eight_comebet": 5,
            "nine_comebet": 4,
            "ten_comebet": 3,
            "four_dontcomebet": 3,
            "five_dontcomebet": 4,
            "six_dontcomebet": 5,
            "eight_dontcomebet": 5,
            "nine_dontcomebet": 4,
            "ten_dontcomebet": 3
        }

    def still_playing(self):
        self.review()
        playing = True
        if self.money < self.dontcome:
            playing = False
            self.broke = True
        if self.money >= self.cashout:
            playing = False 
        return playing

    def cash_exists(self, amt):
        if amt <= self.money:
            return True
        else:
            return False

    def review(self):
        if self.money > self.max:
            self.max = self.money

    def pay(self, value, msg):
        self.money -= value
        if value > 0:
            self.broadcast(value, msg, loss=True)
        return value

    def gain(self, value, msg):
        self.money += value
        if value > 0:
            self.broadcast(value, msg, win=True)
        return value

    def broadcast(self, amt, bet_type, win=False, loss=False, bet=True):
        if win:
            color = 'green'
        elif loss:
            color = 'red'
        elif bet:
            color = 'yellow'

        line = '--> {} bet:'.format(bet_type).ljust(15)
        line += '${}'.format(amt)
        cprint(line, color)

    def bet_pass(self, table):
        return self.pay(self.passline, 'pass')
    
    def bet_pass_odds(self, table):
        cap = self.caps[table.passline.get_key()]
        amt = table.passline.get_bet()*cap
        table_max = table.passline.get_bet()*table.passline.get_cap()
        if amt > table_max:
            amt = table_max
        return self.pay(amt, 'pass odds')
    
    def confirm_pass_odds(self, table):
        if table.passline.has_bet() and not table.passline.has_odds():
            return True
        else:
            return False

    def bet_dontpass(self, table):
        return self.pay(self.dontpassline, 'don\'t pass')
    def bet_dontpass_odds(self, table):
        cap = self.caps[table.dontpassline.get_key()]
        amt = table.dontpassline.get_bet()*cap
        table_max = table.dontpassline.get_bet()*table.dontpassline.get_cap()
        if amt > table_max:
            amt = table_max
        return self.pay(amt, 'don\'t pass odds')
    def confirm_dontpass_odds(self, table):
        if table.dontpassline.has_bet() and not table.dontpassline.has_odds():
            return True
        else:
            return False


    def bet_field(self, table):
        return self.pay(self.field, 'field')
    def confirm_fieldbet(self, table):
        if self.field > 0 and self.cash_exists(self.field):
            return True
        else:
            return False

    def bet_come(self, table):
        return self.pay(self.come, 'come')
    def confirm_comebet(self, table):
        confirm = self.dc_exists(table) and self.cash_exists(self.come)
        if confirm:
            if table.come_stage > 0:
                confirm = False
        return confirm

    def bet_dontcome(self, table):
        return self.pay(self.dontcome, 'don\'t come')
    def confirm_dontcomebet(self, table):
        return not self.dc_exists(table) and self.cash_exists(self.dontcome)

    def bet_lay(self, table, lb):
        return self.pay(self.lay, 'lay')
    def confirm_laybet(self, table, lb):
        if table.point == 0:
            playing = False
        else:
            playing = (lb.roll in self.lay_numbers) and self.cash_exists(self.lay)
        
        return playing

    def bet_place(self, table, pb):
        return self.pay(self.place, 'place')
    def confirm_placebet(self, table, pb):
        if table.point == 0:
            playing = False
        else:
            playing = (pb.roll in self.place_numbers) and self.cash_exists(self.place)
        
        return playing

    def dc_exists(self, table):
        for dc in table.dontcomebets:
            if dc.bet > 0:
                return True
        return False
