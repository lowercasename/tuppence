from datetime import datetime
import json
from app import app
from flask import render_template, request
from lib.auth import with_auth
from lib.charts import balance_history, categories_by_month
from models.account import Account
from models.pot import Pot

@app.route('/')
@with_auth
def overview():
    month = request.args.get('m')
    year = request.args.get('y')
    month = int(month) if month is not None else None
    year = int(year) if year is not None else None
    if month is None or year is None:
        now = datetime.now()
        month = now.month
        year = now.year
    a = Account.get_all()
    p = Pot.get_all()
    account_balance = 0
    pot_balance = 0
    for account in a:
        account_balance += account.balance
    for pot in p:
        pot_balance += pot.balance
    balance_chart = json.dumps(balance_history(month, year))
    categories_chart = json.dumps(categories_by_month(month, year))
    return render_template('overview.html', accounts=a, pots=p, account_balance=account_balance, pot_balance=pot_balance, balance_chart=balance_chart, categories_chart=categories_chart)
