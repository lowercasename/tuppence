from app import app
from flask import render_template
from lib.auth import with_auth
from models.account import Account
from models.pot import Pot

@app.route('/')
@with_auth
def overview():
    a = Account.get_all()
    p = Pot.get_all()
    account_balance = 0
    pot_balance = 0
    for account in a:
        account_balance += account.balance
    for pot in p:
        pot_balance += pot.balance
    return render_template('overview.html', accounts=a, pots=p, account_balance=account_balance, pot_balance=pot_balance)
