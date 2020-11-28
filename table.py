#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os
import pdb

# Global variables

# Class declarations
class PlayerConfig(object):
	"""docstring for PlayerConfig"""
	def __init__(self):
		self.ante = 10
		self.buy_in = 500
		self.dontcome = 200
		self.place = 10
		self.lay = 10
		self.come = 10
		self.field = 0

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

class CrapsTable(object):
	"""docstring for CrapsTable"""
	def __init__(self, config):
		self.table = config
		self.placebets = []
		self.laybets = []
		self.comebets = []
		self.dontcomebets = []
		self.fieldbet = FieldBet(0)


		self.build_table()

	def build_table(self):
		self.build_placebets()
		self.build_laybets()
		self.build_comebets()
		self.build_dontcomebets()
		return

	def build_placebets(self):
		placebet_builder = [
			(4, "four_placebet"),
			(5, "five_placebet"),
			(6, "six_placebet"),
			(8, "eight_placebet"),
			(9, "nine_placebet"),
			(10, "ten_placebet")]
		for item in placebet_builder:
			self.placebets.append(PlaceBet(item[0], item[1], self.table.payouts[item[1]]))

	def build_laybets(self):
		laybet_builder = [
			(4, "four_laybet"),
			(5, "five_laybet"),
			(6, "six_laybet"),
			(8, "eight_laybet"),
			(9, "nine_laybet"),
			(10, "ten_laybet")]
		for item in laybet_builder:
			self.laybets.append(LayBet(item[0], item[1], self.table.payouts[item[1]]))

	def build_comebets(self):
		comebet_builder = [
			(4, "four_comebet"),
			(5, "five_comebet"),
			(6, "six_comebet"),
			(8, "eight_comebet"),
			(9, "nine_comebet"),
			(10, "ten_comebet")]
		for item in comebet_builder:
			self.comebets.append(ComeBet(item[0], item[1], self.table.payouts[item[1]], self.table.caps[item[1]]))

	def build_dontcomebets(self):
		dontcomebet_builder = [
			(4, "four_dontcomebet"),
			(5, "five_dontcomebet"),
			(6, "six_dontcomebet"),
			(8, "eight_dontcomebet"),
			(9, "nine_dontcomebet"),
			(10, "ten_dontcomebet")]
		for item in dontcomebet_builder:
			self.dontcomebets.append(DontComeBet(item[0], item[1]))


class PlaceBet(object):
	"""docstring for PlaceBet"""
	def __init__(self, roll, name,  payout):
		self.name = name
		self.payout = payout
		self.bet = 0
		self.roll = roll
		self.point = False
		self.off = False

class LayBet(object):
	"""docstring for LayBet"""
	def __init__(self, roll, name,  payout):
		self.name = name
		self.payout = payout
		self.bet = 0
		self.roll = roll
		self.point = False
		self.off = False

class ComeBet(object):
	"""docstring for ComeBet"""
	def __init__(self, roll, name, payout, cap):
		self.name = name
		self.roll = roll
		self.cap = cap
		self.payout = payout
		self.bet = 0
		self.odds = 0
		self.point = False
		self.off = False
		
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

class PassLine(object):
	"""docstring for PassLine"""
	def __init__(self, player):
		self.bet = player.ante
		self.odds = 0
		self.roll = 0
		self.point = 0
		
		

# Function declarations

def main():
    player = PlayerConfig()
    table_rules = TableConfig()
    table = CrapsTable(table_rules)
    pdb.set_trace()

# Main body
if __name__ == '__main__':
    main()
