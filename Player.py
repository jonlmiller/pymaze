from GameObject import GameObject, Brain
from Missile import Missile
from Camera import Camera
from Npc import Npc
from Exit import Exit
from GameState import GameState

import pygame
from pygame.locals import *
import sys

class Player(GameObject):
    """Class to model the player - a child class of GameObject."""
    
    def __init__(self, position):
        """Initialize the the Player object facing east, as positioned in the maze definition file.

        Positional Arguments:

        position - initial position in maze: tuple of (vertical_offset, horizontal_offset)
        """
        gs = GameState.singleton()
        GameObject.__init__(
            self,
            position = position,
            direction = 90,                             # face east
            brain = PlayerBrain(self),      # Player's brain responds to control(ler) inputs
            color = gs.color,
            nickname = gs.nickname
        )
        
class PlayerBrain(Brain):
    """Class to model the player's brain, i.e., respond to control(ler) inputs."""

    def __init__(self, go):
        """Initialize the player's brain to think the thoughts about control(ler) inputs.

        Positional Arguments:

        go - reference to the Player object
        """
        Brain.__init__(self, go, next_thought = self.check_controls)

    def check_controls(self):
        """Think one player thought - the player's default state to respond to control(ler) inputs."""
        # TODO handle network/remote cases
        # if we crash into a Npc (non-player character), we both die
        for hash in self.go.gs.objects:
            target = self.go.gs.objects[hash]
            if target != self.go:
                if target.position == self.go.position:
                    if isinstance(target, Npc):
                        print(f"Player calls {target.object_hash}.die()")
                        target.die()
                        return self.die_next
                    elif isinstance(target, Exit):
                        return self.win_next
        # process the queued pygame.event's
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # move or fire
                if event.key == K_d:
                    self.go.turn(90)
                elif event.key == K_a:
                    self.go.turn(-90)
                elif event.key == K_w:
                    self.go.fwd()
                elif event.key == K_z:
                    self.go.back()
                elif event.key == K_f:
                    # launch a missile from player
                    Missile(self.go)
                elif event.key == K_m:
                    # trigger slo mo rendering
                    self.go.gs.camera.in_slo_mo = True
                    self.go.gs.request_refresh()
            elif event.type == QUIT:
                # terminate (cmd-Q or ctrl-Q)
                pygame.quit()
                sys.exit()

    def die_next(self):
        # TODO - ask to restart automatically?
        """A separate state when player dies - can be used to animation the player's demise."""
        self.go.die()
        print("*** you died. watch out for evil eyeballs ! **")
        pygame.quit()
        sys.exit()

    def die(self):
        print("*** you died. watch out for evil eyeballs ! **")
        pygame.quit()
        sys.exit()

    def win_next(self):
        print("*** YOU ENTERED THE EXIT... YOU WIN! **")
        pygame.quit()
        sys.exit()
        