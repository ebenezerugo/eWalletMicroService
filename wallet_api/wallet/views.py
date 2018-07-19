from django.views.decorators.csrf import csrf_exempt
from .serializers import *
from django.http import JsonResponse
from rest_framework import status
from .utils import *
from .models import *


@csrf_exempt
def create_wallet(request):
    if request.method == 'POST':
        data = get_wallet_creation_data(request)
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
def user_wallets(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        wallets = list()
        for wallet in Wallet.objects.filter(user_id=user_id):
            print(wallet.wallet_id, wallet.current_balance)
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
        wallet_id = request.GET.get('wallet_id')
        current_balance = Wallet.objects.get(wallet_id=wallet_id).current_balance
        context = {
            'current_balance': current_balance,
            'message': 'Retrieved current balance',
            'request_status': 1
        }
        return JsonResponse(context, status=status.HTTP_200_OK)


@csrf_exempt
def transactions(request):
    if request.method == 'POST':
        try:
            filters = JSONParser().parse(request)
        except:
            filters = dict()
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
        context = {'transactions': transactions}
        return JsonResponse(context, status=status.HTTP_200_OK)
