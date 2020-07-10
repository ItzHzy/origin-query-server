import asyncio
import websockets
import json
from uuid import uuid1
from gameElements import *

# UUID -> Game
gameListings = {}

# Websocket -> User
connections = {}

# String -> User
users = {}

# Test Creds
credentials = {'user' : 'pass', 
                'user1': 'pass1',
                'user2': 'pass2'}

verified = set()

class User():
    def __init__(self, name, connection):
        self.name = name
        self.connection = connection

async def register(ws, name):
    verified.add(ws)
    user = User(name, ws)
    users[name] = user
    connections[ws] = user

async def unregister(ws):
    verified.remove(ws)

async def sendAll(msg):
    for ws in verified:
        await ws.send(msg)

async def server_handler(websocket, path):
    try: 
        async for data in websocket:
            msg = json.loads(data)
            await msg_handler(msg, websocket)
    finally:
        await unregister(websocket)

def startServer():
    server = websockets.serve(server_handler, "localhost", 2129)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

async def msg_handler(msg, ws):
    if ws not in verified:
        if credentials[msg['user']] != msg['pass']:
            print ("Login Failed. Closing Connection ")
            ret_msg = {"type": "Login","result": "Failed"}
            await ws.send(json.dumps(ret_msg))
            await ws.close()
        else: 
            await register(ws, msg['user'])
            ret_msg = {"type": "Login","result": "Success"}
            await ws.send(json.dumps(ret_msg))

    else:
        user = connections[ws]

        if msg["type"] == "Create Game":
            gameID = "G-" + str(uuid1())
            game = Game(gameID, msg["data"]["title"], int(msg["data"]["numPlayers"]), user.name, "OPEN")
            gameListings[gameID] = game
            player = Player(gameListings[gameID], user.name, ws)
            player.isHost = True

            ret_msg = {
                "type": "Create Game",
                "data": {
                    "gameID": gameID,
                    "title": game.title,
                    "numPlayers": msg["data"]["numPlayers"],
                    "creator": user.name,
                    "status": "OPEN"
                }
            }

            ret_msg = json.dumps(ret_msg)
            await sendAll(ret_msg)
        
        elif msg["type"] == "Show Games":
            games = []
            for gameID in gameListings:
                game = gameListings[gameID]
                entry = {}
                entry["gameID"] = game.gameID
                entry["title"] = game.title
                entry["numPlayers"] = game.numPlayers
                entry["status"] = game.status
                entry["creator"] = game.creator
                games.append(entry)
            
            ret_msg = {
                "type": "Show Games",
                "data": games
            }

            await ws.send(json.dumps(ret_msg))

        elif msg["type"] == "Join Game":
            gameID = msg["data"]["gameID"]
            if gameID in gameListings:
                game = gameListings[gameID]
                player = Player(gameListings[gameID], user.name, ws)
                game.addPlayerToGame(player)
                players = [[player.name, player.playerID] for player in game.players]

                ret_msg = {
                    "type": "Join Game",
                    "data": {
                        "gameID": gameID,
                        "playerID": player.playerID,
                        "players": players
                    }
                }

                for player in game.players:
                    await player.ws.send(json.dumps(ret_msg))
        
        elif msg["type"] == "Ready":
            allReady = True
            gameID = msg["data"]["gameID"]
            playerID = msg["data"]["playerID"]
            if gameID in gameListings:

                game = gameListings[gameID]
                for player in game.players:
                    if player.playerID == playerID:
                        player.isReady = True

                for player in game.players:
                    if player.isReady == False:
                        allReady = False

                if (allReady and len(game.players) == game.numPlayers):
                    game.prep()
                    ret_msg = {
                        "type": "Start Game",
                        "data": {
                            "numPlayers": game.numPlayers,
                            "players": [[player.playerID, player.name, player.lifeTotal, player.flavorText, player.pfp] for player in game.players]
                        }
                    }

                else:
                    ret_msg = {
                        "type": "Ready",
                        "data": {
                            "gameID": gameID,
                            "playerID": playerID
                        }
                    }     
                    
                for player in game.players:
                        await player.ws.send(json.dumps(ret_msg))

        elif msg["type"] == "Not Ready":
            gameID = msg["data"]["gameID"]
            playerID = msg["data"]["playerID"]
            if gameID in gameListings:
                game = gameListings[gameID]
                for player in game.players:
                    if player.playerID == playerID:
                        player.isReady = False

                for player in game.players:
                    ret_msg = {
                        "type": "Not Ready",
                        "data": {
                            "gameID": gameID,
                            "playerID": playerID
                        }
                    }
                    await player.ws.send(json.dumps(ret_msg))

        elif msg["type"] == "Choose Deck":
            gameID = msg["data"]["gameID"]
            playerID = msg["data"]["playerID"]
            if gameID in gameListings:
                game = gameListings[gameID]
                for player in game.players:
                    if player.playerID == playerID:
                        player.cards = msg["data"]["deck"]

if __name__ == "__main__":
    startServer()