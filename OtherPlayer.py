from GameObject import GameObject, Brain
from EyeBall import EyeBall
class OtherPlayer(EyeBall):
    """Class to model another player in multiplayer - child class of EyeBall."""

    def __init__(self, nickname, position, direction, color, object_hash = None):
        """Initialize another player in multiplayer game.

        Positional Arguments:

        nickname - nickname of new other player
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
            color = color,
            remote_object = True,
            object_hash = object_hash
        )

