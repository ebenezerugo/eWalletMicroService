from django.test import TestCase
from .utils import *
from unittest import skip
from pprint import pprint


# @skip('completed')
class WalletIdTestCase(TestCase):

    def test_get_wallet_id(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        expected_output = 'cc1eee99782ffb59ae86facbd8fea9f0'
        actual_output = get_wallet_id(data['user_id'], data['currency'])
        self.assertEqual(actual_output, expected_output)


# @skip('completed')
class WalletCreationDataTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)

    def test_get_wallet_creation_data_positive(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        expected_output = get_wallet_id(data['user_id'], data['currency'])
        actual_output = get_wallet_creation_data(data)['wallet_id']
        self.assertEqual(actual_output, expected_output)

    def test_get_wallet_creation_data_invalid_currency(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': ''}
        actual_output = 'error' in get_wallet_creation_data(data).keys()
        self.assertEqual(actual_output, True)

    def test_get_wallet_creation_data_invalid_user_id(self):
        data = {'user_id': 54759, 'currency': 'INR'}
        actual_output = 'error' in get_wallet_creation_data(data).keys()
        self.assertEqual(actual_output, True)


# @skip('completed')
class CreateWalletTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)

    def test_handle_create_wallet_positive(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        expected_output = 201
        wallet_creation_data = get_wallet_creation_data(data)
        actual_output = handle_create_wallet(wallet_creation_data)[1]
        self.assertEqual(actual_output, expected_output)

    def test_handle_create_wallet_invalid_currency(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': ''}
        wallet_creation_data = get_wallet_creation_data(data)
        actual_output = handle_create_wallet(wallet_creation_data)
        request_status = actual_output[0]['request_status']
        response_status = actual_output[1]
        self.assertEqual(request_status, 0)
        self.assertEqual(response_status, 400)

    def test_handle_create_wallet_invalid_user_id(self):
        data = {'user_id': 54759, 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        actual_output = handle_create_wallet(wallet_creation_data)
        request_status = actual_output[0]['request_status']
        response_status = actual_output[1]
        self.assertEqual(request_status, 0)
        self.assertEqual(response_status, 400)


# @skip('completed')
class TransactionCreationDataTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')

    def test_get_transaction_data_credit_positive(self):
        data = {
            "user_id": "54759eb3c090d83409l2l889",
            "currency": "INR",
            "transaction_amount": 300.0,
            "source": "Android",
            "payment_id": "1234",
            "transaction_remarks": "deducting money"
        }
        transaction_type = 'credit'
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        expected_output = get_wallet_id(wallet_id, str(data['transaction_amount']))
        actual_output = get_transaction_data(data, transaction_type)['transaction_id']
        self.assertEqual(actual_output, expected_output)

    def test_get_transaction_data_debit_positive(self):
        data = {
            "user_id": "54759eb3c090d83409l2l889",
            "currency": "INR",
            "transaction_amount": 300,
            "source": "Android",
            "payment_id": "1234",
            "transaction_remarks": "deducting money"
        }
        transaction_type = 'credit'
        wallet_id = get_wallet_id(data['user_id'], data['currency'])
        expected_output = get_wallet_id(wallet_id, str(data['transaction_amount']))
        actual_output = get_transaction_data(data, transaction_type)['transaction_id']
        self.assertEqual(actual_output, expected_output)

    def test_get_transaction_data_invalid_amount(self):
        data = {
            "user_id": "54759eb3c090d83409l2l889",
            "currency": "INR",
            "transaction_amount": 'hello',
            "source": "Android",
            "payment_id": "1234",
            "transaction_remarks": "deducting money"
        }
        transaction_type = 'credit'
        actual_output = 'error' in get_transaction_data(data, transaction_type)
        self.assertEqual(actual_output, True)

    def test_get_transaction_data_invalid_user_id(self):
        data = {
            "user_id": 134,
            "currency": "INR",
            "transaction_amount": 300,
            "source": "Android",
            "payment_id": "1234",
            "transaction_remarks": "deducting money"
        }
        transaction_type = 'credit'
        actual_output = 'error' in get_transaction_data(data, transaction_type)
        self.assertEqual(actual_output, True)

    def test_get_transaction_data_invalid_currency(self):
        data = {
            "user_id": '54759eb3c090d83409l2l889',
            "currency": "",
            "transaction_amount": 300,
            "source": "Android",
            "payment_id": "1234",
            "transaction_remarks": "deducting money"
        }
        transaction_type = 'credit'
        actual_output = 'error' in get_transaction_data(data, transaction_type)
        self.assertEqual(actual_output, True)


# @skip('completed')
class MakeTransactionTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')

    def test_make_transaction_positive_credit(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 81,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_make_transaction_positive_debit(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 40,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "deducting money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_make_transaction_positive_null_source_payment_Id_remarks(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 82}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_make_transaction_invalid_user_id(self):
        data = {"user_id": "", "currency": "INR", "transaction_amount": 83,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(response_status, 400)

    def test_make_transaction_invalid_amount(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 'hello',
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(response_status, 400)

    def test_make_transaction_invalid_currency(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "", "transaction_amount": 85,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(response_status, 400)

    def test_make_transaction_invalid_transaction_type(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "", "transaction_amount": 85,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = ''
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = make_transaction(transaction_data, transaction_type)
        self.assertEqual(response_status, 400)


# @skip('completed')
class HandleTransactTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')

    def test_handle_transact_positive(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = handle_transact(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_transact_exceed_limit(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 1095,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = handle_transact(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 200)

    def test_handle_transact_insufficient_balance(self):
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 395,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        context, response_status = handle_transact(transaction_data, transaction_type)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 200)


# @skip('completed')
class TransactionsByDateTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 195,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 295,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_get_transactions_by_date_positive(self):
        filters = {"start_date": "2018-07-31"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_by_date_positive_date_format(self):
        filters = {"start_date": "2018/07/31"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_by_date_positive_start_and_end_date(self):
        filters = {"start_date": "2018-07-31", "end_date": "2018-07-31"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_by_date_positive_start_and_end_date_backdated(self):
        filters = {"start_date": "2018-07-31", "end_date": "2018-07-20"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_date_positive_start_and_end_date_format(self):
        filters = {"start_date": "2018/07/31", "end_date": "2018-jul-31"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_by_date_only_end_date(self):
        filters = {"end_date": "2018-jul-31"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_date_invalid_start_date(self):
        filters = {"start_date": "hello"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_date_invalid_end_date(self):
        filters = {"start_date": "2018/07/24", "end_date": "hello"}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_date_invalid_date_number(self):
        filters = {"start_date": "2018/07/24", "end_date": 44}
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_date(filters, transaction_objects)
        self.assertEqual(len(transactions), 0)


# @skip('completed')
class TransactionsByTypeTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 195,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 295,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_get_transactions_by_type_positive_credit(self):
        transaction_type = "CREDIT"
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_type(transaction_type, transaction_objects)
        self.assertEqual(len(transactions), 2)

    def test_get_transactions_by_type_positive_debit(self):
        transaction_type = "DEBIT"
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_type(transaction_type, transaction_objects)
        self.assertEqual(len(transactions), 1)

    def test_get_transactions_by_type_invalid_transaction_type(self):
        transaction_type = ""
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_type(transaction_type, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_type_invalid_transaction_type_number(self):
        transaction_type = 4
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_type(transaction_type, transaction_objects)
        self.assertEqual(len(transactions), 0)


# @skip('completed')
class TransactionsByUserTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 195,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 295,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_get_transactions_by_user_positive(self):
        user_id = '54759eb3c090d83409l2l889'
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_user(user_id, transaction_objects)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_by_user_no_transactions(self):
        user_id = '00059eb3c090d83409l2l000'
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_user(user_id, transaction_objects)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_by_user_invalid_user_id(self):
        user_id = 787
        transaction_objects = Transaction.objects
        transactions = get_transactions_by_user(user_id, transaction_objects)
        self.assertEqual(len(transactions), 0)


# @skip('completed')
class GetTransactionsTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 195,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 295,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_get_transactions_start_date(self):
        filters = {
            'start_date': '2018-07-31',
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_start_and_end_date(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_start_date_end_date_and_user_id(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_start_date_end_date_and_type(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'transaction_type': 'CREDIT'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 2)

    def test_get_transactions_start_date_end_date_user_id_and_type(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'transaction_type': 'DEBIT',
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 1)

    def test_get_transactions_user_id(self):
        filters = {
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 3)

    def test_get_transactions_user_id_and_type(self):
        filters = {
            'user_id': '54759eb3c090d83409l2l889',
            'transaction_type': 'DEBIT'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 1)

    def test_get_transactions_type(self):
        filters = {
            'transaction_type': 'DEBIT'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 1)

    def test_get_transactions_invalid_start_date(self):
        filters = {
            'start_date': '',
            'end_date': '2018-07-31',
            'transaction_type': 'DEBIT',
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_invalid_end_date(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '',
            'transaction_type': 'DEBIT',
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_invalid_transaction_type(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'transaction_type': '',
            'user_id': '54759eb3c090d83409l2l889'
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 0)

    def test_get_transactions_invalid_user_id(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'transaction_type': '',
            'user_id': ''
        }
        transactions = get_transactions(filters, 1)
        self.assertEqual(len(transactions), 0)


# @skip('completed')
class HandleTransactionDetailsTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)
        TransactionType.objects.create(type_name='CREDIT')
        TransactionType.objects.create(type_name='DEBIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 195,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 295,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 95,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'DEBIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_handle_transactions_details_positive(self):
        filters = {
            'start_date': '2018-07-31',
            'end_date': '2018-07-31',
            'transaction_type': 'DEBIT',
            'user_id': '54759eb3c090d83409l2l889'
        }
        context, response_status = handle_transactions_details(filters, 1)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_transactions_details_positive_no_filters(self):
        filters = {}
        context, response_status = handle_transactions_details(filters, 1)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_transactions_details_invalid_filters(self):
        filters = {
            'start_date': '',
            'end_date': '2018-07-31',
            'transaction_type': 'DEBIT',
            'user_id': '54759eb3c090d83409l2l889'
        }
        context, response_status = handle_transactions_details(filters, 1)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 200)


# @skip('completed')
class HandleUserWallets(TestCase):
    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'USD'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

    def test_handle_user_wallets_positive(self):
        user_id = '54759eb3c090d83409l2l889'
        context, response_status = handle_user_wallets(user_id)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_user_wallets_null_user_id(self):
        user_id = ''
        context, response_status = handle_user_wallets(user_id)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)

    def test_handle_user_wallets_invalid_user_id(self):
        user_id = 345
        context, response_status = handle_user_wallets(user_id)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)


# @skip('completed')
class HandleCurrentBalanceInWallet(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

    def test_handle_current_balance_in_wallet_positive(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        context, response_status = handle_current_balance_in_wallet(data)
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_current_balance_in_wallet_invalid_user_id(self):
        data = {'user_id': '', 'currency': 'INR'}
        context, response_status = handle_current_balance_in_wallet(data)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)

    def test_handle_current_balance_in_wallet_invalid_currency(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': ''}
        context, response_status = handle_current_balance_in_wallet(data)
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)


# @skip('completed')
class HandleAllowedCurrenciesTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

    def test_handle_allowed_currencies_positive(self):
        context, response_status = handle_allowed_currencies()
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_allowed_currencies_positive_list(self):
        context, response_status = handle_allowed_currencies()
        self.assertEqual(len(context['allowed_currencies']), 2)


# @skip('completed')
class HandleWalletStatusTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

    def test_handle_wallet_status_positive_activate(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        context, response_status = handle_wallet_status(data, 'deactivate')
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_wallet_status_positive_deactivate(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        context, response_status = handle_wallet_status(data, 'activate')
        self.assertEqual(context['request_status'], 1)
        self.assertEqual(response_status, 200)

    def test_handle_wallet_status_invalid_action(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        context, response_status = handle_wallet_status(data, '')
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)

    def test_handle_wallet_status_invalid_user_id(self):
        data = {'user_id': '', 'currency': 'INR'}
        context, response_status = handle_wallet_status(data, 'activate')
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)

    def test_handle_wallet_status_invalid_currency(self):
        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': ''}
        context, response_status = handle_wallet_status(data, 'activate')
        self.assertEqual(context['request_status'], 0)
        self.assertEqual(response_status, 400)


# @skip('completed')
class CurrencyObjectTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

    def test_get_currency_object_positive_INR(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        self.assertEqual(currency_object.currency_limit, 1000)

    def test_get_currency_object_positive_USD(self):
        currency_name = 'USD'
        currency_object = get_currency_object(currency_name)
        self.assertEqual(currency_object.currency_limit, 100)

    def test_get_currency_object_invalid_currency(self):
        currency_name = ''
        currency_object = get_currency_object(currency_name)
        self.assertEqual(currency_object, None)


# @skip('completed')
class CheckCurrencyStatusChangeTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'USD'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

    def test_check_currency_status_change_deactivate_INR(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = False
        active = False
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_status_change(wallets, currency_object, hard_reset, active,
                                               context, update_success)
        self.assertEqual(context['request_status'], 0)

    def test_check_currency_status_change_deactivate_USD(self):
        currency_name = 'USD'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = False
        active = False
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_status_change(wallets, currency_object, hard_reset, active,
                                               context, update_success)
        self.assertEqual(context['request_status'], 0)

    def test_check_currency_status_change_deactivate_hard_INR(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = True
        active = False
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_status_change(wallets, currency_object, hard_reset, active,
                                               context, update_success)
        self.assertEqual(context['request_status'], 1)

    def test_check_currency_status_change_deactivate_hard_USD(self):
        currency_name = 'USD'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = True
        active = False
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_status_change(wallets, currency_object, hard_reset, active,
                                               context, update_success)
        self.assertEqual(context['request_status'], 1)


# @skip('completed')
class CheckCurrencyLimitChangeTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

        TransactionType.objects.create(type_name='CREDIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 800,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_check_currency_limit_change_reduce_limit(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = False
        limit = 600
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_limit_change(wallets, currency_object, hard_reset, limit,
                                              context, update_success)
        self.assertEqual(context['request_status'], 0)

    def test_check_currency_limit_change_increase_limit(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = False
        limit = 1600
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_limit_change(wallets, currency_object, hard_reset, limit,
                                              context, update_success)
        self.assertEqual(context['request_status'], 1)

    def test_check_currency_limit_change_reduce_limit_hard(self):
        currency_name = 'INR'
        currency_object = get_currency_object(currency_name)
        wallets = Wallet.objects.filter(currency_id=currency_object.currency_id)
        hard_reset = True
        limit = 600
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = check_currency_limit_change(wallets, currency_object, hard_reset, limit,
                                              context, update_success)
        self.assertEqual(context['request_status'], 1)


# @skip('completed')
class ExistingCurrencyTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)

        data = {'user_id': '54759eb3c090d83409l2l889', 'currency': 'INR'}
        wallet_creation_data = get_wallet_creation_data(data)
        handle_create_wallet(wallet_creation_data)

        TransactionType.objects.create(type_name='CREDIT')
        data = {"user_id": "54759eb3c090d83409l2l889", "currency": "INR", "transaction_amount": 800,
                "source": "Android", "payment_id": "1234", "transaction_remarks": "adding money"}
        transaction_type = 'CREDIT'
        transaction_data = get_transaction_data(data, transaction_type)
        handle_transact(transaction_data, transaction_type)

    def test_existing_currency_reduce_limit(self):
        currency_item = {'currency_name': 'INR', 'limit': 600, 'active': True}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': False, 'status_hard': False}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_limit']['request_status'], 0)

    def test_existing_currency_reduce_limit_hard(self):
        currency_item = {'currency_name': 'INR', 'limit': 600, 'active': True}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': True, 'status_hard': False}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_limit']['request_status'], 1)

    def test_existing_currency_deactivate(self):
        currency_item = {'currency_name': 'INR', 'limit': 1000, 'active': False}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': False, 'status_hard': False}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_status']['request_status'], 0)

    def test_existing_currency_deactivate_hard(self):
        currency_item = {'currency_name': 'INR', 'limit': 1000, 'active': False}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': False, 'status_hard': True}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_status']['request_status'], 1)

    def test_existing_currency_reduce_limit_and_deactivate(self):
        currency_item = {'currency_name': 'INR', 'limit': 600, 'active': False}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': False, 'status_hard': False}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_status']['request_status'], 0)
        self.assertEqual(context[currency_item['currency_name']]['currency_limit']['request_status'], 0)

    def test_existing_currency_reduce_limit_and_deactivate_hard(self):
        currency_item = {'currency_name': 'INR', 'limit': 600, 'active': False}
        currency_object = get_currency_object(currency_item['currency_name'])
        update_success = get_context(message='Currency has been updated', request_status=1)
        data = {'limit_hard': True, 'status_hard': True}
        context = existing_currency(currency_object, currency_item, data, update_success)
        self.assertEqual(context[currency_item['currency_name']]['currency_status']['request_status'], 1)
        self.assertEqual(context[currency_item['currency_name']]['currency_limit']['request_status'], 1)


# @skip('completed')
class NewCurrencyTestCase(TestCase):

    def test_new_currency_positive(self):
        currency_item = {'currency_name': 'EUR', 'limit': 200, 'active': True}
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = new_currency(currency_item, context, update_success)
        self.assertEqual(context[currency_item['currency_name']]['request_status'], 1)

    def test_new_currency_invalid_limit(self):
        currency_item = {'currency_name': 'EUR', 'limit': 'sadasdsa', 'active': True}
        update_success = get_context(message='Currency has been updated', request_status=1)
        context = dict()
        context = new_currency(currency_item, context, update_success)
        self.assertEqual(context['request_status'], 0)


# @skip('completed')
class HandleUpdateCurrenciesTestCase(TestCase):

    def setUp(self):
        Currency.objects.create(currency_name='INR', currency_limit=1000, active=True)
        Currency.objects.create(currency_name='USD', currency_limit=100, active=True)

    def test_handle_update_currencies_positive(self):
        data = {'status_hard': False, 'limit_hard': False}
        context, response_status = handle_update_currencies(data)
        self.assertEqual(context['EUR']['request_status'], 1)
