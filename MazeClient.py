#from __future__ import print_function

import sys
from time import sleep
from sys import stdin, exit
import random
from PodSixNet.Connection import connection, ConnectionListener
from GameObject import GameObject
from OtherPlayer import OtherPlayer
from GameState import GameState
from Maze import Maze
from GameObjectFactory import GameObjectFactory

class MazeClient(ConnectionListener):

    def __init__(self, host, port):
        print("MazeClient started")
        self.host = host
        self.port = port
        self.Connect((host, port))
        self.gs = GameState.singleton()
        self.RegisterClientWithServer()
    
    def Loop(self):
        connection.Pump()
        self.Pump()
        sleep(0.001)
        #print("MazeClient.Loop()")
    
    # MazeClient methods to message MazeServer

    def RegisterClientWithServer(self):
        print(f"RegisterClientWithServer({self.gs.client_hash})")
        connection.Send({
            "action": "registerclientwithserver", 
            "client_hash": self.gs.client_hash, 
            "nickname": self.gs.nickname, 
            "color": self.gs.color})

    # client is deregistered from server when it closes the connection

    def RegisterObjectWithServer(self, game_object):
        print(f"RegisterObjectWithServer({game_object.object_hash})")
        if game_object.remote_object:
            raise ValueError(f"tried to register remote object: "
                + f"{type(game_object).__name__}/{game_object.object_hash}")
        connection.Send({
            "action": "registerobjectwithserver",
            "nickname": game_object.nickname,
            "object_hash": game_object.object_hash,
            "position": game_object.position, 
            "direction": game_object.direction,
            "color": game_object.color,
            "class": type(game_object).__name__})

    def UpdateObjectOnServer(self, game_object):
        print(f"UpdateObjectOnServer({game_object.object_hash})")
        if game_object.remote_object:
            raise ValueError(f"tried to update remote object: "
                + f"{type(game_object).__name__}/{game_object.object_hash}")
        connection.Send({
            "action": "updateobjectonserver",
            "object_hash": game_object.object_hash,
            "position": game_object.position, 
            "direction": game_object.direction})
    
    def DeregisterObjectFromServer(self, game_object):
        print(f"DeregisterObjectFromServer({game_object.object_hash})")
        if game_object.remote_object:
            raise ValueError(f"tried to deregister remote object: "
                + f"{type(game_object).__name__}/{game_object.object_hash}")
        connection.Send({
            "action": "deregisterobjectfromserver",
            "object_hash": game_object.object_hash})

    def KillOriginalOnItsClient(self, game_object):
        print(f"KillOriginalOnItsClient({game_object.object_hash})")
        if not game_object.remote_object:
            raise ValueError(f"tried to kill local object via the server: "
                + f"{type(game_object).__name__}/{game_object.object_hash}")
        connection.Send({
            "action": "killoriginalonitsclient",
            "object_hash": game_object.object_hash})



    # listeners for messages from MazeServer to MazeClient 

    def Network_cloneobjectfromserver(self, data):
        data = data['data']
        print(f"Network_cloneobjectfromserver({data})")
        GameObjectFactory.clone_object(data)

    def Network_updateobjectclone(self, data):
        object_hash = data['object_hash']
        print(f"Network_updateobjectclone({object_hash})")
        go = self.gs.get_object_by_hash(object_hash)
        go.position = data['position']
        go.direction = data['direction']
        self.gs.request_refresh()

    def Network_killobjectclone(self, data):
        object_hash = data['object_hash']
        print(f"Network_killobjectclone({object_hash})")
        go = self.gs.get_object_by_hash(object_hash)
        if go:
            if go.remote_object:
                go.die()
                print(f"  killed: {go.object_hash}")
            else:
                raise ValueError("tried to killobjectclone a local object: "
                    + f"{type(go).__name__}/{go.object_hash}")
        else:
            print(f"  object not found")

    def Network_killoriginalobject(self, data):
        object_hash = data['object_hash']
        print(f"Network_killoriginalobject({object_hash})")
        go = self.gs.get_object_by_hash(object_hash)
        if go:
            if go.remote_object:
                print("  can't kill remote object")
            else:
                go.die()
                print(f"  killed: {go.object_hash}")
        else:
            print(f"  object not found")

    def Network_sendmazedatatoclient(self, data):
        print(f"Network_sendmazedatatoclient(...)")
        gs = GameState.singleton()
        gs.maze = Maze(maze_rows = data['maze'])
    
    # built in stuff

    def Network_connected(self, data):
        gs = GameState.singleton()
        print(f"You are now connected to the MazeServer @ " +
            f"{self.host}:{self.port} as {gs.nickname} [{gs.client_hash}]")
    
    def Network_error(self, data):
        print('error:', data['error'])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        host, port = 'localhost', 8089
    else:
        host, port = sys.argv[1].split(":")
    nickname = ''
    while not nickname:
        nickname = input("Enter your nickname:")
    c = MazeClient(host, int(port), nickname)
    while 1:
        c.Loop()
        sleep(0.001)
else:
    pass
    # from other code, do:
    # server_connection = Client(host, port, nickname)
    #
    # call once per game loop:
    # server_connection.Loop()
    #
    # to update your position:
    # server_connection.UpdateLocation(player.position, player.direction)

