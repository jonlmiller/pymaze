from GameObject import GameObject, Brain
import pygame
from pygame.locals import *

class OtherMissile(GameObject):
    """Class to model another player's missile"""

    def __init__(self, nickname, position, direction, color, object_hash = None):
        """Initialize a Missile object with same position and direction as its creator.

        Positional Arguments:

        nickname - nickname of new other missile
        position - initial position in maze: tuple of (vertical_offset, horizontal_offset)
        direction - initial direction
        color - object's color as (r, g, b) tuple

        Keyword Arguments:

        object_hash - specific object_hash when cloning from server (default is to generate one)
        """
        GameObject.__init__(
            self,
            nickname, 
            position, 
            direction,
            color = (255, 255, 255), #color,
            remote_object = True,
            object_hash = object_hash
        )

    def render_avatar(self, camera):
        # print(f"{self =} {self.color =}")
        radius = camera.square_center_height / 6
        # centered in the hallway horizontally and vertically at the player position
        center = (camera.pov_width / 2, camera.square_center_bottom - camera.square_center_height / 2)
        # when the Missile is exploding, it turns red and grows through 6 sizes
        pygame.draw.circle(
            camera.surface, self.color,
            center,
            radius
        )
