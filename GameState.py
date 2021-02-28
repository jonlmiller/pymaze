import uuid

class GameState():
    """A Singleton for holding game state."""

    _singleton = None

    @classmethod
    def singleton(cls):
        """Return reference to the singleton GameState object, created first
        if it doesn't exist.
        """
        if not cls._singleton:
            cls._singleton = GameState()
        return cls._singleton

    def __init__(self):
        """Initialize the singleton GameState object attributes."""
        self.log_level = 0
        self.trace_depth_render = False
        self.client_hash = uuid.uuid4().hex     # for unique id to MazeServer
        self.nickname = None
        self.color = (0, 255, 0)
        self.maze = None
        self.objects = {}
        self.connection = None
        self.player = None
        self.need_refresh = True
        self.multiplayer = False

    def colors(self):
        return {
            'r': (255, 0, 0),
            'l': (0, 255, 0),
            'b': (0, 0, 255),
            'w': (255, 255, 255),
            'y': (255, 255, 0),
            'g': (0, 128, 0),
            'c': (0, 255, 255),
            'm': (255, 0, 255),
            'p': (128, 0, 128)
        }

    def get_object_by_hash(self, object_hash):
        """look for remote object by object_hash - return it if found, else return False"""
        if object_hash in self.objects:
            return self.objects[object_hash]
        else:
            return False

    def request_refresh(self):
        """Request a screen refresh after the game loop calls GameObject.everybody_think()"""
        self.need_refresh = True

    def refresh_requested(self):
        """Check if a screen refresh is needed (NOTE: the flag state is cleared when read!)"""
        need_refresh = self.need_refresh
        self.need_refresh = False
        if self.log_level >= 2:
            print(f"refresh_requested() returns {need_refresh}")
        return need_refresh


