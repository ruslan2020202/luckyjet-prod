import flask_marshmallow as ma


class SchemaBase(ma.Schema):
    @classmethod
    def schema_many(cls, arg):
        if len(arg) > 1:
            return cls(many=True).dump(arg)
        else:
            return cls(many=False).dump(arg[0])


class UserSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('id', 'balance', 'admin', 'block_bet', 'block_payout',
                  'email', 'login', 'payout_method', 'referal',
                  'verification', '_id')


class GameSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('id', 'multiplier', 'status')


class AdminSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('word', 'referal_url', 'bonus')


class BetSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('id', 'multiplier')


class DepositSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('id', 'user', 'amount')


class PromoCodeSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('id', 'word', 'type', 'bonus', 'count')


class PayoutSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('user', 'amount', 'payout_method', 'card')


class MyBetSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('game_id', 'amount', 'multiplier', 'win')


class RequisiteSchema(SchemaBase, ma.Schema):
    class Meta:
        fields = ('type', 'card')
