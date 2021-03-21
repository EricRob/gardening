#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os
import random
import pdb
from termcolor import cprint
from player import Player
import time
import argparse
from math import floor

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
    def __init__(self, args):
        self.payouts = {
            #Place
            "four_placebet": 9/5,
            "five_placebet": 7/5,
            "six_placebet": 7/6,
            "eight_placebet": 7/6,
            "nine_placebet": 7/5,
            "ten_placebet": 9/5,
            #Lay
            "four_laybet": 1/2,
            "five_laybet": 2/3,
            "six_laybet": 5/6,
            "eight_laybet": 5/6,
            "nine_laybet": 2/3,
            "ten_laybet": 1/2,
            #Come
            "four_comebet": 2/1,
            "five_comebet": 3/2,
            "six_comebet": 6/5,
            "eight_comebet": 6/5,
            "nine_comebet": 3/2,
            "ten_comebet": 2/1,
            #Don't Come
            "four_dontcomebet": 2/1,
            "five_dontcomebet": 3/2,
            "six_dontcomebet": 6/5,
            "eight_dontcomebet": 6/5,
            "nine_dontcomebet": 3/2,
            "ten_dontcomebet": 2/1,
        }
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
        self.comeouts = [4, 5, 6, 8, 9, 10]
        self.naturals = [7, 11]
        self.craps = [2, 3, 12]
        self.field_win = [2, 3, 4, 9, 10, 11, 12]
        self.field_loss = [5, 6, 7, 8]

class CrapsTable(object):
    """docstring for CrapsTable"""
    def __init__(self, config, args):
        self.table = config
        self.placebets = []
        self.laybets = []
        self.comebets = []
        self.dontcomebets = []

        self.verbose = args.v
        self.debug = args.d

        self.point = 0

        self.come_stage = 0
        self.dontcome_stage = 0

        self.build_table()

    def build_table(self):
        self.build_placebets()
        self.build_laybets()
        self.build_comebets()
        self.build_dontcomebets()
        self.fieldbet = FieldBet()
        self.passline =  PassLine(self.comebet_builder, self.table.payouts, self.table.caps)
        self.dontpassline = DontPassLine(self.comebet_builder, self.table.payouts, self.table.caps)
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
            self.dontcomebets.append(DontComeBet(item[0], item[1], self.table.payouts[item[1]], self.table.caps[item[1]]))

    def update_point(self, point):
        if point == 7 or self.point == point:
            self.point = 0
        else:
            self.point = point
            cprint('-->New point: {}'.format(point), 'cyan')
            self.passline.set_odds(point)
            self.dontpassline.set_odds(point)
            for cb in self.comebets:
                if cb.roll == point:
                    cb.set_point()

    def evaluate(self, player, dice):

        self.evaluate_fieldbet(player, dice)

        self.evaluate_laybets(player, dice)
        self.evaluate_placebets(player, dice)

        self.evaluate_passes(player, dice)

        self.evaluate_comebets(player, dice)
        self.evaluate_dontcomebets(player, dice)

        # I think stages need to be evaluated last
        # because they update bets
        self.evaluate_stages(player, dice)

    def evaluate_passes(self, player, dice):
        if self.point == 0:
            if dice in self.table.naturals:
                self.passline.payout(player)
                self.dontpassline.reset()
            
            elif dice in self.table.craps:
                self.passline.reset()
                if dice == 12:
                    self.dontpassline.bar(player)
                else:
                    self.dontpassline.payout(player)
        else:
            if dice == self.point:
                self.passline.payout(player)
                self.dontpassline.reset()
            
            elif dice == 7:
                self.passline.reset()
                self.dontpassline.payout(player)
        return

    def evaluate_comebets(self, player, dice):
        # If there is a match, the bet is a win
        # and must be paid
        if dice == 7:
            for cb in self.comebets:
                cb.reset()
        else:
            for cb in self.comebets:
                if cb.has_bet() and cb.roll == dice:
                    cb.payout(player)

    def evaluate_dontcomebets(self, player, dice):
        # If there is a match, the bet is a loss
        # and must be cleared. A 7 wins all don't comes
        if dice == 7:
            for dc in self.dontcomebets:
                if dc.has_bet():
                    dc.payout(player)
        else:
            for dc in self.dontcomebets:
                if dc.roll == dice:
                    dc.reset()
        return

    def evaluate_placebets(self, player, dice):
        if dice == 7:
            for pb in self.placebets:
                if not pb.off:
                    pb.reset()
        else:
            for pb in self.placebets:
                if pb.roll == dice and not pb.off:
                    pb.payout(player)
        return

    def evaluate_laybets(self, player, dice):
        if dice == 7:
            for lb in self.laybets:
                if not lb.off:
                    lb.payout(player)
        else:
            for lb in self.laybets:
                if lb.roll == dice and not lb.off:
                    lb.reset()
        return

    def evaluate_fieldbet(self, player, dice):
        if dice in self.table.field_win:
            self.fieldbet.payout(player)

        elif dice in self.table.field_loss:
            self.fieldbet.reset()

        return

    def evaluate_stages(self, player, dice):
        if self.point == 0:
            # Stages are not used on the come out
            pass
        else:
            if dice in [2, 3]:
                player.gain(self.dontcome_stage*2, 'dc stage')
            
            elif dice in [7, 11]:
                player.gain(self.come_stage*2, 'come stage')
            
            elif dice in [12]:
                player.gain(self.dontcome_stage, 'BAR2') #bar(refund)

            else:
                for cb in self.comebets:
                    if cb.roll == dice:
                        cb.bet = self.come_stage
                
                for dc in self.dontcomebets:
                    if dc.roll == dice:
                        dc.bet = self.dontcome_stage

        # Make sure the stages are empty at the end of evaluation
        self.come_stage = 0
        self.dontcome_stage = 0

    def seven(self, player):

        # Clear: field, comebets, stages, lines, lays, places
        self.fieldbet.reset()
        self.passline.reset()
        self.dontpassline.reset()
        self.come_stage = 0
        self.dontcome_stage = 0
        
        for cb in self.comebets:
            cb.reset()
        
        for dc in self.dontcomebets:
            dc.reset()

        for lb in self.laybets:
            lb.reset()

        for pb in self.placebets:
            pb.reset()

        return

    def play_round(self, player):
        playing = True
        while(playing):
            self.make_bets(player)

            if self.debug:
                self.readout(player)

            
            playing = self.roll(player)

            if self.verbose or self.debug:
                self.readout(player)
                if self.debug:
                    pdb.set_trace()
                print('')
                print('************************************************')
        print('~~~~ ROUND END ~~~~~')
        if not self.verbose and not self.debug:
            self.readout(player)
        return player.still_playing()

    def make_bets(self, player):
        # First division: Come Out and Point
        if self.point == 0:
            pass_bet = player.bet_pass(self)
            dontpass_bet = player.bet_dontpass(self)
            
            self.passline.make_bet(pass_bet)
            self.dontpassline.make_bet(dontpass_bet)

        else:
            #Field
            if player.confirm_fieldbet(self):
                bet = player.bet_field(self)
                self.fieldbet.make_bet(bet) 

            # Come
            if player.confirm_comebet(self):
                bet = player.bet_come(self)
                self.come_stage = bet

            # Don't come
            if player.confirm_dontcomebet(self):
                bet = player.bet_dontcome(self)
                self.dontcome_stage = bet

            # Lay
            for lb in self.laybets:
                if lb.has_bet():
                    continue
                elif self.point == lb.roll:
                    continue
                elif player.confirm_laybet(self, lb):
                    bet = player.bet_lay(self, lb)
                    lb.make_bet(bet)

            # Place
            for pb in self.placebets:
                if pb.has_bet():
                    continue
                elif self.point == pb.roll:
                    continue
                elif player.confirm_placebet(self, pb):
                    bet = player.bet_place(self, pb)
                    pb.make_bet(bet)

            # Pass odds
            if player.confirm_pass_odds(self):
                bet = player.bet_pass_odds(self)
                self.passline.bet_odds(bet)

            # Don't pass odds
            if player.confirm_dontpass_odds(self):
                bet = player.bet_dontpass_odds(self)
                self.dontpassline.bet_odds(bet)

        # Come odds
        for cb in self.comebets:
            if cb.has_bet():
                if player.confirm_come_odds(self, cb):
                    bet = player.bet_come_odds(self, cb)
                    cb.bet_odds(bet)

        # Don't Come odds
        for dc in self.dontcomebets:
            if dc.has_bet():
                if player.confirm_dontcome_odds(self, dc):
                    bet = player.bet_dontcome_odds(self, dc)
                    dc.bet_odds(bet)
        return

    def roll(self, player):
        dice = random.randint(1, 6) + random.randint(1, 6)

        cprint('*******************\n~~~DICE: {}~~~~\n*******************'.format(dice), 'yellow')

        self.evaluate(player, dice)

        if self.point == 0: # Come Out phase
            if dice in self.table.comeouts:
                self.update_point(dice)
                self.turn_on_bets()
            if dice == 7:
                self.seven(player)
            return (dice in self.table.comeouts)

        else: # Point phase
            if dice == 7:
                self.seven(player)
                self.update_point(dice)
                return False
            elif dice == self.point:
                self.update_point(dice)
                self.turn_off_bets()
                return False
            return True 

    def readout(self, player):
        print('---------Player---------')
        print('Total money: ${}'.format(player.money))
        print('\n---------Board---------')
        print('Pass line:    ${} (${})    Don\'t Pass:       ${} (${})'.format(self.passline.bet, self.passline.odds, self.dontpassline.bet, self.dontpassline.odds))
        print('Field:        ${}'.format(self.fieldbet.bet))
        print('Come stage:   ${}          Don\'t Come stage: ${}'.format(self.come_stage, self.dontcome_stage))
        print('')
        print('Come bets:')
        for cb in self.comebets:
            if cb.bet > 0:
                print('| {}:  ${}  (${}) |'.format(cb.roll, cb.get_bet(), cb.get_odds()), end = '')
        print('')
        print('Dont Come bets: ')
        for dc in self.dontcomebets:
            if dc.bet > 0:
                print('| {}:  ${} (${}) |'.format(dc.roll, dc.get_bet(), dc.get_odds()), end = '')
        print('')
        print('Place bets: ')
        for pb in self.placebets:
            if pb.bet > 0:
                if pb.is_on():
                    color = 'white'
                elif pb.is_off():
                    color = 'grey'
                cprint('| {}:  ${} |'.format(pb.roll, pb.bet), color, end = '')
        print('')
        print('Lay bets: ')
        for lb in self.laybets:
            if lb.bet > 0:
                if lb.is_on():
                    color = 'white'
                elif lb.is_off():
                    color='grey'
                cprint('| {}:  ${} |'.format(lb.roll, lb.bet), color, end = '')
        print('')
        cprint('POINT: {}'.format(self.point), 'cyan')

    def turn_on_bets(self):
        for lb in self.laybets:
            lb.turn_on()
        for pb in self.placebets:
            pb.turn_on()

    def turn_off_bets(self):
        for lb in self.laybets:
            lb.turn_off()
        for pb in self.placebets:
            pb.turn_off()

class PlaceBet(object):
    """docstring for PlaceBet"""
    def __init__(self, roll, name,  odd):
        self.name = name
        self.odds = odd
        self.bet = 0
        self.roll = roll
        self.point = False
        self.off = 1

    def payout(self, player):
        if self.bet > 0:
            amt = self.bet # bet refund
            amt += self.bet*self.odds # profit

            player.gain(floor(amt), 'place')
        self.reset()

    def reset(self):
        self.bet = 0
        self.point = False
        self.off = 0

    def turn_on(self):
        self.off = 0

    def turn_off(self):
        self.off = 1

    def make_bet(self, amt):
        self.bet = amt

    def has_bet(self):
        return self.bet > 0

    def is_on(self):
        return self.off == 0

    def is_off(self):
        return self.off == 1

class LayBet(object):
    """docstring for LayBet"""
    def __init__(self, roll, name,  odd):
        self.name = name
        self.odds = odd
        self.bet = 0
        self.roll = roll
        self.point = False
        self.off = 1

    def payout(self, player):
        if self.bet > 0:
            amt = self.bet # refund
            amt += self.bet*self.odds # profit
            player.gain(floor(amt), 'lay')
        self.reset()

    def reset(self):
        self.bet = 0
        self.off = 0

    def turn_on(self):
        self.off = 0

    def turn_off(self):
        self.off = 1

    def make_bet(self, amt):
        self.bet = amt

    def has_bet(self):
        return self.bet > 0

    def is_on(self):
        return self.off == 0

    def is_off(self):
        return self.off == 1

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
        amt = self.bet*2 # 1:1 payout
        amt += self.odds # odds refund
        amt += self.odds*self.odds_payout # odds payout
        player.gain(floor(amt), 'come')
        self.reset()

    def set_point(self):
        self.point = True
    
    def has_bet(self):
        return self.bet > 0

    def has_odds(self):
        return self.odds > 0

    def bet_odds(self, amt):
        if amt > self.bet*self.cap:
            cprint('ALERT: EXCEEDED TABLE ODDS CAP')
        self.odds = amt
    
    def get_bet(self):
        return self.bet

    def get_cap(self):
        return self.cap

    def get_key(self):
        return self.name

    def get_odds(self):
        return self.odds

class DontComeBet(object):
    """docstring for DontComeBet"""
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
        amt = self.bet*2 # 1:1 payout
        amt += self.odds # odds refund
        amt += self.odds*self.odds_payout # odds payout
        player.gain(floor(amt), 'don\'t come')
        self.reset()
    
    def has_bet(self):
        return self.bet > 0

    def has_odds(self):
        return self.odds > 0
    
    def bet_odds(self, amt):
        if amt > self.bet*self.cap:
            cprint('ALERT: EXCEEDED TABLE ODDS CAP')
        self.odds = amt
    
    def get_bet(self):
        return self.bet

    def get_cap(self):
        return self.cap

    def get_key(self):
        return self.name

    def get_odds(self):
        return self.odds

class FieldBet(object):
    """docstring for FieldBet"""
    def __init__(self):
        self.bet = 0

    def payout(self, player):
        player.gain(self.bet*2, 'field')
        self.reset()

    def reset(self):
        self.bet = 0

    def make_bet(self, amt):
        self.bet = amt

    def has_bet(self):
        return self.bet > 0

class PassLine(object):
    """docstring for PassLine"""
    def __init__(self, odds_key, payouts, caps):
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0
        self.odds_payout = 0
        self.odds_key_dict = odds_key
        self.payouts = payouts
        self.cap_list = caps

    def set_odds(self, point):
        self.point = point
        for odds in self.odds_key_dict:
            if odds[0] == self.point:
                self.key = odds[1]
                self.odds_payout = self.payouts[self.key]
                self.cap = self.cap_list[self.key]

    def payout(self, player):
        amt = self.bet*2 # 1:1 payout
        amt += self.odds # odds refund
        amt += self.odds*self.odds_payout # odds payout (this doesn't turn off)
        player.gain(floor(amt), 'pass')
        self.reset()

    def reset(self):
        cprint('pass line reset', 'red')
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0

    def make_bet(self, amt):
        self.bet = amt
    
    def has_bet(self):
        return self.bet > 0

    def bet_odds(self, amt):
        if amt > self.bet*self.cap:
            cprint('ALERT: EXCEEDED TABLE ODDS CAP')
        self.odds = amt

    def has_odds(self):
        return self.odds > 0
    
    def get_bet(self):
        return self.bet

    def get_key(self):
        return self.key

    def get_cap(self):
        return self.cap

class DontPassLine(object):
    """docstring for PassLine"""
    def __init__(self, odds_key, payouts, caps):
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0
        self.odds_payout = 0
        self.odds_key_dict = odds_key
        self.payouts = payouts
        self.cap_list = caps

    def set_odds(self, point):
        self.point = point
        for odds in self.odds_key_dict:
            if odds[0] == self.point:
                self.key = odds[1]
                self.odds_payout = self.payouts[self.key]
                self.cap = self.cap_list[self.key]

    def bar(self, player):
        amt = player.gain(self.bet, 'BAR') # full refund
        self.reset()

    def payout(self, player):
        amt = self.bet*2 # 1:1 payout
        amt += self.odds # odds refund
        amt += self.odds*self.odds_payout # odds payout (this doesn't turn off)
        player.gain(floor(amt), 'don\'t pass')
        self.reset()

    def reset(self):
        self.bet = 0
        self.odds = 0
        self.roll = 0
        self.point = 0
        self.odds_payout = 0

    def make_bet(self, amt):
        self.bet = amt
    
    def has_bet(self):
        return self.bet > 0

    def has_odds(self):
        return self.odds > 0

    def bet_odds(self, amt):
        if amt > self.bet*self.cap:
            cprint('ALERT: EXCEEDED TABLE ODDS CAP')
        self.odds = amt
    
    def get_bet(self):
        return self.bet

    def get_key(self):
        return self.key

    def get_cap(self):
        return self.cap

# Function declarations

def main(args):
    # Player enters the game
    player = Player()

    # House builds table and establishes rules
    table_rules = TableConfig(args)
    table = CrapsTable(table_rules, args)

    test_rounds = args.rounds
    for i in range(test_rounds):
        playing = table.play_round(player)
        if not playing:
            cprint('Exit at round {}'.format(i), 'yellow')
            break
    if player.broke:
        cprint('~*~*~*~*~*~*~*~*~*~*~*~', 'red')
    else:
        cprint('~*~*~*~*~*~*~*~*~*~*~*~', 'green')
    cprint('Peak $$$: {}'.format(player.max), 'cyan')
    cprint('Low  $$$: {}'.format(player.min), 'magenta')


# Main body
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Engine for craps simulation using a custom player strategy')
    parser.add_argument('-v', action='store_true', help='Verbose - Display table updates as the round progresses')
    parser.add_argument('-d', action='store_true', help='Run in debug mode')
    parser.add_argument('--rounds', default=50, type=int, help='Number of rounds to simulate.')
    args = parser.parse_args()
    main(args)