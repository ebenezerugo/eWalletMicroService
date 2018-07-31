from rest_framework import serializers
from .models import *


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'


class WalletDetailSerializer(serializers.ModelSerializer):

    currency_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionDetailSerializer(serializers.ModelSerializer):

    transaction_type = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class UserAndCurrencySerializer(serializers.Serializer):
    user_id = serializers.CharField(min_length=24, max_length=24)
    currency = serializers.CharField(min_length=3, max_length=10)


class TransactionDataSerializer(serializers.Serializer):
    user_id = serializers.CharField(min_length=24, max_length=24)
    currency = serializers.CharField(min_length=3, max_length=10)
    transaction_amount = serializers.FloatField()