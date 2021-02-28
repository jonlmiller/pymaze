from GameObject import GameObject, Brain
from EyeBall import EyeBall

class Npc(EyeBall):
    """Class to model an NPC - a child class of EyeBall."""

    def __init__(self, position):
        """Initialize an NPC object facing north, as positioned in the maze definition file.

        Positional Arguments:

        position - initial position in maze: tuple of (vertical_offset, horizontal_offset)
        """
        GameObject.__init__(
            self,
            'N',                                    # all NPCs have the label "N"
            position,
            0,
            brain = NpcBrain(self),                  # NPCs' simple brain = follow the right hand wall
            color = (255, 0, 0)
        )
        # these two lines save the start position from the map, then hide the NPC (position=None)
        # the NpcBrain pauses for 2 seconds before birthing the NPCs
        self.start_position = self.position
        self.position = None

class NpcBrain(Brain):
    """Class to model an NPC's brain, i.e., follow the right hand wall."""

    def __init__(self, go):
        """Initialize the NPC's' brain to think the thoughts about right hand walls.

        Positional Arguments:

        go - reference to the Npc object
        """
        # note that first thought doesn't occur until 2 seconds after game start
        Brain.__init__(self, go, delay_first = 2, next_thought = self.start)

    def start(self):
        """First NPC thought - put me on the board, then switch to thinking about right hand walls."""
        self.go.position = self.go.start_position
        return self.follow_right

    def follow_right(self):
        """Main NPC state - follow the right hand wall from wherever the NPC is first instanciated."""
        if not self.go.gs.maze.blocks(self.go, 90):
            # 1. if hall to right is open - turn towards it and take 1 step forward
            self.go.turn(90)
            self.wait(1)
            return self.go_fwd_one
        # hall to right is blocked...
        if self.go.gs.maze.blocks(self.go, 0):
            # 2. hall ahead is blocked (and hall to right is blocked) - turn left
            self.go.turn(-90)
            self.wait(1)
        else:
            # 3. hall ahead is open (and hall to right is blocked) - go forward
            self.go.fwd()
            self.wait(1)

    def go_fwd_one(self):
        """After turning to open hall on right, always then go fwd one before resuming follow_right."""
        self.go.fwd()
        self.wait(1)
        return self.follow_right
