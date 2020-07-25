from aiohttp import web
import socketio

sio = socketio.AsyncServer(logger=True, cors_allowed_origins=[])
app = web.Application()
sio.attach(app)
