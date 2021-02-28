# This file contains both GameObject and Brain classes because they refer to each other
import time
import uuid
import pygame
from pygame.locals import *

from GameState import GameState

class GameObject():
    """Parent class of all objects located in the maze."""

    def __init__(
        self,
        nickname = None,
        position = None,
        direction = None,
        brain = None,
        color = None,
        remote_object = False,
        object_hash = None
    ):
        """Initialize a GameObject object.

        Keyword Arguments:

        nickname - label (needn't be unique) for this object (default: previous count of GameObjects)
        position - start position in maze (vertical_offset, horizontal_offset) (default: (0, 0) = not visible)
        direction - start orientatation: 0=north/up, 90=east/right, ... (default: 0=north)
        brain - reference to a Brain object containing the object's FSM (default: None (just stand there))
        color - this object's color when rendered
        remote_object - False for local objects, True for objects which are objects cloned by the server from other players' games.
        object_hash - only specified for remote objects (clones of an object that lives in another client)
        """
        self.gs = GameState.singleton()
        self.object_hash = object_hash if object_hash else uuid.uuid4().hex
        self.nickname = nickname if nickname else '??'
        self.position = position if position else (0, 0)
        self.direction = direction if direction else 0
        self.brain = brain if brain else None
        self.color = color if color else None
        self.dead = False
        self.moved = True
        self.remote_object = remote_object
        self.gs.objects[self.object_hash] = self
        if not self.remote_object:
            if self.gs.connection:
                self.gs.connection.RegisterObjectWithServer(self)
        self.gs.request_refresh()

    def turn(self, degrees):
        """Rotate this GameObject and request a screen refresh.

        Arguments:

        degrees - amount to turn: >0 for CW, <0 for CCW, only use multiples of 90
        """
        self.direction = (self.direction + degrees) % 360
        self.moved = True
        self.gs.request_refresh()
        
    def fwd(self):
        """If not blocked by the maze, move this GameObject forward one square (according to its direction)
        from its current position and request a screen refresh.
        """
        if not self.gs.maze.blocks(self, 0):
            self.position = self.gs.maze.move(self.position, self.direction)
            self.moved = True
            self.gs.request_refresh()

    def back(self):
        """If not blocked by the maze, move this GameObject back one square (according to its direction))
        from its current position and request a screen refresh.
        """
        if not self.gs.maze.blocks(self, 180):
            self.position = self.gs.maze.move(self.position, self.direction + 180)
            self.moved = True
            self.gs.request_refresh()

    def die(self):
        """Flag this GameObject for deletion in this game cycle and request a screen refresh."""
        print(f"{self.object_hash}.die() called")
        if self.remote_object:
            # if this is a clone of a remote object, send msg to kill original
            self.gs.connection.KillOriginalOnItsClient(self)
        else:
            # if this is the original, deregister it from server and all the clones will go to
            if self.gs.multiplayer:
                self.gs.connection.DeregisterObjectFromServer(self)
        self.dead = True
        print(f"  sets self.dead=True")
        self.gs.request_refresh()
        return None

    def kill(self):
        """Unused"""
        # override this to create a death behavior
        self.die()

    def on_die(self):
        """Override this in child class for specific action upon death."""
        pass

    def render_avatar(self, camera):
        """Override this in child class to provide point of view renderer to the camera."""
        pass

    def render_map(self, camera, use_color = None):
        """Default renderer for showing object on the map overview.

        Override this in a child class to draw something other than a colored arrow.
        """ 
        color = use_color if use_color else self.color
        i, j = self.position
        gs = GameState.singleton()
        ci = camera.map_top + (i + 0.5) * camera.map_square_size
        cj = camera.map_left + (j + 0.5) * camera.map_square_size
        v1 = gs.maze.move((0, 0), self.direction + 180)
        v2 = gs.maze.move((0, 0), self.direction)
        v3 = gs.maze.move((0, 0), self.direction - 90)
        v4 = gs.maze.move((0, 0), self.direction + 90)
        p1 = [cj + 4 * v1[1], ci + 4 * v1[0]]
        p2 = [cj + 4 * v2[1], ci + 4 * v2[0]]
        p3 = [cj + 3 * v3[1], ci + 3 * v3[0]]
        p4 = [cj + 3 * v4[1], ci + 3 * v4[0]]
        pygame.draw.aalines(camera.surface, color, False, [p1, p2, p3, p4, p2])

class Brain():
    """Parent class of all GameObject brains (AI's, FSM's, ...)."""

    def __init__(self, game_object, delay_first = 0, next_thought = None):
        """Initialize the Brain.

        Note: All thoughts thought by a Brain should be methods of that Brain object.

        Keyword Arguments:

        game_object - reference to this Brain's body
        delay_first - initial delay in seconds before thinking first thought (default: 0)
        first_thought - first state transition made after initial delay (default: just stand there)
        """
        self.go = game_object
        self.next_thought = next_thought
        self.wait(delay_first)
    
    def think(self):
        """Think a thought: after completing an optional (non-blocking) delay, and if next_thought is
        definied, called the next_thought function to update the GameObject's state. If the next_thought
        function returns a value, that becomes the new next_thought function.
        """
        if self.go.gs.log_level >= 2:
            print(f"Brain.think({self}): sleep_until={self.sleep_until} next_thought={self.next_thought}")
        # non-blocking asynchronous delay for this GameObject only
        if self.sleep_until:
            if time.time() > self.sleep_until:
                self.sleep_until = 0
            else:
                return
        # if there's a next thought
        if self.next_thought:
            # then think it
            next_thought = self.next_thought()
            # and if it changes your mind (state), then save the function reference for the next update
            if next_thought:
                self.next_thought = next_thought
                if self.go.gs.log_level >= 2:
                    print(f"   next_thought << {self.next_thought}")

    def wait(self, seconds):
        """Set the delay until the next thought.

        Positional Arguments:

        seconds - delay until next thought is thunk (default: 0)
        """
        self.sleep_until = time.time() + seconds

    @classmethod
    def everybody_think(cls):
        """Brain class method to update the brains (finite state machines) for each local GameObject in the maze."""
        gs = GameState.singleton()
        # first let each object think
        # can't use for loop since an object may add other object(s) in its brain
        # TODO - take into account local vs. remote (cloned) objects
        hashes = list(gs.objects)
        for go_hash in hashes:
            go = gs.objects[go_hash]
            if go.brain:
                if go.remote_object:
                    raise ValueError(f"remote object {go_hash} also has a brain! shouldn't happen")
                go.brain.think()
        # then kill any resulting dead objects (even if they thought they were still thinking in the previous loop)
        # can't use for loop since we may delete GameObject(s) from the list GameObject.game_objects
        # TODO - also need to collision detect between our local objects, and all the other remote objects
        #   1. need to check remote objects
        #   2. need to update local objects to server for multiplayer
        hashes = list(gs.objects)
        for go_hash in hashes:
            go = gs.objects[go_hash]
            if gs.log_level >= 2:
                print(f"  checking {go}.dead = {go.dead}")
            if go.dead:
                # TODO - needs work wrt network state
                if gs.player == go:
                    gs.player = None
                del(gs.objects[go_hash])
                print(f"Main loop deleted {go_hash}")
                if gs.multiplayer:
                    gs.connection.Loop()
                go.gs.request_refresh()


