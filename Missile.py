from GameObject import GameObject, Brain
import pygame
from pygame.locals import *

class Missile(GameObject):
    """Class to model an missile - a child class of GameObject. (Only fired by player for now.)"""

    def __init__(self, from_game_object):
        """Initialize a Missile object with same position and direction as its creator.

        Arguments:

        from_game_object - reference to the GameObject (the creator) that fired the missile
        """
        GameObject.__init__(
            self,
            nickname = 'M', 
            position = from_game_object.position, 
            direction = from_game_object.direction,
            brain = MissileBrain(self),
            color = from_game_object.color
            )
        # record who created me, so i don't kill them by accident
        self.shot_from = from_game_object
        # state variable to control simple missile explosion animation
        self.die_cycle = 0

    def render_avatar(self, camera):
        """Render this missile from a Camera's view.

        Arguments:

        camera - a reference to the game's Camera object
        """

        # print(f"{self =} {self.color =}")
        radius = camera.square_center_height / 6
        # centered in the hallway horizontally and vertically at the player position
        center = (camera.pov_width / 2, camera.square_center_bottom - camera.square_center_height / 2)
        # when the Missile is exploding, it turns red and grows through 6 sizes
        pygame.draw.circle(
            camera.surface, self.color,
            center,
            radius * (self.die_cycle if self.die_cycle else 1)
        )

    def render_map(self, camera):
        GameObject.render_map(self, camera, use_color = (0, 0, 0))

class MissileBrain(Brain):
    """Class to model a Missile's brain, i.e., go forth quickly until NPC or wall."""

    def __init__(self, go):
        """Initialize the Missile's brain to fly, crash, and burn.

        Arguments:

        go - reference to the object that launched this missile
        """
        Brain.__init__(self, go, next_thought = self.go_till_wall)

    def go_till_wall(self):
        """Main Missile state - check before and after each step fwd: if collision with a target object
        (other than the creator object) then and kill the target and start the Missle explosion animation."""
        if not self.go.gs.maze.blocks(self.go, 0):
            # hall is open ahead
            for hash in self.go.gs.objects:
                target = self.go.gs.objects[hash]
                if target != self.go and target != self.go.shot_from and target.position == self.go.position:
                    target.die()
                    return self.die_cycle
            # fly forward...
            self.go.fwd()
            #   quickly.
            self.wait(0.1)
            for hash in self.go.gs.objects:
                target = self.go.gs.objects[hash]
                if target != self.go and target != self.go.shot_from and target.position == self.go.position:
                    target.kill()
                    return self.die_cycle
        else:
            # block ahead. time to explode
            self.go.die()

    def die_cycle(self):
        """Missile death state - 6 even quicker cycles (self.die_cycle controls animation), and then die."""
        self.go.die_cycle += 1
        if self.go.die_cycle == 6:
            self.go.die()
        self.wait(0.05)
        self.go.gs.request_refresh()
