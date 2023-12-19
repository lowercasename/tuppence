from datetime import datetime
from app import app
from flask import render_template, request, redirect, session
from lib.auth import with_auth
from lib.server import validate_form_fields
from models.account import Account
from models.category import Category
from models.transaction import Transaction
from lib.strings import currency_string_to_database

@app.route('/transactions')
@with_auth
def transaction_list():
    month = request.args.get('m')
    year = request.args.get('y')
    a = Account.get_all()
    if month is not None and year is not None:
        try:
            t = Transaction.get_all(int(month), int(year))
            return render_template('transactions.html', transactions=t, accounts=a)
        except ValueError:
            pass
    now = datetime.now()
    t = Transaction.get_all(month=now.month, year=now.year)
    return render_template('transactions.html', transactions=t, accounts=a)

# Returns a table row for a single transaction
# TODO: Is this used?
@app.route('/transactions/<id>')
@with_auth
def transaction_get(id):
    t = Transaction.get_by_id(id)
    if t is None:
        return 404
    return render_template('transaction_single.html', transaction=t)

@app.route('/transactions/<id>', methods=['DELETE'])
@with_auth
def transaction_delete(id):
    Transaction.get_by_id(id).delete()
    return redirect('/transactions', code=303)

@app.route('/transactions', methods=['POST'])
@with_auth
def transaction_create():
    account_id, amount, sign, description, transfer_source_id, transfer_destination_id = validate_form_fields(
        ['account_id', 'amount', 'sign', 'description', 'transfer_source_id', 'transfer_destination_id']).values()
    amount = currency_string_to_database(amount)
    if sign == '-':
        amount = -amount
    else:
        amount = abs(amount)
    is_transfer = bool(request.form.get('is_transfer', False))
    user_id = session['user_id']
    category_names = [c.strip() for c in request.form.getlist('category_names')]
    print(category_names)

    if is_transfer:
        # We create two transactions, one for the source account and one for the destination account
        source_transaction = Transaction(user_id=user_id, account_id=transfer_source_id,
                                        amount=-amount, description=description, is_transfer=True,
                                        category_names=category_names)
        destination_transaction = Transaction(user_id=user_id, account_id=transfer_destination_id,
                                        amount=amount, description=description, is_transfer=True,
                                        category_names=category_names)
        source_transaction.save()
        destination_transaction.save()
    else:
        t = Transaction(user_id=user_id, account_id=account_id,
                        amount=amount, description=description, is_transfer=False,
                        category_names=category_names)
        t.save()
    return redirect('/transactions', code=303)


@app.route('/transactions/<id>', methods=['PUT'])
@with_auth
def transaction_update(id):
    account_id, amount, description = validate_form_fields(
        ['account_id', 'amount', 'description']).values()
    category_names = [c.strip() for c in request.form.getlist('category_names')]
    t = Transaction.get_by_id(id)
    t.update(account_id=account_id,
            amount=currency_string_to_database(amount), description=description,
            category_names=category_names)
    t.save()
    return redirect('/transactions', code=303)

# Returns an editable table row for a single transaction
@app.route('/transactions/<id>/editor', methods=['GET'])
@with_auth
def transaction_editor(id):
    t = Transaction.get_by_id(id)
    if t is None:
        return 404
    a = Account.get_all()
    return render_template('transaction_editor.html', transaction=t, accounts=a)

@app.route('/transactions/<id>/categories', methods=['GET'])
@with_auth
def transaction_categories(id):
    t = Transaction.get_by_id(id)
    if t is None:
        return 404
    return render_template('transaction_categories.html', transaction=t)

@app.route('/category/search', methods=['GET'])
@with_auth
def category_search():
    q = request.args.get('new_category')
    if q is None or q == '':
        return render_template('category_search.html', categories=[])
    c = Category.search(q)
    return render_template('category_search.html', categories=c)