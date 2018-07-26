from hashlib import md5
from datetime import datetime
from .serializers import *
import json
from django.db import transaction
from rest_framework import status
from dateutil import parser
from pprint import pprint

CONSTANTS = {
    'WALLET_INITIAL_STATUS': True,
    'WALLET_INITIAL_BALANCE': 0.0,
}


def get_wallet_id(*args):
    text = ''
    for arg in args:
        text += arg
    return md5(text.encode()).hexdigest()


def get_context(**kwargs):
    return kwargs


# ----------------------------------------------------------------------------------------------------------------------

def get_wallet_creation_data(data):
    try:
        if data['user_id'] == "" or not isinstance(data['user_id'], str):
            return get_context(error='Invalid user ID')
        currency = Currency.objects.get(currency_name=data['currency'])
        if not currency.active:
            return get_context(error='This currency is not supported')
        data['currency_id'] = currency.currency_id
    except Exception as e:
        return get_context(error=str(e))
    data['wallet_created_date_and_time'] = datetime.now()
    data['wallet_id'] = get_wallet_id(data['user_id'], data['currency'])
    data['active'] = CONSTANTS['WALLET_INITIAL_STATUS']
    data['current_balance'] = CONSTANTS['WALLET_INITIAL_BALANCE']
    return data


def handle_create_wallet(data):
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        return context, status.HTTP_400_BAD_REQUEST
    serializer = WalletSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        context = get_context(wallet_id=serializer.data['wallet_id'], message='wallet created', request_status=1)
        return context, status.HTTP_201_CREATED
    return serializer.errors, status.HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------------------------------------------------------------


def get_new_balance(balance, amount, transaction_type):
    if transaction_type == 'CREDIT':
        return balance + amount
    if transaction_type == 'DEBIT':
        return balance - amount


def get_transaction_data(data, transaction_type):
    try:
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        wallet = Wallet.objects.get(wallet_id=wallet_id)

        if not wallet.active:
            return get_context(error='Inactive wallet')

        if not isinstance(data['transaction_amount'], int) and not isinstance(data['transaction_amount'], float):
            return get_context(error='Invalid transaction amount')

        data['wallet_id'] = wallet.wallet_id
        data['transaction_id'] = get_wallet_id(data['wallet_id'], str(
            data['transaction_amount']))  # str(datetime.now())
        data['transaction_date'] = datetime.now().date()
        data['transaction_time'] = datetime.now().time()
        data['previous_balance'] = Wallet.objects.get(wallet_id=data['wallet_id']).current_balance
        data['transaction_type'] = TransactionType.objects.get(type_name=transaction_type).type_id
        data['current_balance'] = get_new_balance(data['previous_balance'], data['transaction_amount'],
                                                  transaction_type)
        return data
    except Exception as e:
        return get_context(error=str(e))


def check_limit(balance, currency):
    limit = Currency.objects.get(currency_name=currency).currency_limit
    if balance > limit:
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
        return context, status.HTTP_200_OK
    return serializer.errors, status.HTTP_400_BAD_REQUEST


def handle_transact(data, transaction_type):
    data = get_transaction_data(data, transaction_type)
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        return context, status.HTTP_400_BAD_REQUEST
    context = get_context(current_balance=data['previous_balance'], message='', request_status=0)
    if transaction_type == 'CREDIT':
        if check_limit(data['current_balance'], data['currency']):
            context['message'] = 'Credit failed due to currency limit'
            return context, status.HTTP_200_OK
    elif transaction_type == 'DEBIT':
        if data['current_balance'] < 0:
            context['message'] = 'Debit failed due to insufficient funds'
            return context, status.HTTP_200_OK
    context, response_status = make_transaction(data, transaction_type)
    return context, response_status


# ----------------------------------------------------------------------------------------------------------------------


def get_transactions_by_date(filters, transaction_objects):
    try:
        start_date = parser.parse(filters['start_date']).date()
        if 'end_date' in filters.keys():
            end_date = parser.parse(filters['end_date']).date()
        else:
            end_date = start_date
        return transaction_objects.filter(transaction_date__range=(start_date, end_date))
    except:
        return transaction_objects.none()


def get_transactions_by_user(user_id, transaction_objects):
    try:
        wallets = Wallet.objects.filter(user_id=user_id)
        transactions_in_wallet = transaction_objects.none()
        for wallet in wallets:
            transactions_in_wallet = transactions_in_wallet | (
                transaction_objects.filter(wallet_id=wallet.wallet_id))
        return transactions_in_wallet
    except:
        return transaction_objects.none()


def get_transactions_by_type(transaction_type, transaction_objects):
    try:
        transaction_type = TransactionType.objects.get(type_name=transaction_type).type_id
        return transaction_objects.filter(transaction_type=transaction_type)
    except:
        return transaction_objects.none()


def get_transactions(filters):
    transaction_objects = Transaction.objects
    transactions = list()
    if 'start_date' in filters.keys():
        transaction_objects = get_transactions_by_date(filters, transaction_objects)
    if 'user_id' in filters.keys():
        transaction_objects = get_transactions_by_user(filters['user_id'], transaction_objects)
    if 'transaction_type' in filters.keys():
        transaction_objects = get_transactions_by_type(filters['transaction_type'], transaction_objects)
    for transaction_object in transaction_objects.all():
        transactions.append(TransactionSerializer(transaction_object).data)
    return transactions


def handle_transactions_details(filters):
    curated_transactions = get_transactions(filters)
    if not len(curated_transactions):
        return get_context(message='Found ' + str(len(curated_transactions)), request_status=0), status.HTTP_200_OK
    else:
        return get_context(transactions=curated_transactions,
                           message='Found ' + str(len(curated_transactions)) + ' transactions',
                           request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

def handle_user_wallets(user_id):
    if user_id == '' or isinstance(user_id, int):
        return get_context(message='Invalid user ID', request_status=0), status.HTTP_400_BAD_REQUEST
    wallets = list(Wallet.objects.filter(user_id=user_id).values('wallet_id', 'current_balance', 'currency_id'))
    return get_context(wallets=wallets, message='Found ' + str(len(wallets)) + ' wallets',
                       request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

def handle_current_balance_in_wallet(user_id, currency):
    wallet_id = get_wallet_id(user_id, currency)
    try:
        current_balance = Wallet.objects.get(wallet_id=wallet_id).current_balance
    except Exception as e:
        return get_context(error=str(e), request_status=0), status.HTTP_400_BAD_REQUEST
    return get_context(current_balance=current_balance, message='Retrieved current balance',
                       request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

def handle_allowed_currencies():
    currencies = list(Currency.objects.values_list('currency_name', flat=True))
    return get_context(allowed_currencies=currencies, request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

def handle_wallet_status(user_id, currency, action):
    wallet_id = get_wallet_id(user_id, currency)
    try:
        if action == 'activate':
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            wallet.active = True
            wallet.save()
            return get_context(message='wallet has been activated', request_status=1), status.HTTP_200_OK
        elif action == 'deactivate':
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            wallet.active = False
            wallet.save()
            return get_context(message='wallet has been deactivated', request_status=1), status.HTTP_200_OK
        else:
            return get_context(message='action failed', request_status=0), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return get_context(error=str(e), request_status=0), status.HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------------------------------------------------------------

def get_currency_config():
    with open('wallet/currency_config.json') as config:
        data = json.load(config)
    return data


def get_currency_object(currency_name):
    try:
        currency_object = Currency.objects.get(currency_name=currency_name)
    except:
        currency_object = None
    return currency_object


def check_currency_status_change(wallets, currency_object, hard_reset, active_status, context, update_success):
    if not wallets.count() or hard_reset:
        currency_object.active = bool(active_status)
        currency_object.save()
        return update_success
    else:
        return get_context(message='Existing wallets of users listed maybe affected due to currency status',
            users=list(wallets.values()), request_status=0)


def check_currency_limit_change(wallets, currency_object, hard_reset, limit, context, update_success):
    wallets = wallets.filter(current_balance__gt=limit)
    if not wallets.count() or hard_reset:
        currency_object.currency_limit = limit
        currency_object.save()
        return update_success
    else:
        return get_context(message='Existing wallets of users listed maybe affected due to limit',
            users=list(wallets.values()), request_status=0)


def existing_currency(currency_object, currency_item, data, update_success):
    wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
    context = {str(currency_object): dict()}
    if currency_item['active'] != currency_object.active:
        context[str(currency_object)].update(
            currency_status=check_currency_status_change(wallets, currency_object, data['status_hard'],
                                                         currency_item['active'],
                                                         context, update_success))
    if currency_item['limit'] != currency_object.currency_limit:
        context[str(currency_object)].update(
            currency_limit=check_currency_limit_change(wallets, currency_object, data['limit_hard'],
                                                       currency_item['limit'],
                                                       context, update_success))
    return context


def new_currency(currency_item, context, update_success):
    currency_item['currency_limit'] = currency_item['limit']
    serializer = CurrencySerializer(data=currency_item)
    if serializer.is_valid():
        serializer.save()
        context[currency_item['currency_name']] = update_success
        return context
    return get_context(error=serializer.errors, currency=currency_item['currency_name'], request_status=0)


def handle_update_currencies(data):
    currencies = get_currency_config()
    update_success = get_context(message='Currency has been updated', request_status=1)
    context = dict()
    with transaction.atomic():
        for currency_item in currencies:
            currency_object = get_currency_object(currency_item['currency_name'])
            if currency_object:
                context.update(existing_currency(currency_object, currency_item, data, update_success))
            else:
                new_currency_context = new_currency(currency_item, context, update_success)
                if 'error' in new_currency_context.keys():
                    return new_currency_context, status.HTTP_400_BAD_REQUEST
                context.update(new_currency_context)
        return context, status.HTTP_200_OK
