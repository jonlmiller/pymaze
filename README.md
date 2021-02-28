### Installation ###

```
$ python3 -m pip install -U pygame
$ pip install podsixnet
```

### Single Player Game ###

```
$ python pymaze.py
pygame 2.0.0 (SDL 2.0.12, python 3.6.10)
Hello from the pygame community. https://www.pygame.org/contribute.html
For multiplayer game, enter your nickname (default is single player):
```

Press ENTER without entering a name to start single player pymaze. You should see this:

![pymaze starting view](./pymaze_opening_screen.png "pymaze opening screen")

Keyboard commands in the game:
* ‘a’ = turn left, ‘w’ = forward one square, ‘d’=  turn right, ‘z’ = back one square
* ‘f’ = fire a missile
* Exit with command-Q or alt-Q in the GUI, or with ctrl-C in the associated Terminal session.

There are several non-player characters (NPC's, or bad guys) roaming around with you. If you bump into one, you die.
Fire missiles ('f') to kill them -- they will not regenerate.

To win the game and exit, enter the square with with the green exit flag. 
It's located in the overhead view at the green arrow that isn't you,
and looks like a green square floating in space in the 1st person view.

### Multiplayer Game ###

To run multiplayer (on the same machine: 2+ clients plus a server):

In one terminal/shell, start the server:

```
$ python MazeServer.py
MazeServer launched
```

In one or more *other* terminals/shells, start the client:

```
$ python pymaze.py
pygame 2.0.0 (SDL 2.0.12, python 3.8.3)
Hello from the pygame community. https://www.pygame.org/contribute.html
For multiplayer game, enter your nickname (default is single player):
```

Enter a player name, followed by ENTER.

```
For multiplayer game, enter your nickname (default is single player):jon
Choose a color code (r, l, b, w, y, g, c, m, p) (default is w):
```

Choose a color from one of the single letter codes in the prompt, e.g., p for purple, followed by ENTER

```
Choose a color code (r, l, b, w, y, g, c, m, p) (default is w):p
```

You are now running around, by yourself, in the maze -- no bad guys, no exit.

Now add one or more additional players (from additional terminals/shells).
