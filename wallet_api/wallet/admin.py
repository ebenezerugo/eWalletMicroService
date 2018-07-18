from django.contrib import admin
from .models import *

admin.site.register(Currency)
admin.site.register(Wallet)
admin.site.register(TransactionType)
admin.site.register(Transaction)

