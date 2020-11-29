#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os
import random
import pdb
from player import Player

# Global variables

# Class declarations
# class Player(object):
#   """docstring for PlayerConfig"""
#   def __init__(self):
#       self.ante = 10
#       self.money = 500 # This is the buy-in
#       self.dontcome = 200
#       self.place = 10
#       self.lay = 10
#       self.come = 10
#       self.field = 0

#   def ante(self):
#       self.money -= self.ante
#       return self.ante

#   def gain(self, value):
#       self.money += value

class TableConfig(object):
    """docstring for TableConfig"""
    def __init__(self):
        self.payouts = {
            "four_placebet": 9/5,
            "five_placebet": 7/5,
            "six_placebet": 7/6,
            "eight_placebet": 7/6,
            "nine_placebet": 7/5,
            "ten_placebet": 9/5,
            "four_laybet": 2/5,
            "five_laybet": 4/7,
            "six_laybet": 4/5,
            "eight_laybet": 4/5,
            "nine_laybet": 4/7,
            "ten_laybet": 2/5,
            "four_comebet": 2/1,
            "five_comebet": 3/2,
            "six_comebet": 6/5,
            "eight_comebet": 6/5,
            "nine_comebet": 3/2,
            "ten_comebet": 2/1,
        }
        self.caps = {
            "four_comebet": 3,
            "five_comebet": 4,
            "six_comebet": 5,
            "eight_comebet": 5,
            "nine_comebet": 4,
            "ten_comebet": 3
        }
        self.comeouts = [4, 5, 6, 8, 9, 10]
        self.naturals = [7, 11]
        self.craps = [2, 3, 12]

class CrapsTable(object):
    """docstring for CrapsTable"""
    def __init__(self, config):
        self.table = config
        self.placebets = []
        self.laybets = []
        self.comebets = []
        self.dontcomebets = []
        self.fieldbet = FieldBet()
        self.passline = None
        self.point = 0

        self.come_stage = 0
        self.dontcome_stage = 0

        self.build_table()

    def build_table(self):
        self.build_placebets()
        self.build_laybets()
        self.build_comebets()
        self.build_dontcomebets()
        return

    def build_placebets(self):
        self.placebet_builder = [
            (4, "four_placebet"),
            (5, "five_placebet"),
            (6, "six_placebet"),
            (8, "eight_placebet"),
            (9, "nine_placebet"),
            (10, "ten_placebet")]
        for item in self.placebet_builder:
            self.placebets.append(PlaceBet(item[0], item[1], self.table.payouts[item[1]]))

    def build_laybets(self):
        self.laybet_builder = [
            (4, "four_laybet"),
            (5, "five_laybet"),
            (6, "six_laybet"),
            (8, "eight_laybet"),
            (9, "nine_laybet"),
            (10, "ten_laybet")]
        for item in self.laybet_builder:
            self.laybets.append(LayBet(item[0], item[1], self.table.payouts[item[1]]))

    def build_comebets(self):
        self.comebet_builder = [
            (4, "four_comebet"),
            (5, "five_comebet"),
            (6, "six_comebet"),
            (8, "eight_comebet"),
            (9, "nine_comebet"),
            (10, "ten_comebet")]
        for item in self.comebet_builder:
            self.comebets.append(ComeBet(item[0], item[1], self.table.payouts[item[1]], self.table.caps[item[1]]))

    def build_dontcomebets(self):
        self.dontcomebet_builder = [
            (4, "four_dontcomebet"),
            (5, "five_dontcomebet"),
            (6, "six_dontcomebet"),
            (8, "eight_dontcomebet"),
            (9, "nine_dontcomebet"),
            (10, "ten_dontcomebet")]
        for item in self.dontcomebet_builder:
            self.dontcomebets.append(DontComeBet(item[0], item[1]))

    def change_point(self, point):
        for comebet in self.comebets:
            if comebet.roll == point:
                comebet.point = True
            else:
                comebet.point = False

    def evaluate(self, player, dice):
        if self.point == 0:
            self.evaluate_comebets(player, dice)
            self.evaluate_dontcomebets(player, dice)
            self.evaluate_laybets(player, dice)
            self.evaluate_placebets(player, dice)

    def evaluate_comebets(self, player, dice):
        if self.point == 0:
            for comebet in self.comebets:
                if comebet.bet == 0:
                    continue
                elif comebet.roll == dice:
                    comebet.payout(player)

    def evaluate_dontcomebets(self, player, dice):
        for dontcomebet in self.dontcomebets:
            pass

    def evaluate_placebets(self, player, dice):
        if self.point == 0:
            for placebet in self.placebets:
                if placebet.bet == 0:
                    continue
                elif placebet.roll == dice:
                    placebet.payout(player)

    def evaluate_laybets(self, player, dice):
        if self.point == 0:
            for laybet in self.laybets:
                if laybet.bet == 0:
                    continue
                elif laybet.roll == dice:
                    laybet.reset()
        return

    def setup_table(self, player):
        self.passline = PassLine(player, self.comebet_builder, self.table.payouts)

    def seven(self, player):
        # paying: lays, don't comes, come stage, first pass
        for lay in self.laybets:
            lay.payout(player)
        for dc in self.dontcomebets:
            dc.payout(player)
        player.gain(self.come_stage*2)
        self.passline.payout(player)

        # Clear: field, comebets, stages, lines, lays, places
        self.field.reset()
        self.passline.reset()
        self.come_stage = 0
        self.dontcome_stage = 0
        for cb in self.comebets:
            cd.reset()
        for lb in self.laybets:
            lb.reset()
        pass

    def play_round(self, player):
        playing = True
        while(playing):
            self.make_bets(player)
            playing = self.roll(player)
        pdb.set_trace()

    def make_bets(self, player):
        # First division: Come Out and Point
        if self.point == 0:
            self.passline.bet = player.ante()
        return

    def roll(self, player):
        dice = random.randint(1, 6) + random.randint(1, 6)

        if self.point == 0: # Come Out
            if dice in self.table.craps:
                return False
            elif dice in self.table.naturals:
                self.passline.payout(player)
                if dice == 7:
                    self.seven(player)
                return False
            elif dice in self.table.comeouts:
                self.evaluate(player, dice)
                self.change_point(dice)
                return True
        else: # Point
            return False




class PlaceBet(object):
    """docstring for PlaceBet"""
    def __init__(self, roll, name,  payout):
        self.name = name
        self.payout = payout
        self.bet = 0
        self.roll = roll
        self.point = False
        self.off = 0

    def payout(self, player):
        player.gain(self.bet) # bet refund
        player.gain(self.bet*self.payout*self.off) # profit
        self.reset()

    def reset(self):
        self.bet = 0
        self.point = False
        self.off = 0

class LayBet(object):
    """docstring for LayBet"""
    def __init__(self, roll, name,  payout):
        self.name = name
        self.payout = payout
        self.bet = 0
        self.roll = roll
        self.point = False
        self.off = 0

    def payout(self, player):
        player.gain(self.bet) # refund
        player.gain(self.bet*self.payout*self.off) # profit
        self.reset()

    def reset(self):
        self.bet = 0
        self.off = 0

class ComeBet(object):
    """docstring for ComeBet"""
    def __init__(self, roll, name, payout, cap):
        self.name = name
        self.roll = roll
        self.cap = cap
        self.odds_payout = payout
        self.bet = 0
        self.odds = 0
        self.point = False
        self.off = 0
    
    def reset(self):
        self.bet = 0
        self.odds = 0
        self.point = False
        self.off = 0

    def payout(self, player):
        player.gain(self.bet*2) # 1:1 payout
        player.gain(self.odds) # odds refund
        player.gain(self.odds*self.odds_payout*self.off) # odds payout
        self.reset()
        
class DontComeBet(object):
    """docstring for DontComeBet"""
    def __init__(self, roll, name):
        self.name = name
        self.roll = roll
        self.bet = 0
    
class FieldBet(object):
    """docstring for FieldBet"""
    def __init__(self, bet):
        self.bet = 0

    def reset(self):
        self.bet = 0

class PassLine(object):
    """docstring for PassLine"""
    def __init__(self, player, odds_key, payouts):
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0
        self.odds_payout = 0
        self.odds_key = odds_key
        self.payouts = payouts

    def set_odds(self):
        for odds in self.odds_key:
            if odds[0] == self.point:
                self.odds_payout = self.payouts[odds[1]]


    def payout(self, player):
        player.gain(self.bet*2) # 1:1 payout
        player.gain(self.odds) # odds refund
        player.gain(self.odds*self.odds_payout) # odds payout (this doesn't turn off)

    def reset(self):
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0
        self.odds_payout = 0
        
        

# Function declarations

def main():
    # Player enters the game
    player = Player()

    # House builds table and establishes rules
    table_rules = TableConfig()
    table = CrapsTable(table_rules)

    # Player antes, begins playing
    table.setup_table(player)

    test_rounds = 10
    for i in range(test_rounds):
        table.play_round(player)


# Main body
if __name__ == '__main__':
    main()
