from hashlib import md5
from rest_framework.parsers import JSONParser
from .models import *
from datetime import datetime


def get_hash_string(*args):
    text = ''
    for arg in args:
        text += arg
    return md5(text.encode()).hexdigest()


def get_wallet_creation_data(request):
    data = JSONParser().parse(request)
    data['wallet_created_date_and_time'] = datetime.now()
    data['wallet_id'] = get_hash_string(data['user_id'], data['currency'])
    data['currency_id'] = Currency.objects.get(currency_name=data['currency']).currency_id
    data['current_balance'] = 0.0
    return data


def get_transaction_data(request):
    data = JSONParser().parse(request)
    data['transaction_id'] = get_hash_string(data['wallet_id'], str(
        data['transaction_amount']), str(datetime.now()))
    data['wallet_id'] = Wallet.objects.get(wallet_id=data['wallet_id'])
    data['transaction_date'] = datetime.now().date()
    data['transaction_time'] = datetime.now().time()
    data['previous_balance'] = Wallet.objects.get(wallet_id=data['wallet_id']).current_balance
    return data
