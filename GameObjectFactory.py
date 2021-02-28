from OtherPlayer import OtherPlayer
from OtherMissile import OtherMissile

class GameObjectFactory():

    @classmethod
    def clone_object(cls, data):
        """Factory method for create various children of GameObject when server sends a clone.

        Arguments:

        data - the dictionary passed from MazeServer to MazeClient with a BroadcastNewObject() call.
        """
        if data['class'] == 'Player':
            OtherPlayer(
                nickname = data['nickname'],
                position = data['position'],
                direction = data['direction'],
                color = data['color'],
                object_hash = data['object_hash']
            )
        elif data['class'] == 'Missile':
            OtherMissile(
                nickname = data['nickname'],
                position = data['position'],
                direction = data['direction'],
                color = data['color'],
                object_hash = data['object_hash']
            )
            