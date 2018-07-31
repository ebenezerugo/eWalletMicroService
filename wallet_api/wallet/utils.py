from hashlib import md5
from .metrics import *
from datetime import datetime
from .serializers import *
import json
from django.db import transaction
from rest_framework import status
from dateutil import parser
from django.core.paginator import Paginator


def get_context(**kwargs):
    return kwargs


def get_wallet_id(*args):
    text = ''
    for arg in args:
        text += arg
    return md5(text.encode()).hexdigest()


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


@track_runtime
@track_database
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


# ----------------------------------------------------------------------------------------------------------------------

@track_runtime
@track_database
def handle_allowed_currencies():
    currencies = CurrencySerializer(Currency.objects.filter(active=True).values('currency_name', 'currency_limit'),
                                    many=True).data
    return get_context(allowed_currencies=currencies, request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

def get_wallet_creation_data(data):
    serializer = UserAndCurrencySerializer(data=data)
    if serializer.is_valid():
        try:
            currency = Currency.objects.get(currency_name=data['currency'])
        except Exception as e:
            return get_context(error=str(e))
        if not currency.active:
            return get_context(error='This currency is not supported')
        data['currency_id'] = currency.currency_id
        data['wallet_id'] = get_wallet_id(data['user_id'], data['currency'])
        return data
    return get_context(error=serializer.errors)


@track_runtime
@track_database
def handle_create_wallet(data):
    data = get_wallet_creation_data(data)
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        # logging.info(data['error'])
        return context, status.HTTP_400_BAD_REQUEST
    serializer = WalletSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        context = get_context(wallet_id=serializer.data['wallet_id'], message='wallet created', request_status=1)
        return context, status.HTTP_201_CREATED
    # logging.info(serializer.errors)
    return serializer.errors, status.HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------------------------------------------------------------

def get_new_balance(balance, amount, transaction_type):
    if transaction_type == 'CREDIT':
        return balance + float(amount)
    if transaction_type == 'DEBIT':
        return balance - float(amount)


def get_transaction_data(data, transaction_type):
    serializer = TransactionDataSerializer(data=data)
    if serializer.is_valid():
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        try:
            wallet = Wallet.objects.get(pk=wallet_id)
        except Exception as e:
            return get_context(error=str(e))
        if not wallet.active:
            return get_context(error='Inactive wallet')
        data['wallet_id'] = wallet.wallet_id
        data['transaction_id'] = get_wallet_id(data['wallet_id'], str(
            data['transaction_amount']), )  # str(datetime.now())
        data['previous_balance'] = wallet.current_balance
        data['transaction_type'] = TransactionType.objects.get(type_name=transaction_type).type_id
        data['current_balance'] = get_new_balance(data['previous_balance'], data['transaction_amount'],
                                                  transaction_type)
        return data
    return get_context(error=serializer.errors)


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


@track_runtime
@track_database
def handle_transact(data, transaction_type):
    data = get_transaction_data(data, transaction_type)
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        return context, status.HTTP_400_BAD_REQUEST
    context = get_context(current_balance=data['previous_balance'], message='', request_status=0)
    if transaction_type == 'CREDIT':
        if check_limit(data['current_balance'], data['currency']):
            context['message'] = 'Credit failed due to currency limit'
            context['currency_limit'] = Currency.objects.get(currency_name=data['currency']).currency_limit
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
            if end_date < start_date:
                return transaction_objects.none()
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


def get_paginated_transactions(transaction_objects, page):
    paginator = Paginator(transaction_objects.all(), 10)
    paginated_transactions = paginator.get_page(page).object_list
    return TransactionDetailSerializer(paginated_transactions, many=True).data


def get_transactions(filters, page):
    transaction_objects = Transaction.objects

    if 'start_date' in filters.keys():
        transaction_objects = get_transactions_by_date(filters, transaction_objects)
    if 'user_id' in filters.keys():
        transaction_objects = get_transactions_by_user(filters['user_id'], transaction_objects)
    if 'transaction_type' in filters.keys():
        transaction_objects = get_transactions_by_type(filters['transaction_type'], transaction_objects)

    transactions = get_paginated_transactions(transaction_objects, page)

    return transactions


@track_runtime
@track_database
def handle_transactions_details(filters, page):
    curated_transactions = get_transactions(filters, page)
    if not len(curated_transactions):
        return get_context(message='Found ' + str(len(curated_transactions)) + ' transactions',
                           request_status=0), status.HTTP_200_OK
    else:
        return get_context(transactions=curated_transactions,
                           message='Found ' + str(len(curated_transactions)) + ' transactions',
                           request_status=1), status.HTTP_200_OK


# ----------------------------------------------------------------------------------------------------------------------

@track_runtime
@track_database
def handle_user_wallets(user_id):
    serializer = UserAndCurrencySerializer(data={'user_id': user_id, 'currency': 'All'})
    if serializer.is_valid():
        wallets = Wallet.objects.filter(user_id=user_id)

        serializer = WalletDetailSerializer(wallets, many=True)
        return get_context(wallets=serializer.data, message='Found ' + str(len(wallets)) + ' wallets',
                           request_status=1), status.HTTP_200_OK
    return get_context(error=serializer.errors, request_status=0), status.HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------------------------------------------------------------

@track_runtime
@track_database
def handle_current_balance_in_wallet(data):
    serializer = UserAndCurrencySerializer(data=data)
    if serializer.is_valid():
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        try:
            current_balance = Wallet.objects.get(wallet_id=wallet_id).current_balance
        except Exception as e:
            return get_context(error=str(e), request_status=0), status.HTTP_400_BAD_REQUEST
        return get_context(current_balance=current_balance, message='Retrieved current balance',
                           request_status=1), status.HTTP_200_OK
    return get_context(error=serializer.errors, request_status=0), status.HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------------------------------------------------------------


@track_runtime
@track_database
def handle_wallet_status(data, action):
    serializer = UserAndCurrencySerializer(data=data)
    if serializer.is_valid():
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        wallet = Wallet.objects.filter(wallet_id=wallet_id)
        if not len(list(wallet)):
            return get_context(message='wallet does not exist', request_status=0), status.HTTP_400_BAD_REQUEST
        if action == 'activate':
            wallet.update(active=True)
            return get_context(message='wallet has been activated', request_status=1), status.HTTP_200_OK
        elif action == 'deactivate':
            wallet.update(active=False)
            return get_context(message='wallet has been deactivated', request_status=1), status.HTTP_200_OK
        else:
            return get_context(message='action failed', request_status=0), status.HTTP_400_BAD_REQUEST
    return get_context(error=serializer.errors, request_status=0), status.HTTP_400_BAD_REQUEST

# ----------------------------------------------------------------------------------------------------------------------
