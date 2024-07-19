from api import create_app, emit_game_updates
import config as config

app, socketio = create_app(config.DevelopmentConfig)

if __name__ == '__main__':
    try:
        # Запуск Flask-сервера
        socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print('Exit')
