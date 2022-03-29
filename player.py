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
    def __init__(self, args):
        self.verbose = args.v
        self.buy_in = args.buyin
        self.money = self.buy_in
        self.max = self.money
        self.min = self.money
        self.cashout = args.out

        self.broke = False

        self.passline = 10
        self.dontpassline = 0
        self.dontcome = 50
        self.place = 15
        self.lay = 5
        self.come = 15
        self.field = 0

        self.lay_numbers = []
        self.place_numbers = [4, 5, 6, 8, 9, 10]

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

    def get_peak(self):
        return self.max

    def get_low(self):
        return self.min

    def get_money(self):
        return self.money

    def get_buy_in(self):
        return self.buy_in

    def get_cashout(self):
        return self.cashout

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
        if self.money < self.min:
            self.min = self.money

    def pay(self, value, msg):
        self.money -= value
        if value > 0 and self.verbose:
            self.broadcast(value, msg, loss=True)
        return value

    def gain(self, value, msg):
        self.money += value
        if value > 0 and self.verbose:
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
        if self.cash_exists(amt):
            return self.pay(amt, 'pass odds')
        else:
            return 0
    
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
        if self.cash_exists(amt):
            return self.pay(amt, 'don\'t pass odds')
        else:
            return 0

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
    
    def bet_come_odds(self, table, cb):
        self_cap = self.caps[cb.get_key()]
        amt = cb.get_bet()*self_cap
        table_max = cb.get_bet()*cb.get_cap()
        if amt > table_max:
            amt = table_max
        if self.cash_exists(amt):
            return self.pay(amt, 'come odds')
        else:
            return 0

    def confirm_come_odds(self, table, cb):
        if cb.has_bet() and not cb.has_odds():
            return True
        else:
            return False

    def bet_dontcome(self, table):
        return self.pay(self.dontcome, 'don\'t come')
    def confirm_dontcomebet(self, table):
        return not self.dc_exists(table) and self.cash_exists(self.dontcome)
    def confirm_dontcome_odds(self, table, dc):
        if dc.has_bet() and not dc.has_odds():
            return True
        else:
            return False

    def bet_dontcome_odds(self, table, dc):
        self_cap = self.caps[dc.get_key()]
        amt = dc.get_bet()*self_cap
        table_max = dc.get_bet()*dc.get_cap()
        if amt > table_max:
            amt = table_max
        if self.cash_exists(amt):
            return self.pay(amt, 'don\'t come odds')
        else:
            return 0

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

        for cb in table.comebets:
            if cb.roll == pb.roll:
                if cb.has_bet():
                    playing = False

        for dc in table.dontcomebets:
            if dc.roll == pb.roll:
                if dc.has_bet():
                    playing = False
        
        return playing

    def dc_exists(self, table):
        for dc in table.dontcomebets:
            if dc.bet > 0:
                return True
        return False
