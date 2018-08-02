from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.parsers import JSONParser
from .utils import *
from django.http import JsonResponse
from django.shortcuts import render


@track_runtime
@track_database
@require_http_methods(['POST'])
@csrf_exempt
def create_wallet(request):
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    context, response_status = handle_create_wallet(data)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['PUT'])
@csrf_exempt
def transact(request):
    transaction_type = str(request.get_full_path().split('/')[-2]).upper()
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    context, response_status = handle_transact(data, transaction_type)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['POST'])
@csrf_exempt
def transactions(request):
    try:
        filters = JSONParser().parse(request)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    page = request.GET.get('page')
    context, response_status = handle_transactions_details(filters, page)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['GET'])
@csrf_exempt
def user_wallets(request):
    user_id = request.GET.get('user_id')
    context, response_status = handle_user_wallets(user_id)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['GET'])
@csrf_exempt
def current_balance_in_wallet(request):
    data = {'user_id': request.GET.get('user_id'), 'currency': request.GET.get('currency')}
    context, response_status = handle_current_balance_in_wallet(data)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['GET'])
@csrf_exempt
def allowed_currencies(request):
    context, response_status = handle_allowed_currencies()
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['PUT'])
@csrf_exempt
def wallet_status(request):
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    action = str(request.get_full_path().split('/')[-2])
    context, response_status = handle_wallet_status(data, action)
    return JsonResponse(context, status=response_status)


@track_runtime
@track_database
@require_http_methods(['PUT'])
@csrf_exempt
def update_currencies(request):
    try:
        data = JSONParser().parse(request)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    context, response_status = handle_update_currencies(data)
    print(context)
    return JsonResponse(context, status=response_status, safe=False)


def api_doc(request):
    return render(request, 'wallet/doc.html')
