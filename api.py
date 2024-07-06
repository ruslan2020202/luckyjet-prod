from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

from database.models import *
from resources.actions import register_actions
from resources.errors import Errors


def init_data(app):
    with app.app_context():
        PayoutModel('Ошибочный', 'Мамонту в любом случае будет выводить ошибку вывода через пару секунд',
                    False, True).save()
        PayoutModel('Открытый', 'Мамонт может выводить на любые реквизиты',
                    False, False).save()
        PayoutModel('Обычный', 'Мамонт может вывести только на реквизиты из меню воркера',
                    False, False).save()
        PayoutModel('Верификационный', 'Для вывода на реквизиты из меню воркера у мамонта должна быть'
                                       'верификация', True, False).save()

        RequisiteModel('rub', '2200280401269719').save()
        RequisiteModel('eth', '0x203626346af19EBf979025c5E1ce3D0cdA3bFe67').save()
        RequisiteModel('usdt', 'TSv2u6qdXMMVvJdWHSuVPD3XkwUybVkBDx').save()
        RequisiteModel('btc', 'bc1qzllzsaxzdc9t5055zpml5k8wsnmgye3t2w6jgf').save()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        # db.drop_all()
        db.create_all()
    JWTManager(app)
    CORS(app)
    Marshmallow(app)
    register_actions(app)
    Errors(app)
    # init_data(app)
    return app
