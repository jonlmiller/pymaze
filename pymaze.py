"""Toplevel script for pymaze game - instanciate Game and then play it."""
import sys

from Game import Game

if len(sys.argv) != 2:
    host, port = 'localhost', '8089'
else:
    host, port = sys.argv[1].split(":")

game = Game("maze1.txt", host, int(port))
game.play()
