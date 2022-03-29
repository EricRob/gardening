#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pdb

# Global variables

# Class declarations
class Series(object):
	"""docstring for Series"""
	def __init__(self, player):
		self.peak = 0
		self.low = 0
		self.end_money = 0
		self.rounds = []
		self.buy_in = player.get_buy_in()

	def add_round(self, player):
		self.rounds.append(player.get_money())

	def end_series(self, player):
		self.peak = player.get_peak()
		self.low = player.get_low()
		self.end_money = player.get_money()

class Tracker(object):
	"""docstring for Tracker"""
	def __init__(self):
		self.series_log = []
		self.current_series = None

	def new_series(self, player):
		self.current_series = Series(player)

	def log_round(self, player):
		self.current_series.add_round(player)

	def end_series(self, player):
		self.current_series.end_series(player)
		self.series_log.append(self.current_series)
		self.current_series = None

	def summarize(self, player):
		h = []
		fig = plt.figure()
		ax1 = fig.add_subplot(311)
		fig.suptitle('{} Rounds,  Buy In: ${}, Cash Out: ${}'.format(len(self.series_log), player.get_buy_in(), player.get_cashout()))
		ax1.set_xlabel('Rounds')
		ax1.set_ylabel('Money')
		ax1.set_title('Winning Series')
		ax1.set_ylim([0, player.get_cashout()*1.1])

		ax2 = fig.add_subplot(312)
		ax2.set_xlabel('Rounds')
		ax2.set_ylabel('Money')
		ax2.set_title('Losing Series')
		ax2.set_ylim([0, player.get_cashout()*1.1])

		for series in self.series_log:
			h.append(series.end_money)
			y = series.rounds
			x = np.arange(1, len(y)+1)
			if series.end_money > series.buy_in:
				ax1.plot(x, y, color='lightgreen', alpha=0.6)
			else:
				ax2.plot(x, y, color='coral', alpha=0.6)

		ax3 = fig.add_subplot(313)
		ax3.set_title('Money at Series end')
		ax3.set_ylabel('qty')
		ax3.set_xlabel('End money')
		median = np.median(h)
		mean = np.mean(h)
		ax3.hist(h, bins=75)
		ax3.axvline(median, color='k', linestyle='dashed')
		ax3.axvline(mean, color='r', linestyle='dashed')
		min_ylim, max_ylim = ax3.get_ylim()
		ax3.text(median*1.05, max_ylim*0.9, 'Median: {:.2f}'.format(median))
		ax3.text(mean*1.05, max_ylim*0.9, 'Mean: {:.2f}'.format(mean))
		fig.tight_layout()
		plt.show()




# Function declarations

def main():
	pass

# Main body
if __name__ == '__main__':
    main()
