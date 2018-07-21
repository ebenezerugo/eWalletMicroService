from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from .utils import *
from django.db import transaction


@csrf_exempt
def create_wallet(request):
    if request.method == 'POST':
        data = get_wallet_creation_data(request)
        if 'error' in data.keys():
            context = {
                'message': data['error'],
                'request_status': 0
            }
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)
        serializer = WalletSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            context = {
                'wallet_id': serializer.data['wallet_id'],
                'message': 'Wallet created',
                'requestStatus': 1
            }
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def credit(request):
    if request.method == 'PUT':
        data = get_transaction_data(request)
        if 'error' in data.keys():
            context = {
                'message': data['error'],
                'request_status': 0
            }
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)
        data['current_balance'] = data['previous_balance'] + data['transaction_amount']
        data['transaction_type'] = TransactionType.objects.get(type_name='CREDIT').type_id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            Wallet.objects.filter(wallet_id=data['wallet_id']).update(current_balance=data['current_balance'])
            context = {
                'current_balance': data['current_balance'],
                'message': 'Credit successful',
                'request_status': 1
            }
            return JsonResponse(context, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def debit(request):
    if request.method == 'PUT':
        data = get_transaction_data(request)
        if 'error' in data.keys():
            context = {
                'message': data['error'],
                'request_status': 0
            }
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)
        context = {
            'current_balance': data['previous_balance'],
            'message': 'Debit failed due to insufficient funds',
            'request_status': 0
        }
        data['current_balance'] = data['previous_balance'] - data['transaction_amount']
        if data['current_balance'] < 0:
            return JsonResponse(context, status=status.HTTP_200_OK)
        data['transaction_type'] = TransactionType.objects.get(type_name='DEBIT').type_id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            Wallet.objects.filter(wallet_id=data['wallet_id']).update(current_balance=data['current_balance'])
            context['current_balance'] = data['current_balance']
            context['message'] = "Debit successful"
            context['request_status'] = 1
            return JsonResponse(context, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def transactions(request):
    if request.method == 'POST':
        try:
            filters = JSONParser().parse(request)
        except:
            filters = dict()
        curated_transactions = get_transactions(filters)
        context = {
            'transactions': curated_transactions,
            'message': 'Found ' + str(len(curated_transactions)) + ' transactions',
            'request_status': 1
        }
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def user_wallets(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        wallets = list()
        for wallet in Wallet.objects.filter(user_id=user_id):
            wallets.append({
                'wallet_id': wallet.wallet_id,
                'current_balance': wallet.current_balance
            })
        context = {
            'wallets': wallets,
            'message': 'Found ' + str(len(wallets)) + ' wallets',
            'request_status': 1
        }
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def current_balance_in_wallet(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        currency = request.GET.get('currency')
        wallet_id = get_hash_string(user_id, currency)
        current_balance = Wallet.objects.get(wallet_id=wallet_id).current_balance
        context = {
            'current_balance': current_balance,
            'message': 'Retrieved current balance',
            'request_status': 1
        }
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def allowed_currencies(request):
    if request.method == 'GET':
        currencies = list(Currency.objects.values_list('currency_name', flat=True))
        context = {'allowed_currencies': currencies}
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def wallet_status(request):
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        wallet_id = get_hash_string(data['user_id'], data['currency'])
        action = str(request.get_full_path().split('/')[-2])
        if action == 'activate':
            Wallet.objects.filter(wallet_id=wallet_id).update(active=True)
            context = {
                'message': 'wallet has been activated',
                'request_status': 1
            }
        elif action == 'deactivate':
            Wallet.objects.filter(wallet_id=wallet_id).update(active=True)
            context = {
                'message': 'wallet has been deactivated',
                'request_status': 1
            }
        else:
            context = {
                'message': 'action failed',
                'request_status': 0
            }
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def update_currencies(request):
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        currencies = get_currency_config()
        context = {
            'message': 'Currencies have been updated',
            'request_status': 1
        }
        with transaction.atomic():
            for currency_item in currencies:
                currency_object = Currency.objects.filter(currency_name=currency_item['currency_name'])
                if currency_object.exists():
                    wallets = Wallet.objects.filter(currency_id=currency_object[0].currency_id)

                    if currency_item['active'] != currency_object[0].active:
                        if not wallets.count() or data['status_hard']:
                            currency_object.update(active=bool(currency_item['active']))
                        else:
                            context = dict()
                            context['currency_status'] = {
                                'message': 'Existing wallets of users listed maybe affected due to currency status',
                                'users': list(wallets.values()),
                                'request_status': 0
                            }

                    if currency_item['limit'] != currency_object[0].currency_limit:
                        wallets = wallets.filter(current_balance__gt=currency_item['limit'])
                        if not wallets.count() or data['limit_hard']:
                            currency_object.update(currency_limit=currency_item['limit'])
                        else:
                            context = dict()
                            context['currency_limit'] = {
                                'message': 'Existing wallets of users listed maybe affected due to limit',
                                'users': list(wallets.values()),
                                'request_status': 0
                            }
                else:
                    currency = Currency(currency_name=currency_item['currency_name'],
                                        currency_limit=currency_item['limit'],
                                        active=bool(currency_item['active']))
                    currency.save()
            return JsonResponse(context, status=status.HTTP_200_OK)
