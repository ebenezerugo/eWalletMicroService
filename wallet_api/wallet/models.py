from django.db import models


class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency_name = models.CharField(max_length=100)

    def __str__(self):
        return self.currency_name


class Wallet(models.Model):
    currency_id = models.ForeignKey(Currency, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=24)
    wallet_id = models.CharField(max_length=32, primary_key=True)
    wallet_created_date_and_time = models.DateTimeField()
    current_balance = models.FloatField()

    def __str__(self):
        return self.wallet_id

    class Meta:
        ordering = ('wallet_created_date_and_time',)


class TransactionType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.type_name


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=32, primary_key=True)
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=32)
    source = models.CharField(max_length=100)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    transaction_time = models.TimeField()
    previous_balance = models.FloatField()
    transaction_amount = models.FloatField()
    current_balance = models.FloatField()
    transaction_remarks = models.TextField()

    def __str__(self):
        return self.transaction_id
