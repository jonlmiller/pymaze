#from __future__ import print_function

import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class MazeClientChannel(Channel):
    """One MazeClient's connection to the MazeServer."""

    def __init__(self, *args, **kwargs):
        """A MazeClient opened a connection: Initialize the MazeClientChannel.

        The MazeClientChannel will not be registered with the MazeServer
        until the MazeClient sends a registerclientwithserver message to
        the MazeServer. 
        """
        self.client_hash = None
        self.nickname = None
        self.color = None
        self.objects = {}
        Channel.__init__(self, *args, **kwargs)
    
    def Close(self):
        """The MazeClient closed the connection: cleanly tear it down."""
        self._server.DeregisterClientFromServer(self)
    
    # listeners for messages from MazeClient to MazeServer

    def Network_registerclientwithserver(self, data):
        """MazeClient sent a registerclientwithserver message to the MazeServer.
        
        Record the registration data in the MazeClientChannel, then register
        the MazeClientChannel with the MazeServer."""
        print(f"Network_registerclientwithserver({data})")
        self.client_hash = data['client_hash']
        self.nickname = data['nickname']
        self.color = data['color']
        self.id = f"{self.nickname}|{self.client_hash}@{self.addr}"
        self._server.RegisterClientWithServer(self)

    def Network_registerobjectwithserver(self, data):
        """MazeClient sent a registerobjectwithserver message to MazeServer.

        Add the object info to this MazeClientChannel's list of registered
        objects, and then have the MazeServer broadcast it to all registered
        MazeClients.
        """
        object_hash = data['object_hash']
        print(f"Network_registerobjectwithserver({object_hash})")
        # TODO - check for dupes, and save nickname and class name (type)
        self.objects[object_hash] = data 

        # print(f"+1 >>> {len(self.objects)} objects on server for {self.id}:")
        # for object in self.objects.values():
        #     print(f"  {object}")
        self._server.BroadcastNewObject(self, object_hash)

    def Network_deregisterobjectfromserver(self, data):
        object_hash = data['object_hash']
        print(f"Network_deregisterobjectfromserver({object_hash})")
        self._server.BroadcastKillObject(self, object_hash)
        del(self.objects[object_hash])
        # print(f"-1 >>> {len(self.objects)} objects on server for {self.id}:")
        # for object in self.objects.values():
        #     print(f"  {object}")

    def Network_killoriginalonitsclient(self, data):
        object_hash = data['object_hash']
        print(f"Network_killoriginalonitsclient({object_hash})")
        self._server.BroadcastKillOriginalObject(self, object_hash)

    def Network_updateobjectonserver(self, data):
        object_hash = data['object_hash']
        print(f"Network_updateobjectonserver({object_hash})")
        self.objects[object_hash]['position'] = data['position']
        self.objects[object_hash]['direction'] = data['direction']
        # print(f"{self.id} updated objects[{object_hash}] = "
        #     + f"{self.objects[object_hash]}")
        self._server.BroadcastObjectUpdate(self, object_hash)


class MazeServer(Server):
    """The MazeServer -- connects together multiple MazeClients."""

    # somehow specifies MazeClientChannel to add for each connected client
    channelClass = MazeClientChannel
    
    def __init__(self, *args, **kwargs):
        """Initialize the MazeServer at server start."""
        Server.__init__(self, *args, **kwargs)
        # start with an empty dict of connected clients
        self.clients = {}
        self.maze_rows = None
        print('MazeServer launched')
    
    def Connected(self, client_channel, addr):
        """Callback when a new MazeClient connects to server."""
        print(f"{client_channel} client connected from {addr}")
    
    def list_clients(self, plus_or_minus):
        print(f"{plus_or_minus}1 >>> {len(self.clients)} registered clients:")
        for client_channel in self.clients.values():
            client = {
                'client_hash': client_channel.client_hash,
                'nickname': client_channel.nickname,
                'color': client_channel.color,
                'objects': client_channel.objects
            };
            print(f"  {client}")

    def RegisterClientWithServer(self, client_channel):
        """Register a connected MazeClientChannel with the MazeServer.
        
        The MazeServer then sends inital state info to the newly connected
        MazeClient: the shared maze, and info on all other MazeClients'
        object shared with all players.
        """
        print(f"RegisterClientWithServer({client_channel.id})")
        client_hash = client_channel.client_hash
        self.clients[client_hash] = client_channel
        self.list_clients('+')
        self.SendMazeDataToClient(client_channel)      # send maze data
        self.SeedServerStateOnClient(client_channel)  # and initial other objects
    
    def DeregisterClientFromServer(self, client_channel):
        """Deregister a previously registered MazeClient from the MazeServer.
                
        1. First, kill any/all of this MazeClient's objects which were cloned
        to other (still connected) MazeClients.
        2. Then, deregister this MazeClientChannel from the MazeServer.
        """
        print(f"DeregisterClientFromServer({client_channel.id})")
        client_id = client_channel.id
        client_hash = client_channel.client_hash
        self.BroadcastKillClientObjects(client_channel)
        del(self.clients[client_hash])
        self.list_clients('-')
    
    def SendMazeDataToClient(self, client_channel):
        """Send maze data to a registered MazeClient."""
        print(f"SendMazeDataToClient({client_channel.id})")
        client_hash = client_channel.client_hash
        client_channel.Send({
            "action": "sendmazedatatoclient",
            "maze": self.maze_rows
        })

    def SeedServerStateOnClient(self, client_channel):
        """Send initial MazeServer state to a registered MazeClient."""
        print(f"SeedServerStateOnClient({client_channel.id})")
        for target_channel in self.clients.values():
            if target_channel.client_hash != client_channel.client_hash:
                for object_hash in target_channel.objects:
                    client_channel.Send({
                        "action": "cloneobjectfromserver",
                        "data": target_channel.objects[object_hash]
                    })
                    print(f"  >> {target_channel.id} : {object_hash}")
                    # print(f"seedserver sent cloneobjectfromserver "
                    #     + f"{target_channel.objects[object_hash]} to {client_channel.id}")

    def BroadcastToOtherClients(self, client_channel, msg):
        """Broadcast a message to all clients other than then client doing the sending."""
        print(f"BroadcastToOtherClients({client_channel.id}, {msg})")
        for target_channel in self.clients.values():
            if target_channel.client_hash != client_channel.client_hash:
                print(f"  >> {target_channel.id} : {msg}")
                target_channel.Send(msg)

    def BroadcastNewObject(self, client_channel, object_hash):
        """Broadcast a newly registered object to the other MazeClients."""
        print(f"BroadcastNewObject({client_channel.id}, {object_hash})")
        self.BroadcastToOtherClients(client_channel, {
            "action": "cloneobjectfromserver",
            "data": client_channel.objects[object_hash]
        })

    def BroadcastObjectUpdate(self, client_channel, object_hash):
        """Broadcast new state for a registered object to the other MazeClients."""
        print(f"BroadcastObjectUpdate({client_channel.id}, {object_hash})")
        self.BroadcastToOtherClients(
            client_channel,
            {
                "action": "updateobjectclone",
                "object_hash": object_hash,
                "position": client_channel.objects[object_hash]['position'],
                "direction": client_channel.objects[object_hash]['direction']
            }
        )

    def BroadcastKillObject(self, client_channel, object_hash):
        """Broadcast message to kill the object to the other MazeClients."""
        print(f"BroadcastKillObject({client_channel.id}, {object_hash})")
        self.BroadcastToOtherClients(
            client_channel,
            {
                "action": "killobjectclone",
                "object_hash": object_hash
            }
        )

    def BroadcastKillOriginalObject(self, client_channel, object_hash):
        """Broadcast message to kill the object on its home server."""
        print(f"BroadcastKillOriginalObject({client_channel.id}, {object_hash})")
        self.BroadcastToOtherClients(
            client_channel,
            {
                "action": "killoriginalobject",
                "object_hash": object_hash
            }
        )

# TODO - maybe not killing!
    def BroadcastKillClientObjects(self, client_channel):
        """Broadcast killobject for each of MazeClient's objects to the other MazeClients."""
        print(f"BroadcastKillClientObjects({client_channel.id})")
        for object_hash in client_channel.objects:
            self.BroadcastKillObject(client_channel, object_hash)

    def Launch(self):
        i = 0
        while True:
            # print(f"MazeServer.Launch pausing before loop #{i}...")
            # i += 1
            sleep(0.001)
            self.Pump()

# get command line argument of server, port
if __name__ == '__main__':
    if len(sys.argv) != 2:
        host, port = 'localhost', '8089'
    else:
        host, port = sys.argv[1].split(":")
    with open("maze1.txt","r") as infile:
        raw_input = infile.readlines()
        maze_rows = [datum.strip('\n') for datum in raw_input]
    s = MazeServer(localaddr=(host, int(port)))
    s.maze_rows = maze_rows
    s.Launch()

