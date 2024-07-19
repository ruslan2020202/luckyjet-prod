import time

from flask_socketio import SocketIO, emit

from database.models import GameModel
from schemas.sheme import GameSchema
from utils.crash import *



def sockets_add(app):
    socketio = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('message', {'data': 'Connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('state')
    def handle_state():
        game = GameModel.query.order_by(GameModel._id.desc()).first()
        emit('state', {'state': GameSchema().dump(game)})

    return socketio


def emit_game_updates(socketio, app):
    with app.app_context():
        while True:
            multiplier = AlgorithmCrash().get_result()
            game = GameModel(multiplier)
            game.save()
            print(game)
            socketio.emit('state', GameSchema().dump(game))
            socketio.sleep(14.5)
            game.state = 2
            game.save()
            socketio.emit('state', GameSchema().dump(game))
            flight_time = calculate_flight_time(game.multiplier)+2
            socketio.sleep(flight_time)
            game.state = 3
            game.save()
            socketio.emit('gameFinished', GameSchema().dump(game))



