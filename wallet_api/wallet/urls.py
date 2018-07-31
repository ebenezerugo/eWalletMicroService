from django.urls import path
from .views import *


urlpatterns = [
    path('create_wallet/', create_wallet, name='create_wallet'),
    path('credit/', transact, name='credit'),
    path('debit/', transact, name='debit'),
    path('transactions/', transactions, name='user_transactions'),
    path('user/wallets/', user_wallets, name='user_wallets'),
    path('user/balance/', current_balance_in_wallet, name='current_balance_in_wallet'),
    path('allowed_currencies/', allowed_currencies, name='currencies'),
    path('activate/', wallet_status, name='activate'),
    path('deactivate/', wallet_status, name='deactivate'),
    path('update_currencies/', update_currencies, name='update_currencies'),
    path('docs/', api_doc, name='api_doc'),
]
