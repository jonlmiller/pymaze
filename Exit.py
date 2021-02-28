from GameObject import GameObject, Brain
import pygame
from pygame.locals import *

class Exit(GameObject):
    
    def __init__(self, maze, position):
        GameObject.__init__(
            self,
            'E',
            position,
            0,
            color = (0, 255, 0)
        )

    def render_avatar(self, camera):
        #render the exit
        bottom = camera.square_center_bottom
        left = camera.pov_width / 2 - camera.square_center_height / 2
        right = camera.pov_width / 2 + camera.square_center_height / 2
        top = camera.square_center_bottom - camera.square_center_height
        # pygame.draw.aalines(
        #     camera.surface, self.color, True,
        #     [
        #         [left, top], 
        #         [right, top], 
        #         [right, bottom], 
        #         [left, bottom]
        #     ]
        # )
        pygame.draw.rect(
            camera.surface, self.color, (
                (left, top), (right-left, bottom-top)
            )
        )

