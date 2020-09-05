import gameElements
from uuid import uuid1
import asyncio
from preload import sio, app, web


gameListings = {}

users = {}


class User():
    def __init__(self, name):
        self.name = name
        self.game = None
        self.player = None


def findInfo(sid):
    user = None
    game = None
    player = None
    if sid in users:
        user = users[sid]
        game = user.game
        player = user.player

    return user, game, player


creds = {
    "user": "pass",
    "user1": "pass1",
    "user2": "pass2"
}


@sio.on('Login')
async def login(sid, msg):
    if msg["user"] in creds:
        if creds[msg["user"]] == msg["pass"]:
            users[sid] = User(msg["user"])
            await sio.emit("Login Success", {}, sid)
        else:
            await sio.emit("Login Failed", {}, sid)
    else:
        await sio.emit("Login Failed", {}, sid)


@sio.on("Show Games")
async def showGames(sid):
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
    await sio.emit("Show Games", games, sid)


@sio.on("Create Game")
async def createGame(sid, msg):
    user, game, player = findInfo(sid)
    gameID = "G-" + str(uuid1())
    g = gameElements.Game(gameID, msg["title"], int(
        msg["numPlayers"]), user.name, "OPEN")
    p = gameElements.Player(g, user.name, sid)
    gameListings[gameID] = g
    p.isHost = True
    user.game = g
    user.player = p

    ret_msg = {
        "gameID": gameID,
        "title": g.title,
        "numPlayers": msg["numPlayers"],
        "creator": user.name,
        "status": "OPEN"
    }

    await sio.emit("Game Created", ret_msg)

    await sio.emit("Force Join Game", gameID, to=sid)


@sio.on("Join Game")
async def joinGame(sid, msg):
    user, game, player = findInfo(sid)
    gameID = msg
    if gameID in gameListings:
        g = gameListings[gameID]
        p = gameElements.Player(g, user.name, sid)
        user.game = g
        user.player = p
        g.addPlayerToGame(p)

        players = [{"name": player.name, "playerID": player.playerID,
                    "ready": player.isReady} for player in g.players]

        ret_msg1 = {
            "gameID": gameID,
            "playerID": p.playerID,
            "name": p.name,
        }

        await sio.emit("Another Joined Game", ret_msg1, room=gameID)

        sio.enter_room(sid, gameID)

        ret_msg2 = {
            "gameID": gameID,
            "title": g.title,
            "playerID": p.playerID,
            "name": p.name,
            "players": players,
        }

        await sio.emit("You Joined Game", ret_msg2, to=sid)


@sio.on("Choose Deck")
async def chooseDeck(sid, msg):
    user, game, player = findInfo(sid)
    player.cards = msg


@sio.on("Ready")
async def ready(sid):
    user, game, player = findInfo(sid)

    player.isReady = True

    allReady = True
    for player in game.players:
        if player.isReady == False:
            allReady = False

    if allReady and len(game.players) == game.numPlayers:

        for player in game.players:
            ret_msg = {
                "gameID": game.gameID,
                "relativePlayerList": [player.playerID for player in game.getRelativePlayerList(player)],
                "opponentsList": [{"name": opponent.name, "playerID": opponent.playerID} for opponent in game.getOpponents(player)]
            }
            asyncio.create_task(sio.emit("Start Game", ret_msg, to=player.sid))

        await asyncio.sleep(0)
        await game.run()

    else:
        ret_msg = {
            "gameID": game.gameID,
            "playerID": player.playerID
        }
        await sio.emit("Ready", ret_msg, room=game.gameID)


@sio.on("Not Ready")
async def notReady(sid):
    user, game, player = findInfo(sid)
    player.isReady = False

    ret_msg = {
        "gameID": game.gameID,
        "playerID": player.playerID
    }
    await sio.emit("Not Ready", ret_msg, room=game.gameID)


@sio.on("Answer Question")
async def answerQuestion(sid, msg):
    user, game, player = findInfo(sid)
    player.answer = msg


@sio.on("Take Action")
async def takeAction(sid, msg):
    user, game, player = findInfo(sid)
    player.chosenAction = msg


@sio.on("Pass")
async def passed(sid):
    user, game, player = findInfo(sid)
    player.passed = True


@sio.on("Declare Attacker")
async def declareAttacker(sid):
    user, game, player = findInfo(sid)
    player.declarations !=


if __name__ == '__main__':
    web.run_app(app, host='localhost', port=2129)
