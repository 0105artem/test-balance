"""
=============================================
        HTTP Bad Responses Exceptions
=============================================
"""


class UserNotFound(Exception):
    def __init__(self, user_id):
        self.user_id = user_id

    def __str__(self):
        return f"User with id {self.user_id} not found!"


class UserAlreadyExists(Exception):
    def __init__(self, name):
        self.user_name = name

    def __str__(self):
        return f"User with name {self.user_name} already exists!"


class BalanceNotFound(Exception):
    def __init__(self, date):
        self.date = date

    def __str__(self):
        return f"No balance found for date {self.date}!"


class TransactionNotFound(Exception):
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return f"Transaction with id {self.transaction_id} not found!"


class InsufficientFunds(Exception):
    def __str__(self):
        return "Insufficient funds!"


class UnknownTransactionType(Exception):
    def __str__(self):
        return "Invalid transaction type!"


class TransactionAlreadyExists(Exception):
    def __init__(self, uid):
        self.uid = uid

    def __str__(self):
        return f"Transaction with id {self.uid} already exists!"


"""
=============================================
            Users Models Exceptions
=============================================
"""
class UserIdRequired(Exception):
    def __str__(self):
        return f"User id required for this method!"


class UserNameRequired(Exception):
    def __str__(self):
        return f"User name required for this method!"

