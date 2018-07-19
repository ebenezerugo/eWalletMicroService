from django.urls import path
from .views import *


urlpatterns = [
    path('create_wallet/', create_wallet, name='create_wallet'),
    path('credit/', credit, name='credit'),
    path('debit/', debit, name='debit'),
    path('transactions/', transactions, name='user_transactions'),
    path('user/wallets/', user_wallets, name='user_wallets'),
    path('user/balance/', current_balance_in_wallet, name='current_balance_in_wallet'),
]
