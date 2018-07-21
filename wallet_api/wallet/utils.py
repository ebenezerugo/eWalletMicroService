from hashlib import md5
from datetime import datetime
from .serializers import *
import json
from django.db import transaction
from django.http import JsonResponse
from rest_framework import status

CONSTANTS = {
    'WALLET_INITIAL_STATUS': True,
    'WALLET_INITIAL_BALANCE': 0.0,
}


def get_hash_string(*args):
    text = ''
    for arg in args:
        text += arg
    return md5(text.encode()).hexdigest()


def get_context(**kwargs):
    return kwargs


def get_wallet_creation_data(data):
    try:
        data['wallet_created_date_and_time'] = datetime.now()
        data['wallet_id'] = get_hash_string(data['user_id'], data['currency'])
        data['currency_id'] = Currency.objects.get(currency_name=data['currency']).currency_id
        data['active'] = CONSTANTS['WALLET_INITIAL_STATUS']
        data['current_balance'] = CONSTANTS['WALLET_INITIAL_BALANCE']
        return data
    except Exception as e:
        return get_context(error=str(e))


def get_new_balance(data, transaction_type):
    if transaction_type == 'CREDIT':
        return data['previous_balance'] + data['transaction_amount']
    if transaction_type == 'DEBIT':
        return data['previous_balance'] - data['transaction_amount']


def get_transaction_data(data, transaction_type):
    try:
        wallet_id = get_hash_string(data['user_id'], data['currency'])
        wallet = Wallet.objects.get(wallet_id=wallet_id)
        if not wallet.active:
            return get_context(error='Inactive wallet')
        data['wallet_id'] = wallet.wallet_id
        data['transaction_id'] = get_hash_string(data['wallet_id'], str(
            data['transaction_amount']), str(datetime.now()))
        data['transaction_date'] = datetime.now().date()
        data['transaction_time'] = datetime.now().time()
        data['previous_balance'] = Wallet.objects.get(wallet_id=data['wallet_id']).current_balance
        data['transaction_type'] = TransactionType.objects.get(type_name=transaction_type).type_id
        data['current_balance'] = get_new_balance(data, transaction_type)
        return data
    except Exception as e:
        return get_context(error=str(e))


def check_limit(data):
    currency = Wallet.objects.get(wallet_id=data['wallet_id']).currency_id_id
    limit = Currency.objects.get(currency_id=currency).currency_limit
    if data['current_balance'] > limit:
        return True
    else:
        return False


def make_transaction(data, transaction_type):
    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        with transaction.atomic():
            Wallet.objects.filter(wallet_id=data['wallet_id']).update(current_balance=data['current_balance'])
            serializer.save()
        context = get_context(current_balance=data['current_balance'], message=transaction_type + ' Successful',
                              request_status=1)
        return JsonResponse(context, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_transactions_by_date(filters, transaction_objects):
    try:
        start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
        if 'end_date' in filters.keys():
            end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
        else:
            end_date = start_date
        return transaction_objects.filter(transaction_date__range=(start_date, end_date))
    except:
        return transaction_objects.none()


def get_transactions_by_user(filters, transaction_objects):
    try:
        wallets = Wallet.objects.filter(user_id=filters['user_id'])
        transactions_in_wallet = transaction_objects.none()
        for wallet in wallets:
            transactions_in_wallet = transactions_in_wallet | (
                transaction_objects.filter(wallet_id=wallet.wallet_id))
        return transactions_in_wallet
    except:
        return transaction_objects.none()


def get_transactions_by_type(filters, transaction_objects):
    try:
        transaction_type = TransactionType.objects.get(type_name=filters['transaction_type']).type_id
        return transaction_objects.filter(transaction_type=transaction_type)
    except:
        return transaction_objects.none()


def get_transactions(filters):
    transaction_objects = Transaction.objects
    transactions = list()
    if 'start_date' in filters.keys():
        transaction_objects = get_transactions_by_date(filters, transaction_objects)
    if 'user_id' in filters.keys():
        transaction_objects = get_transactions_by_user(filters, transaction_objects)
    if 'transaction_type' in filters.keys():
        transaction_objects = get_transactions_by_type(filters, transaction_objects)
    for transaction_object in transaction_objects.all():
        transactions.append(TransactionSerializer(transaction_object).data)
    return transactions


def get_wallets(user_id):
    wallets = list()
    for wallet in Wallet.objects.filter(user_id=user_id):
        wallets.append({'wallet_id': wallet.wallet_id, 'current_balance': wallet.current_balance})
    return wallets


def get_current_balance(user_id, currency):
    wallet_id = get_hash_string(user_id, currency)
    current_balance = Wallet.objects.get(wallet_id=wallet_id).current_balance
    return current_balance


def get_currency_config():
    with open('wallet/currency_config.json') as config:
        data = json.load(config)
    return data