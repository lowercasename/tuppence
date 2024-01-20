from calendar import monthrange
from datetime import datetime

from models.account import Account
from models.transaction import Transaction

def balance_history(month: int, year: int):
    """Returns a list of balances for each day in the given month and year"""
    now = datetime.now()
    if month is None or year is None:
        month = now.month
        year = now.year
    days_in_month = monthrange(year, month)[1]
    accounts = Account.get_all(show_archived=False)
    accounts_balances = [{
        'name': a.name,
        'balances': [],
        'days_in_month': days_in_month,
    } for a in accounts]
    transactions_for_month = Transaction.get_all(month, year)
    for day in range(1, days_in_month + 1):
        for i, account in enumerate(accounts_balances):
            if day > now.day and month == now.month and year == now.year:
                continue
            balance = accounts[i].balance
            if len(transactions_for_month) == 0 or transactions_for_month[-1].date is None:
                continue
            # If there are no transactions before this day, we set the balance to 0
            if len(transactions_for_month) > 0 and transactions_for_month[-1].date.day > day:
                balance = 0
            else:
                for transaction in transactions_for_month:
                    if transaction.date is None:
                        continue
                    if transaction.account_id == accounts[i].id and transaction.date and transaction.date.day > day:
                        balance -= transaction.amount
            account['balances'].append(balance)

    return accounts_balances 

def categories_by_month(month: int, year: int):
    """Returns a list of categories and their amounts for the given month and year"""
    now = datetime.now()
    if month is None or year is None:
        month = now.month
        year = now.year
    transactions_for_month = Transaction.get_all(month, year)
    category_names = []
    for transaction in transactions_for_month:
        if transaction.category_names is None:
            continue
        for category in transaction.category_names:
            if category not in category_names:
                category_names.append(category)
    categories = [{
        'name': c,
        'amount': 0
    } for c in category_names]
    for transaction in transactions_for_month:
        for i, category in enumerate(categories):
            if category['name'] in transaction.category_names:
                categories[i]['amount'] += transaction.amount

    return categories
    
    