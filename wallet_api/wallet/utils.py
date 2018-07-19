from hashlib import md5
from rest_framework.parsers import JSONParser
from datetime import datetime
from .serializers import *


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


def get_transactions(filters):
    transaction_objects = Transaction.objects
    transactions = list()

    if 'start_date' in filters.keys():
        start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        if 'end_date' in filters.keys():
            end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        else:
            end_date = start_date
        transaction_objects = transaction_objects.filter(transaction_date__range=(start_date, end_date))

    if 'user_id' in filters.keys():
        wallets = Wallet.objects.filter(user_id=filters['user_id'])
        if not wallets:
            transaction_objects = transaction_objects.none()
        for wallet in wallets:
            transaction_objects = transaction_objects.filter(wallet_id=wallet.wallet_id)

    if 'transaction_type' in filters.keys():
        transaction_type = TransactionType.objects.get(type_name=filters['transaction_type']).type_id
        transaction_objects = transaction_objects.filter(transaction_type=transaction_type)

    for transaction in transaction_objects.all():
        transactions.append(TransactionSerializer(transaction).data)
    return transactions
