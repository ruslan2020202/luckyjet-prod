from api import create_app
import config as config


app = create_app(config.ProductionConfig)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print('Exit')
