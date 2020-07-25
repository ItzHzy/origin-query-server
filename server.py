from fastapi import FastAPI, WebSocket, HTTPException, Body
import asyncio
import uvicorn
import json
from uuid import uuid1
from gameElements import *
from gameActions import playLand, evaluate
from basicFunctions import declareActivation
from starlette.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel # pylint: disable=no-name-in-module

app = FastAPI()

# String to Game
gameListings = {}

connections = {}

# Test Creds
creds = { "user": "pass",
        "user1": "pass1",
        "user2": "pass2"}

class User():
    def __init__(self):
        self.username = None
        self.connection = None
        self.inGame = False
        self.currentGame = None
        self.currentPlayerID = None

class Token(BaseModel):
    access_token: str

@app.websocket_route("/")
async def recv(websocket: WebSocket):
    await websocket.accept()
    print("Connection Established")
    data = await websocket.receive_json()
    if data["access_token"] in connections:
        try:
            connections[data["access_token"]].connection = websocket
            print("Connection Verified")
            while True:
                await asyncio.sleep(0)
        except:
            del connections[data["access_token"]]

    print("Connection Closed")


class LoginMessage(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(msg: LoginMessage):
    if creds[msg.username] == msg.password:
        token = "T-" + str(uuid1())
        user = User()
        user.username = msg.username
        connections[token] = user
        return {"result": "success", "access_token": token}
    else:
        return {"result": "failed", "access_token": None}

@app.get("/games/show")
async def showAllGames(token: Token):
    if token.access_token in connections:
        socket = connections[token.access_token].connection
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
            "type": "/games/show",
            "data": games
        }

        socket.send_json(ret_msg)

    return {"result": "sent"}





if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=2129, log_level="debug")
    print("Server Closed")