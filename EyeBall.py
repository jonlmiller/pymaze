from GameObject import GameObject, Brain
import pygame
from pygame.locals import *

class EyeBall(GameObject):
    """Parent of OtherPlayer and Npc - adds eyeball render_avatar() method to GameObject."""

    def render_avatar(self, camera):
        # render another player in a multiplayer game
        radius = 0.8 * camera.square_center_height / 2
        center = (camera.pov_width / 2, camera.square_center_bottom - radius)
        pygame.draw.circle(
            camera.surface,
            self.color,
            center,
            radius
        )
        # now check for 4 possible pupil locations (pupil is hidden for one of them)
        target_rot_rel_player = (self.direction - self.gs.player.direction) % 360
        if target_rot_rel_player == 180:
            # other player or npc facing player
            pygame.draw.circle(
                camera.surface, (0, 0, 0),
                center,
                radius / 6
            )
        elif target_rot_rel_player == 90:
            # other player or npc facing to the player's right
            pygame.draw.circle(
                camera.surface, (0, 0, 0),
                (center[0] + radius, center[1]),
                radius / 6
            )
        elif target_rot_rel_player == 270:
            # other player or npc facing to the player's left
            pygame.draw.circle(
                camera.surface, (0, 0, 0),
                (center[0] - radius, center[1]),
                radius / 6
            )
