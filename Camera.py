import pygame
from pygame.locals import *
import time
from GameObject import GameObject
from EyeBall import EyeBall
from Npc import Npc
from Exit import Exit
from OtherPlayer import OtherPlayer
from Missile import Missile
from GameState import GameState

class Camera():

    def __init__(self):
        self.gs = GameState.singleton()
        self.in_slo_mo = False

        # calculate screen and port sizes
        self.pov_width = 800
        self.pov_height = 600
        # size in pixels of side of square in the map view
        self.map_square_size = 10
        # total window size for POV and map
        self.window_width = self.pov_width + 1
        self.window_height = (self.pov_height + 
            self.map_square_size * (self.gs.maze.height + 2))
        # upper left window coord of map view
        self.map_left = (self.pov_width - 
            (self.map_square_size * self.gs.maze.width)) / 2
        self.map_top = self.pov_height + self.map_square_size
        self.square_center_bottom = None
        self.square_center_height = None

        pygame.init()
        icon = pygame.Surface((1,1))
        icon.set_alpha(0)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(
            f"You are: {self.gs.nickname} | pymaze.py - V0.2 - Jonathan Miller - " +
            f"W200 Fall 2020 Project 1 - Maze: " +
            f"{self.gs.maze.source}")
        print(f"POV port is ({self.pov_width} X {self.pov_height})")
        print(f"window  is ({self.window_width} X {self.window_height})")
        self.surface = pygame.display.set_mode(
            (self.window_width, self.window_height))
        pygame.display.update()


    def slo_mo(self):
        if self.in_slo_mo:
            pygame.display.update()
            time.sleep(0.5)

    def show_player_pov(self):
        """Draw player's (for now) 1st-person POV and map on the pygame.surface"""
        gs = self.gs

        self.surface.fill((0,0,0))

        self.slo_mo()

        # first draw the 1st person POV at the top of the window

        # calculate screen coords of 1st person view bounding box == the bounding box of the near wall
        #   of the player's current square
        front_top = 0
        front_bottom = self.pov_height
        front_left = 0
        front_right = self.pov_width

        # draw the 1st person view bounding box
        pygame.draw.aalines(
            self.surface, (255, 255, 255), True,
            [
                [front_left, front_top], 
                [front_right, front_top], 
                [front_right, front_bottom], 
                [front_left, front_bottom]
            ]
        )

        self.slo_mo()

        # start at player position
        player = gs.player
        depth = 0
        #print(f"{player =}, {player.position =}")
        position = player.position

        while not gs.maze.filled(position):
            # look left, right, and ahead for openings
            depth += 1
            if gs.trace_depth_render:
                print(f"drawing hall at {position}, depth = {depth}")
            # calculate screen coords of bounding box of the far wall of the player's current square
            back_top = self.pov_height / 2 - (self.pov_height / 2 / (depth + 1))
            back_bottom = self.pov_height / 2 + (self.pov_height / 2 / (depth + 1))
            back_left = self.pov_width / 2 - (self.pov_width / 2 / (depth + 1))
            back_right = self.pov_width / 2 + (self.pov_width / 2 / (depth + 1))

            # store the next position (which may be open or not)
            next_position = gs.maze.move(position, player.direction)

            # check if hall is open to right
            to_right = gs.maze.move(position, player.direction + 90)
            wall_to_right = gs.maze.filled(to_right)
            if wall_to_right:
                # draw the lines for a solid wall to right
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_right, front_top), (back_right, back_top))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_right, front_bottom), (back_right, back_bottom))
            else:
                # draw the lines for an open hall to right
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_right, front_top), (front_right, front_bottom))
                if not gs.maze.filled(next_position):
                    # but hide the right hand vertical line at the end of the hall
                    pygame.draw.aaline(
                        self.surface, (255, 255, 255),
                        (back_right, back_top), (back_right, back_bottom))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (back_right, back_top), (front_right, back_top))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (back_right, back_bottom), (front_right, back_bottom))      
           
            self.slo_mo()

            # check if hall is open to left
            to_left = gs.maze.move(position, player.direction - 90)
            wall_to_left = gs.maze.filled(to_left)
            if wall_to_left:
                # draw the lines for a solid wall to left
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_left, front_top), (back_left, back_top))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_left, front_bottom), (back_left, back_bottom))
            else:
                # draw the lines for an open hall to left
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (front_left, front_top), (front_left, front_bottom))
                if not gs.maze.filled(next_position):
                    # but hide the left hand vertical at the end of the hall
                    pygame.draw.aaline(
                        self.surface, (255, 255, 255),
                        (back_left, back_top), (back_left, back_bottom))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (back_left, back_top), (front_left, back_top))
                pygame.draw.aaline(
                    self.surface, (255, 255, 255),
                    (back_left, back_bottom), (front_left, back_bottom))

            self.slo_mo()

            # copy back-of-square bounding box to values for front-of-square bounding box
            front_left = back_left
            front_right = back_right
            front_top = back_top
            front_bottom = back_bottom
            # and move to the next position which might be open or filled
            position = next_position

        # draw the far wall, accounting for whether there's an opening on either side
        pygame.draw.aaline(
            self.surface, (255, 255, 255),
            (front_left, front_top), (front_right, front_top))
        pygame.draw.aaline(
            self.surface, (255, 255, 255),
            (front_left, front_bottom), (front_right, front_bottom))
        if wall_to_left:
            pygame.draw.aaline(
                self.surface, (255, 255, 255),
                (front_left, front_top), (front_left, front_bottom))
        if wall_to_right:
            pygame.draw.aaline(
                self.surface, (255, 255, 255),
                (front_right, front_top), (front_right, front_bottom))

        # draw other visible objects - back to front
        
        # object back_top = self.pov_height / 2 - (self.pov_height / 2 / (depth + 1))
        #     back_bottom = self.pov_height / 2 + (self.pov_height / 2 / (depth + 1))
        #     back_left = self.pov_width / 2 - (self.pov_width / 2 / (depth + 1))
        #     back_right = self.pov_width / 2 + (self.pov_width / 2 / (depth + 1))

        while depth > 1:
            position = gs.maze.move(position, player.direction + 180)
            self.square_center_height = (
                ((self.pov_height / depth) + (self.pov_height / (depth + 1))) / 2)
            self.square_center_bottom = (self.pov_height / 2) + (self.square_center_height / 2)
            if gs.trace_depth_render:
                print(
                    f"drawing objects at {position}, depth = {depth}, "
                    + f"square_center_bottom = {self.square_center_bottom}, "
                    + f"square_center_height = {self.square_center_height}")
            for t_hash in gs.objects:
                target = gs.objects[t_hash]
                if target != self.gs.player and target.position == position:
                    if gs.trace_depth_render:
                        print(f"rendering {target}")
                    target.render_avatar(self)
            depth -= 1

        # for time lapse rendering...
        self.slo_mo()
        self.in_slo_mo = False

        # then draw the maze overview map at the bottom of the window

        # loop through the maze data and draw each square as solid (gray) or open (white)
        for i in range(0, gs.maze.height):
            for j in range(0, gs.maze.width):
                if gs.maze.filled((i, j)):
                    color = (80, 80, 80)
                else:
                    color = (255, 255, 255)
                self.surface.fill(color,
                    Rect(
                        (self.map_left + j * self.map_square_size, self.map_top + i * self.map_square_size),
                        (self.map_square_size, self.map_square_size)
                    )
                )
        
        # loop through game objects (including player) and draw them in the map overview
        for go_hash in gs.objects:
            go = gs.objects[go_hash]
            if go.position:
                go.render_map(self)

        # and update the screen 
        pygame.display.update()
