from flask_restful import Resource
from flask import jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from faker import Faker
import random

from database.models import *
from schemas.sheme import *
from utils.crash import AlgorithmCrash

import requests


# class GameNew(Resource):
#     def post(self):
#         try:
#             # multiplier = AlgorithmCrash().get_result()
#             print(request.json.get('state'))
#             state = request.json.get('state')
#             print(None,'none')
#             # id = request.json.get('id')
#             # multiplier = request.json.get('multiplier')
#
#             game = GameModel(state['multiplier'], state['id'])
#             game.save()
#             print('game create')
#             print('game create id=' + state['id'] + 'multiplier = ' + state['multiplier'])
#             return GameSchema(many=False).dump(game), 201
#         except Exception as e:
#             return make_response(jsonify({'error': str(e)}))
class GameOver(Resource):
    def post(self, id):  # game_id
        try:
            multiplier = request.json.get("multiplier")
            bets = BetModel.query.filter_by(game_id=id).all()
            if not bets:
                return make_response(jsonify({'message': 'Bets not found'}), 404)
            game = GameModel(id, multiplier)
            game.save()
            for i in bets:
                if i.win is True:
                    sum = round((i.amount * i.multiplier), 2)
                    user = UsersModel.query.get(i.user_id)
                    user.balance += sum
                    user.save()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class GameNew(Resource):
    def post(self):
        try:
            state = request.json.get('state')

            if not isinstance(state, dict):
                return make_response(jsonify({'error': 'State must be an object'}), 400)

            game_id = state.get('id')
            multiplier = state.get('multiplier', None)  # Default to None if not present

            if game_id is None:
                return make_response(jsonify({'error': 'Game ID is required'}), 400)

            # Проверка существования записи с таким же id
            game = GameModel.query.filter_by(id=game_id).first()

            if game:
                if multiplier is not None:
                    game.multiplier = multiplier
                game.save()
            else:
                game = GameModel(id=game_id, multiplier=multiplier)
                game.save()

            return make_response(jsonify({'message': 'Game processed successfully'}), 200)

        except Exception as e:
            print(e)
            return make_response(jsonify({'error': str(e)}), 400)


class GameWork(Resource):
    def get(self, id):  # game_id
        game = GameModel.query.get(id)
        if not game:
            return make_response(jsonify({'error': 'not found game'}), 404)
        return GameSchema(many=False).dump(game), 200

    def post(self, id):  # game_id
        try:
            game = GameModel.query.get(id)
            if not game:
                return make_response(jsonify({'error': 'not found game'}), 404)
            game.status = False
            game.save()
            bets = BetModel.query.filter(BetModel.game_id == id).all()
            for i in bets:
                if i.win is True:
                    sum = round((i.amount * i.multiplier), 2)
                    user = UsersModel.query.get(i.user_id)
                    user.balance += sum
                    user.save()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class BetRouter(Resource):
    @jwt_required()
    def post(self, id):
        try:
            amount = int(request.json.get('amount'))
            user = UsersModel.query.get(get_jwt_identity())
            if user.block_bet:
                return make_response(jsonify({'message': 'bet already blocked'}), 403)
            if user.balance < amount or user.balance > 100000:
                return make_response(jsonify({'message': 'not enough money or stop limit is on'}), 400)
            if user.referal:
                stop_limit = SettingAppModel.find_by_admin_id(user.referal).stop_limit
                if user.balance > stop_limit:
                    return make_response(jsonify({'message': 'stop limit'}), 403)
            user.balance -= amount
            user.save()
            bet = BetModel(user.id, id, amount)
            bet.save()
            return make_response(jsonify({'message': 'success', '_id': bet.id}), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({'error': str(e)}))

    @jwt_required()
    def patch(self, id):  # bet_id
        try:
            user = UsersModel.query.get(get_jwt_identity())
            multiplier = request.json.get('multiplier')
            _id = request.json.get('_id')
            bet = BetModel.query.get(_id)
            if not bet:
                return make_response(jsonify({'message', 'not found this bet'}), 404)
            bet.win = True

            print(user.balance)

            if multiplier:
                bet.multiplier = float(multiplier)
            user.balance += bet.amount * multiplier
            user.save()

            bet.save()
            return make_response(jsonify({'message': 'success', 'amount': bet.amount, 'multiplier': multiplier}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class HistoryBets(Resource):
    def get(self):
        try:
            faker = Faker()
            bets = {
                'count': random.randint(150, 600),
                'bets': []
            }
            for i in range(24):
                bet = {
                    'name': faker.name(),
                    'bet': round(random.uniform(100, 15000)),
                    'multiplier': round(random.uniform(1.1, 2.2), 1)
                }
                bets['bets'].append(bet)
            return make_response(jsonify(bets), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class HistoryGames(Resource):
    def get(self):
        try:
            games = execute_data("""
            select id, multiplier
            from games
            where multiplier != 0
            order by _id desc 
            limit 23
            """)
            # print(games)
            return GameSchema(many=True).dump(games), 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class UserInfo(Resource):
    @jwt_required()
    def get(self):
        try:
            user = UsersModel.query.get(get_jwt_identity())
            return UserSchema(many=False).dump(user), 200
        except Exception as e:
            print(1)
            return make_response(jsonify({'error': str(e)}))


# ДЛЯ БОТА !!!
class AdminRouter(Resource):
    """
    при нажатии /start , в id уходит id админа в тг
    """

    def post(self, id):  # admin_id
        try:
            print(3)
            admin = AdminModel.query.get(id)
            print(2)
            if not admin:
                admin = AdminModel(id)
                admin.save()
                referal = ReferalPromocodesModel(id)
                referal.save()
                admin.save()
                SettingAppModel(id).save()
                SettingBotModel(id).save()
            print(1)
            data = execute_data(f"""
            select referal_promocodes.word, admins.referal_url, referal_promocodes.bonus
            from admins
            join referal_promocodes on admins.telegram_id = referal_promocodes.admin_id
            where admins.telegram_id = {id}
            """)

            print(data)
            return AdminSchema.schema_many(data), 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class BotUserWork(Resource):

    def get(self, id):  # admin_id
        """
        При нажатии кнопки мамонты на сайте, в id уходит id админа в тг
        """
        try:
            users = UsersModel.query.filter_by(referal=id).all()
            if not users:
                return make_response(jsonify({'message': 'Users not found'}), 404)
            return UserSchema(many=True).dump(users), 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))

    def post(self, id):  # admin_id
        """
        Добавление мамотна по логину
        """
        try:
            login = request.json.get('login')
            user = UsersModel.find_by_login(login)
            if user.referal:
                return make_response(jsonify({'message': 'User already has a referal'}), 403)
            user.referal = id
            user.save()
            return make_response(jsonify({'message': 'success added user'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))

    def delete(self, id):  # user_id
        try:
            user = UsersModel.query.get(id)
            user.referal = None
            user.save()
            return make_response(jsonify({'message': 'success delete'}))
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


class BalanceRouter(Resource):
    def post(self, id):  # user_id
        try:
            amount = float(request.json.get('amount'))
            user = UsersModel.query.get(id)
            if not user:
                return make_response(jsonify({'error': 'not found user'}), 404)
            user.balance += amount
            user.save()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))

    def put(self, id):  # user_id
        try:
            amount = request.json.get('amount')
            user = UsersModel.query.get(id)
            if not user:
                return make_response(jsonify({'error': 'not found user'}), 404)
            user.balance -= int(amount)
            if user.balance < 0:
                user.balance = 0.0
            user.save()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))

    def delete(self, id):  # user_id
        try:
            user = UsersModel.query.get(id)
            if not user:
                return make_response(jsonify({'error': 'not found user'}), 404)
            user.balance = 0
            user.save()
            return make_response(jsonify({'message': 'success delete balance'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class SignalRouter(Resource):
    def get(self):
        try:
            data = execute_data("""
            select id, multiplier
            from games
            where multiplier != 0
            order by _id desc
            limit 1
            """)
            if not data:
                return make_response(jsonify({'message': 'Game over'}), 400)
            return GameSchema(many=True).dump(data), 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class PromocodeRouter(Resource):
    def get(self, id):  # admin_id
        promocodes = PromocodesModel.query.filter_by(admin_id=id)
        if not promocodes:
            return make_response(jsonify({'message': 'not found promocode'}), 404)
        else:
            return PromoCodeSchema(many=True).dump(promocodes), 200

    def post(self, id):  # admin_id
        try:
            promo_code = request.json.get('promocode')
            type = request.json.get('type')
            amount = request.json.get('amount')
            count = request.json.get('count')
            data = PromocodesModel.query.filter_by(word=promo_code).first()
            if data:
                return make_response(jsonify({'message': 'promocode already exists'}), 400)
            else:
                PromocodesModel(promo_code, id, type, amount, count).save()
                return make_response(jsonify({'message': 'succes create promocode'}), 201)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class DepositRouter(Resource):
    def get(self, id):  # deposit_id
        """
        при проверке статуса начисления средств
        """
        try:
            deposit = DepositModel.query.get(id)
            if not deposit:
                return make_response(jsonify({'message': 'not found deposit'}), 404)
            if deposit.status is True:
                return make_response(jsonify({'message': 'money has not been transferred yet'}), 400)
            else:
                return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))

    @jwt_required()
    def post(self):
        """
        Для создание депозита
        """
        try:
            amount = int(request.json.get('amount'))
            type = request.json.get('type')
            print(type)
            user = UsersModel.query.get(get_jwt_identity())
            requisite = RequisiteModel.find_by_type(type)
            summ = amount
            if amount < 1000:
                return make_response(jsonify({'message': 'deposit is less than 1000'}), 400)
            if user.referal:
                if amount < SettingAppModel.query.filter_by(admin_id=user.referal).first().min_deposit:
                    return make_response(jsonify({'message': 'deposit is less than minimum'}), 400)
                if not DepositModel.query.filter_by(user_id=user.id).first():
                    bonus_amount = ReferalPromocodesModel.query.filter_by(admin_id=user.referal).first().bonus
                    amount += amount * bonus_amount / 100
            activated_promocode = ActivatedPromocodeModel.query.filter_by(user_id=user.id, status=True).all()
            for i in activated_promocode:
                promocode = PromocodesModel.query.get(i.promocode_id)
                print(promocode.id)
                print(i)
                if promocode.type == 'Бонус к пополнению':
                    amount += amount * promocode.bonus / 100
                    i.status = False
                    i.save()
                    break
            if type == 'btc':
                summ = round((amount / 5000000), 9)
            elif type == 'eth':
                summ = round((amount / 300000), 9)
            elif type == 'usdt':
                summ = round((amount / 85), 9)
            elif type == 'rub':
                pass
            else:
                return make_response(jsonify({'error': 'error country'}), 400)
            deposit = DepositModel(get_jwt_identity(), amount, summ, requisite.id)
            deposit.save()
            data = {
                "id": deposit.id,
                'summ': deposit.sum_payment,
                'type': type,
                'card': requisite.card,
                'user': user.login,
                'amount': amount
            }
            # res = request.post()
            # ВРЕМЕННО!!
            deposit.status = False
            user.balance += amount
            deposit.save()
            user.save()
            # # ВРЕМЕННО!!!
            return make_response(jsonify(data), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({'error': str(e)}), 500)

    def patch(self, id):  # deposit_id
        try:
            deposit = DepositModel.query.get(id)
            if not deposit:
                return make_response(jsonify({'not found deposit'}), 404)
            if deposit.status is False:
                return make_response(jsonify({'message': 'deposit is already active'}), 400)
            user = UsersModel.query.get(deposit.user_id)
            user.balance += deposit.amount
            deposit.status = False
            deposit.save()
            user.save()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class ActivatePromocodeRouter(Resource):
    @jwt_required()
    def post(self):
        word = request.json.get('promocode')
        user = UsersModel.query.get(get_jwt_identity())
        promocode = PromocodesModel.find_by_word(word)
        if promocode:
            if promocode.count > 0:
                activated = ActivatedPromocodeModel(get_jwt_identity(), promocode.id)
                activated.save()
                promocode.count -= 1
                promocode.save()
                if promocode.type == 'Баланс':
                    user.balance += promocode.bonus
                    user.save()
                    activated.status = False
                    activated.save()
                return make_response(jsonify({'message': 'success using promocode'}), 200)
            else:
                return make_response(jsonify({'message': 'promo code invalid'}), 403)
        else:
            return make_response(jsonify({'message': 'promocode not found'}), 404)


class BotUserInfo(Resource):
    def get(self, id):
        try:
            user = UsersModel.query.get(id)
            payout_method = PayoutModel.query.get(user.payout_method_id)
            data = UserSchema(many=False).dump(user)
            data['payout_method_name'] = payout_method.name
            data['payout_method_description'] = payout_method.description
            return data, 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


class PayoutRouter(Resource):
    @jwt_required()
    def post(self):
        try:
            amount = int(request.json.get('amount'))
            card = request.json.get('card')
            user = UsersModel.query.get(get_jwt_identity())
            # res = requests.post()
            if amount > user.balance:
                return make_response(jsonify({'message': 'Not enough money'}), 400)
            if user.referal:
                if amount < SettingAppModel.find_by_admin_id(user.referal).min_output:
                    return make_response(jsonify({'message': 'Minimal payout - 10000 RUB '}), 400)
            else:
                if amount < 10000:
                    return make_response(jsonify({'message': 'Minimal payout - 10000 RUB '}), 400)
            if user.block_payout:
                return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                         'в техническую поддержку'}), 403)
            payout_method = PayoutModel.query.get(user.payout_method_id)
            if payout_method.name == 'Ошибочный':
                return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                         'в техническую поддержку'}), 403)
            elif payout_method.name == 'Открытый':
                user.balance -= amount
                user.save()
                return make_response(jsonify({'message': 'success payout'}), 200)
            elif payout_method.name == 'Обычный':
                if FakeRequisitesModel.find_by_card(card):
                    user.balance -= amount
                    user.save()
                    return make_response(jsonify({'message': 'success payout'}), 200)
                else:
                    return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                             'в техническую поддержку'}), 403)
            elif payout_method.name == 'Верификационный':
                if FakeRequisitesModel.find_by_card(card):
                    if user.verification is False:
                        return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                                 'в техническую поддержку'}), 403)
                    else:
                        user.balance -= amount
                        user.save()
                    return make_response(jsonify({'message': 'success payout'}), 200)
                else:
                    return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                             'в техническую поддержку'}), 403)
            else:
                return make_response(jsonify({'message': 'Произошла ошибка вывода. Обратитесь'
                                                         'в техническую поддержку'}))
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


class Payment(Resource):
    def post(self):
        try:
            id = request.json.get('id')
            print(id)
            deposit = DepositModel.query.get(id)
            requisite = RequisiteModel.query.get(deposit.requisite_id)
            user = UsersModel.query.get(deposit.user_id)
            data = {
                "id": deposit.id,
                'summ': deposit.sum_payment,
                'type': requisite.type,
                'card': requisite.card,
                'user': user.login,
                'amount': deposit.amount
            }
            print(data)
            return make_response(jsonify(data), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({'error': str(e)}), 500)


class ChangeUser(Resource):
    def patch(self, id):  # user_id
        try:
            user = UsersModel.query.get(id)
            action = request.json.get('action')
            if action == 'block_payout':
                user.block_payout = 0
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class BotMirror(Resource):
    def post(self):
        try:
            pass
        except Exception as e:
            return make_response(jsonify({'error': str(e)}))


class MyBets(Resource):
    @jwt_required()
    def get(self):
        my_bets = BetModel.query.filter_by(user_id=get_jwt_identity()).all()
        return MyBetSchema(many=True).dump(my_bets), 200
