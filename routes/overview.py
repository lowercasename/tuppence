from datetime import datetime
import json

from app import app
from dateutil import relativedelta
from flask import render_template, request
from lib.auth import with_auth
from lib.charts import balance_history, categories_by_month
from lib.date import validate_month, validate_year
from models.account import Account
from models.pot import Pot
from models.transaction import Transaction

@app.route('/')
@with_auth
def overview():
    month = validate_month(request.args.get('m'))
    year = validate_year(request.args.get('y'))
    a = Account.get_all()
    p = Pot.get_all()
    t = Transaction.get_all(month, year)
    account_balance = 0
    pot_balance = 0
    for account in a:
        account_balance += account.balance
    for pot in p:
        pot_balance += pot.balance
    month_expenses = 0
    month_income = 0
    month_balance = 0
    for transaction in t:
        if transaction.amount > 0:
            month_income += transaction.amount
        else:
            month_expenses += transaction.amount 
    month_balance = month_income + month_expenses
    month_expenses = abs(month_expenses)
    balance_chart = json.dumps(balance_history(month, year))
    categories_chart = json.dumps(categories_by_month(month, year))
    last_year_categories_chart = json.dumps(categories_by_month(month, year - 1))
    current_datetime = datetime.strptime(f'{year}-{month}', '%Y-%m')
    last_month = current_datetime - relativedelta.relativedelta(months=1)
    last_month_categories_chart = json.dumps(categories_by_month(last_month.month, last_month.year))
    return render_template('overview.html',
                            accounts=a,
                            pots=p,
                            account_balance=account_balance,
                            pot_balance=pot_balance,
                            balance_chart=balance_chart,
                            categories_chart=categories_chart,
                            last_year_categories_chart=last_year_categories_chart,
                            last_month_categories_chart=last_month_categories_chart,
                            month_expenses=month_expenses,
                            month_income=month_income,
                            month_balance=month_balance
                        )
