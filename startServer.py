import asyncio
import websockets
import json
from uuid import uuid1
from gameElements import *
from time import sleep
from gameActions import playLand, evaluate
from basicFunctions import declareActivation

# String to Game
gameListings = {}

# Websocket -> User
connections = {}

verified = set()

# Test Creds
credentials = {'user' : 'pass', 
                'user1': 'pass1',
                'user2': 'pass2'}

class User():
    def __init__(self, name, connection):
        self.name = name
        self.connection = connection
        self.inGame = False
        self.currGame = None
        self.currPlayer = None

async def register(ws, name):
    verified.add(ws)
    user = User(name, ws)
    connections[ws] = user

async def unregister(ws):
    verified.remove(ws)
    del connections[ws]

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
        if user.inGame:
            game = user.currGame
            player = user.currPlayer

        if msg["type"] == "Create Game":
            gameID = "G-" + str(uuid1())
            game = Game(gameID, msg["data"]["title"], int(msg["data"]["numPlayers"]), user.name, "OPEN")
            gameListings[gameID] = game
            player = Player(gameListings[gameID], user.name, ws)
            player.isHost = True
            user.currGame = game
            user.currPlayer = player
            user.inGame = True

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
                user.currGame = game
                user.currPlayer = player
                user.inGame = True
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
        
        elif msg["type"] == "Ready" and user.inGame:
            allReady = True

            user.currPlayer.isReady = True

            for player in game.players:
                if player.isReady == False:
                    allReady = False

            if allReady and len(game.players) == game.numPlayers:
                ret_msg = {
                    "type": "Start Game",
                    "data": {
                        "numPlayers": game.numPlayers,
                        "players": [[player.playerID, player.name, player.lifeTotal, player.flavorText, player.pfp] for player in game.players]
                    }
                }

                try:
                    for player in game.players:
                        await player.ws.send(json.dumps(ret_msg))
                finally:
                    await game.prep()

            else:
                ret_msg = {
                    "type": "Ready",
                    "data": {
                        "gameID": user.currGame.gameID,
                        "playerID": user.currPlayer.playerID
                    }
                }

                for player in game.players:
                    await player.ws.send(json.dumps(ret_msg))

        elif msg["type"] == "Not Ready" and user.inGame:
            user.currPlayer.isReady = False

            ret_msg = {
                    "type": "Not Ready",
                    "data": {
                        "gameID": user.currGame.gameID,
                        "playerID": user.currPlayer.playerID
                    }
                }

            for player in game.players:
                await player.ws.send(json.dumps(ret_msg))

        elif msg["type"] == "Choose Deck" and user.inGame:
            user.currPlayer.cards = msg["data"]["deck"]
            
            msg = {
                "type": "Choose Deck"
            }

            await ws.send(json.dumps(msg))

        elif msg["type"] == "Play Land" and user.inGame:
            instanceID = msg["data"]["instanceID"]
            await evaluate(user.currGame, playLand, user.currGame.allCards[instanceID])

        elif msg["type"] == "Activate Ability" and user.inGame:
            abilityID = msg["data"]["abilityID"]
            await evaluate(user.currGame, declareActivation, abilityID)

if __name__ == "__main__":
    startServer()