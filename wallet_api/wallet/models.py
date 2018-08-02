from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency_name = models.CharField(max_length=10)
    currency_limit = models.FloatField()
    active = models.BooleanField()

    def __str__(self):
        return self.currency_name


class Wallet(models.Model):
    currency_id = models.ForeignKey(Currency, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=24)
    wallet_id = models.CharField(max_length=32, primary_key=True)
    wallet_created_date_and_time = models.DateTimeField(default=timezone.now)
    current_balance = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.wallet_id

    class Meta:
        ordering = ('wallet_created_date_and_time',)


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=32, blank=True)
    source = models.CharField(max_length=100, blank=True)
    transaction_type = models.IntegerField()
    transaction_date = models.DateField(auto_now_add=True)
    transaction_time = models.TimeField(auto_now_add=True)
    previous_balance = models.FloatField()
    transaction_amount = models.FloatField(validators=[MinValueValidator(1)])
    current_balance = models.FloatField()
    transaction_remarks = models.TextField(blank=True)

    def __str__(self):
        return str(self.transaction_id)

    class Meta:
        ordering = ('transaction_date',)
