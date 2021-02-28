# import only system from os 
from os import system, name 
import sys
import time
sys.path.append("/Users/jon/.local/lib/python3.8/site-packages")
import pygame
from pygame.locals import *

from GameObject import GameObject, Brain
from Maze import Maze 
from Npc import Npc
from Player import Player
from Missile import Missile
from Exit import Exit
from Camera import Camera
from MazeClient import MazeClient
from GameState import GameState

class Game():
    """Manager for pygame"""

    def __init__(self, maze_filename):
        """Initialize the game manager object.

        Arguments:

        maze_filename - name of human readable/writable text file containing
            the maze definition for use in single player mode
        """

        gs = GameState.singleton()
        self.gs = gs

        gs.nickname = input("For multiplayer game, enter your nickname (default is single player):")
        if gs.nickname:
            gs.multiplayer = True
            # TODO - should be assigned by MazeServer
            while True:
                new_color_text = input(f"Choose a color code ({', '. join(list(gs.colors()))}) (default is w):")
                if not new_color_text:
                    break
                if new_color_text in gs.colors():
                    gs.color = gs.colors()[new_color_text]
                    break
                print(f"Unknown color code: '{new_color_text}''. Please try again.")
            print(f"Selected {gs.color}.")
            gs.connection = MazeClient('127.0.0.1', 8089)
            gs.connection.Loop()
            # server will send the maze data
            while not gs.maze:
                gs.connection.Loop()
        else:
            gs.maze = Maze(maze_filename)

        # loop through maze file and instanciate the specified objects

        for i in range(0, gs.maze.height):
            for j in range(0, gs.maze.width):
                ch = gs.maze.file_rows[i][j]
                if ch == 'P':
                    gs.player = Player((i, j))
                elif ch == 'N' and not gs.multiplayer:
                    Npc((i, j))
                elif ch == 'E' and not gs.multiplayer:
                    Exit(gs.maze, (i, j))


        # boiler plate pygame initialization (screen just black after this)

        gs.camera = Camera()

    def play(self):
        """Main game loop for pygame:
            1. update brains (GameObject finite state machines)
            2. if player moved, send to server
            3. redraw screen if needed.
            """
        gs = self.gs
        i = 0
        while True:
            Brain.everybody_think()
            if gs.multiplayer:
                # print(f"Game.play pausing before loop #{i}")
                # i += 1
                time.sleep(0.001)
                gs.connection.Loop()
                for go in gs.objects.values():
                    if go.moved:
                        go.moved = False
                        if not go.remote_object:
                            gs.connection.UpdateObjectOnServer(go)
            if gs.refresh_requested():
                gs.camera.show_player_pov()
 
    def clear(self): 
        """Clear screen of stdout device (terminal) on Mac, Windows, or Linux

        Only verified for Mac so far, but not used by pymaze
        """
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = system('clear') 

