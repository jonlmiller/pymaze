from GameObject import GameObject, Brain

class Maze():
    """Model of the user-defined maze for pygame"""
    
    def __init__(self, maze_filename = None, maze_rows = None):
        """Initialize the Maze object from the file: ./maze_file_name and store in self.squares[][].
        
        Keyword arguments:

        maze_filename - name of human readable/writable local text file containing the maze definition
        maze_rows - list of strings in maze file sent from server
        """

        self.source = None
        self.file_rows = None
        if maze_rows:
            self.file_rows = maze_rows
            print(f"received maze data from server")
            self.source = 'server'
        if maze_filename:
            self.maze_filename = maze_filename
            try:
                with open(self.maze_filename,"r") as infile:
                    raw_input = infile.readlines()
                    # the text lines in the file are stored in self.file_rows for extraction of object locations in Game.__init__()
                    self.file_rows = [datum.strip('\n') for datum in raw_input]
            except:
                raise ValueError(f"can't open file: {self.maze_filename}")
            print(f"read maze data from file: {self.maze_filename}")
            self.source = "file: " + self.maze_filename
        self.height = 0
        self.width = 0
        self.squares = []
        for row in self.file_rows:
            self.height += 1
            # all rows must have the same length
            if self.width:
                if len(row) != self.width:
                    raise ValueError(f"length of line #{self.height + 1} doesn't match length"
                                        + f" of line ${self.height} in file: {self.maze_filename}")
            else:
                self.width = len(row)
            # the structure of the maze is stored as a 2d array (list of lists): self.squares[i][j]
            #   where i is vertical offset (0 = top row, self.height-1 = bottom row)
            #   and j is horizontal offset (0 = left-most column, self.width-1 = right-most column)
            # each entry (one per cell or square in the maze) contains:
            #   1 if filled (i.e., blocked), or
            #   0 if empty (i.e., can be occupied)
            self.squares.append([(1 if ch=='x' else 0) for ch in row])
        print(f"created {self.width} wide by {self.height} high maze")
        
    def filled(self, position):
        """Test if the maze square located at position is filled (vs. empty).

        Positional Arguments:

        position - tuple of (vertical_offset, horizontal_offset) position in maze
        """
        i, j = position
        if 0 <= i < self.height and 0 <= j < self.width:
            return self.squares[i][j]
        # all positions outside of the defined area of the maze return as True (filled)
        return 1
    
    def move(self, position, direction):
        """Return the maze coordinate resulting from a 1 square move from position in direction.

        Positional Arguments:

        position - tuple of (vertical_offset, horizontal_offset) position in maze
        direction - absolute screen direction to move in: 0=up, 90=right, 180=down, 270=left
        """
        i, j = position
        direction %= 360
        if direction == 0:
            return (i - 1, j)
        if direction == 90:
            return (i, j + 1)
        if direction == 180:
            return (i + 1, j)
        if direction == 270:
            return (i, j - 1)
        raise ValueError(f"Maze.move called with bad angle = {direction}")

    def blocks(self, game_object, rotation = 0):
        """Return whether or not the maze would block a one square move by GameObject game_object
        from its current position, in a direction relative to its current direction.
        E.g., you can check if the player has its back against the wall with:
            maze.blocks(player, 180)

        Positional Arguments:

        game_object - the GameObject to check against the maze
        rotation - the relative angle added to game_object.direction before checking
        """
        return self.filled(self.move(game_object.position, game_object.direction + rotation))
