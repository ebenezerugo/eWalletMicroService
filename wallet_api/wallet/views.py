from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.parsers import JSONParser
from .utils import *
from django.http import JsonResponse


@require_http_methods(['POST'])
@csrf_exempt
def create_wallet(request):
    data = get_wallet_creation_data(JSONParser().parse(request))
    context, response_status = handle_create_wallet(data)
    return JsonResponse(context, status=response_status)


@require_http_methods(['PUT'])
@csrf_exempt
def transact(request):
    transaction_type = str(request.get_full_path().split('/')[-2]).upper()
    data = JSONParser().parse(request)
    context, response_status = handle_transact(data, transaction_type)
    return JsonResponse(context, status=response_status)


@require_http_methods(['POST'])
@csrf_exempt
def transactions(request):
    filters = JSONParser().parse(request)
    context, response_status = handle_transactions_details(filters)
    return JsonResponse(context, status=response_status)


@require_http_methods(['GET'])
@csrf_exempt
def user_wallets(request):
    user_id = request.GET.get('user_id')
    context, response_status = handle_user_wallets(user_id)
    return JsonResponse(context, status=response_status)


@require_http_methods(['GET'])
@csrf_exempt
def current_balance_in_wallet(request):
    user_id = request.GET.get('user_id')
    currency = request.GET.get('currency')
    context, response_status = handle_current_balance_in_wallet(user_id, currency)
    return JsonResponse(context, status=response_status)


@require_http_methods(['GET'])
@csrf_exempt
def allowed_currencies(request):
    context, response_status = handle_allowed_currencies()
    return JsonResponse(context, status=response_status)


@require_http_methods(['PUT'])
@csrf_exempt
def wallet_status(request):
    data = JSONParser().parse(request)
    action = str(request.get_full_path().split('/')[-2])
    context, response_status = handle_wallet_status(data['user_id'], data['currency'], action)
    return JsonResponse(context, status=response_status)


@require_http_methods(['PUT'])
@csrf_exempt
def update_currencies(request):
    data = JSONParser().parse(request)
    context, response_status = handle_update_currencies(data)
    return JsonResponse(context, status=response_status)
