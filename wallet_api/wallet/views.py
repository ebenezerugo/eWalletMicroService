from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.parsers import JSONParser
from .utils import *


@require_http_methods(['POST'])
@csrf_exempt
def create_wallet(request):
    data = get_wallet_creation_data(JSONParser().parse(request))
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)
    serializer = WalletSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        context = get_context(wallet_id=serializer.data['wallet_id'], message='wallet_created', request_status=0)
        return JsonResponse(context, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_http_methods(['PUT'])
@csrf_exempt
def transact(request):
    transaction_type = str(request.get_full_path().split('/')[-2]).upper()
    data = get_transaction_data(JSONParser().parse(request), transaction_type)
    if 'error' in data.keys():
        context = get_context(message=data['error'], request_status=0)
        return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)
    context = get_context(current_balance=data['previous_balance'], message='', request_status=0)
    if transaction_type == 'CREDIT':
        if check_limit(data):
            context['message'] = 'Credit failed due to currency limit'
            return JsonResponse(context, status=status.HTTP_200_OK)
    elif transaction_type == 'DEBIT':
        if data['current_balance'] < 0:
            context['message'] = 'Debit failed due to insufficient funds'
            return JsonResponse(context, status=status.HTTP_200_OK)
    return make_transaction(data, transaction_type)


@require_http_methods(['POST'])
@csrf_exempt
def transactions(request):
    filters = JSONParser().parse(request)
    curated_transactions = get_transactions(filters)
    context = get_context(transactions=curated_transactions,
                          message='Found ' + str(len(curated_transactions)) + ' transactions', request_status=1)
    return JsonResponse(context, status=status.HTTP_200_OK)


@require_http_methods(['GET'])
@csrf_exempt
def user_wallets(request):
    user_id = request.GET.get('user_id')
    wallets = get_wallets(user_id)
    context = get_context(wallets=wallets, message='Found ' + str(len(wallets)) + ' wallets', request_status=1)
    return JsonResponse(context, status=status.HTTP_200_OK)


@require_http_methods(['GET'])
@csrf_exempt
def current_balance_in_wallet(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        currency = request.GET.get('currency')
        current_balance = get_current_balance(user_id, currency)
        context = get_context(current_balance=current_balance, message='Retrieved current balance', request_status=1)
        return JsonResponse(context, status=status.HTTP_200_OK)


@require_http_methods(['GET'])
@csrf_exempt
def allowed_currencies(request):
    currencies = list(Currency.objects.values_list('currency_name', flat=True))
    context = get_context(allowed_currencies=currencies)
    return JsonResponse(context, status=status.HTTP_200_OK)


@require_http_methods(['PUT'])
@csrf_exempt
def wallet_status(request):
    data = JSONParser().parse(request)
    wallet_id = get_hash_string(data['user_id'], data['currency'])
    action = str(request.get_full_path().split('/')[-2])
    if action == 'activate':
        Wallet.objects.filter(wallet_id=wallet_id).update(active=True)
        context = get_context(message='wallet has been activated', request_status=1)
    elif action == 'deactivate':
        Wallet.objects.filter(wallet_id=wallet_id).update(active=False)
        context = get_context(message='wallet has been deactivated', request_status=1)
    else:
        context = get_context(message='action failed', request_status=0)
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
                try:
                    currency_object = Currency.objects.get(currency_name=currency_item['currency_name'])
                except:
                    currency_object = None
                print(currency_object)
                if currency_object:
                    wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)

                    if currency_item['active'] != currency_object.active:
                        if not wallets.count() or data['status_hard']:
                            currency_object.active = bool(currency_item['active'])
                            currency_object.save()
                        else:
                            context = dict()
                            context['currency_status'] = {
                                'message': 'Existing wallets of users listed maybe affected due to currency status',
                                'users': list(wallets.values()),
                                'request_status': 0
                            }

                    if currency_item['limit'] != currency_object.currency_limit:
                        wallets = wallets.filter(current_balance__gt=currency_item['limit'])
                        if not wallets.count() or data['limit_hard']:
                            currency_object.currency_limit = currency_item['limit']
                            currency_object.save()
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
