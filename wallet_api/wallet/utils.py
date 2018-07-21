from hashlib import md5
from rest_framework.parsers import JSONParser
from datetime import datetime
from .serializers import *
import json


def get_hash_string(*args):
    text = ''
    for arg in args:
        text += arg
    return md5(text.encode()).hexdigest()


def get_wallet_creation_data(request):
    try:
        data = JSONParser().parse(request)
        data['wallet_created_date_and_time'] = datetime.now()
        data['wallet_id'] = get_hash_string(data['user_id'], data['currency'])
        data['currency_id'] = Currency.objects.get(currency_name=data['currency']).currency_id
        data['active'] = True
        data['current_balance'] = 0.0
        return data
    except Exception as e:
        return {'error': str(e)}


def get_transaction_data(request):
    try:
        data = JSONParser().parse(request)
        wallet_id = get_hash_string(data['user_id'], data['currency'])
        wallet = Wallet.objects.get(wallet_id=wallet_id)
        if not wallet.active:
            return {'error': 'Inactive wallet'}
        data['wallet_id'] = wallet.wallet_id
        data['transaction_id'] = get_hash_string(data['wallet_id'], str(
            data['transaction_amount']), str(datetime.now()))
        data['transaction_date'] = datetime.now().date()
        data['transaction_time'] = datetime.now().time()
        data['previous_balance'] = Wallet.objects.get(wallet_id=data['wallet_id']).current_balance
        return data
    except Exception as e:
        return {'error': str(e)}


def get_transactions(filters):
    transaction_objects = Transaction.objects
    transactions = list()
    if 'start_date' in filters.keys():
        try:
            start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
            if 'end_date' in filters.keys():
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
            else:
                end_date = start_date
            transaction_objects = transaction_objects.filter(transaction_date__range=(start_date, end_date))
        except Exception as e:
            print(e)
            transaction_objects = transaction_objects.none()

    if 'user_id' in filters.keys():
        try:
            wallets = Wallet.objects.filter(user_id=filters['user_id'])
            transactions_in_wallet = transaction_objects.none()
            for wallet in wallets:
                transactions_in_wallet = transactions_in_wallet | (
                    transaction_objects.filter(wallet_id=wallet.wallet_id))
            transaction_objects = transactions_in_wallet
        except Exception as e:
            print(e)
            transaction_objects = transaction_objects.none()

    if 'transaction_type' in filters.keys():
        try:
            transaction_type = TransactionType.objects.get(type_name=filters['transaction_type']).type_id
            transaction_objects = transaction_objects.filter(transaction_type=transaction_type)
        except Exception as e:
            print(e)
            transaction_objects = transaction_objects.none()

    for transaction in transaction_objects.all():
        transactions.append(TransactionSerializer(transaction).data)

    return transactions


def get_currency_config():
    with open('wallet/currency_config.json') as config:
        data = json.load(config)
    return data