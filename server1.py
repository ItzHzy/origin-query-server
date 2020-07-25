from gameElements import *
from uuid import uuid1
import asyncio
from preload import sio, app, web

hello = []


gameListings = {}


sidToUser = {}


creds = {
    "user": {"pass": "pass", "user_id": "U-91cfe1dc-cbc3-11ea-87d0-0242ac130003"},
    "user1": {"pass": "pass1", "user_id": "U-ab1973c4-d267-45ce-9e0a-c29f9e238a6f"},
    "user2": {"pass": "pass2", "user_id": "U-9e9fbd5a-cbc4-11ea-87d0-0242ac130003"}
}


async def task():
    while True:
        while len(hello) == 0:
            await sio.sleep()
        await sio.emit(hello.pop(0), broadcast=True)


@sio.on('Login')
async def login(sid, msg):
    if msg["user"] in creds:
        if creds[msg["user"]]["pass"] == msg["pass"]:
            sidToUser[sid] = {"name": msg["user"]}
            await sio.emit("Login Success", {}, sid)
        else:
            await sio.emit("Login Failed", {}, sid)
    else:
        await sio.emit("Login Failed", {}, sid)


@sio.on("Show Games")
async def showGames(sid):
    if sid in sidToUser:
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
        await sio.emit("Show Games", {"games": games}, sid)


@sio.on("Create Game")
async def createGame(sid, msg):
    user = sidToUser[sid]
    gameID = "G-" + str(uuid1())
    game = Game(gameID, msg["title"], int(
        msg["numPlayers"]), user, "OPEN")
    gameListings[gameID] = game
    player = Player(gameListings[gameID], user["name"], sid)
    player.isHost = True

    ret_msg = {
        "gameID": gameID,
        "title": game.title,
        "numPlayers": msg["numPlayers"],
        "creator": user["name"],
        "status": "OPEN"
    }

    await sio.emit("Game Created", ret_msg)


@sio.on("Join Game")
async def joinGame(sid, msg):
    user = sidToUser[sid]
    gameID = msg["gameID"]
    if gameID in gameListings:
        game = gameListings[gameID]
        player = Player(gameListings[gameID], user["name"], sid)
        user["player"] = player
        game.addPlayerToGame(player)
        players = [[player.name, player.playerID] for player in game.players]

        ret_msg = {
            "gameID": gameID,
            "playerID": player.playerID,
            "players": players
        }

        sio.enter_room(sid, gameID)

        await sio.emit("Joined Game", ret_msg, room=gameID)


@sio.on("Choose Deck")
async def chooseDeck(sid, msg):
    user = sidToUser[sid]
    user["player"].cards = msg


@sio.on("Ready")
async def ready(sid):
    user = sidToUser[sid]
    game = user["player"].game

    allReady = True

    user["player"].isReady = True

    for player in game.players:
        if player.isReady == False:
            allReady = False

    if allReady and len(game.players) == game.numPlayers:
        ret_msg = {
            "numPlayers": game.numPlayers,
            "players": [[player.playerID, player.name, player.lifeTotal, player.flavorText, player.pfp] for player in game.players]
        }

        await sio.emit("Start Game", ret_msg, room=game.gameID)
        asyncio.create_task(game.run())

    else:
        ret_msg = {
            "gameID": user.currGame.gameID,
            "playerID": user.currPlayer.playerID
        }

        await sio.emit("Ready", ret_msg, room=game.gameID)


@sio.on("Not Ready")
async def notReady(sid):
    user = sidToUser[sid]
    game = user["player"].game
    user["player"].isReady = False

    ret_msg = {
        "gameID": user.currGame.gameID,
        "playerID": user.currPlayer.playerID
    }

    await sio.emit("Not Ready", ret_msg, room=game.gameID)


@sio.on("Answer Question")
async def answerQuestion(sid, msg):
    sidToUser[sid]["player"].answer = msg["answer"]


if __name__ == '__main__':
    web.run_app(app, host='localhost', port=2129)
