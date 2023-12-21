from datetime import datetime
import json
from app import app
from flask import render_template, request
from lib.auth import with_auth
from lib.charts import balance_history, categories_by_month
from lib.date import validate_month, validate_year
from models.account import Account
from models.pot import Pot

@app.route('/')
@with_auth
def overview():
    month = validate_month(request.args.get('m'))
    year = validate_year(request.args.get('y'))
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
