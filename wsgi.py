from api import create_app, emit_game_updates
import config as config
from apscheduler.schedulers.background import BackgroundScheduler

app, socketio = create_app(config.DevelopmentConfig)

if __name__ == '__main__':
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=emit_game_updates, args=[socketio, app], trigger="interval", seconds=1)
        scheduler.start()

        # Запуск Flask-сервера
        socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print('Exit')
    finally:
        scheduler.shutdown()
