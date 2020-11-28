#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import sys
import os

# Global variables

# Class declarations
class Player(object):
    """docstring for PlayerConfig"""
    def __init__(self):
        self.ante = 10
        self.money = 500 # This is the buy-in
        self.dontcome = 200
        self.place = 10
        self.lay = 10
        self.come = 10
        self.field = 0

    def ante(self):
        self.money -= self.ante
        return self.ante

    def gain(self, value):
        self.money += value

# Function declarations

# def main():
    
#     #{1:this}

# # Main body
# if __name__ == '__main__':
#     main()
