from flask import render_template, request, redirect, session
from app import app
from lib.auth import with_auth
from lib.server import validate_form_fields
from models.account import Account
from lib.strings import currency_string_to_database

@app.route('/accounts')
@with_auth
def account_list():
    a = Account.get_all()
    return render_template('accounts.html', accounts=a)


@app.route('/accounts/<id>')
@with_auth
def account_get(id):
    a = Account.get_by_id(id)
    if a is None:
        return 404
    return render_template('account_single.html', account=a)


@app.route('/accounts/<id>', methods=['DELETE'])
@with_auth
def account_delete(id):
    Account.get_by_id(id).delete()
    return redirect('/accounts', code=303)


@app.route('/accounts', methods=['POST'])
@with_auth
def account_create():
    name, balance, notes = validate_form_fields(['name', 'balance', 'notes']).values()
    user_id = session['user_id']
    a = Account(user_id=user_id, name=name, balance=currency_string_to_database(balance), notes=notes, sort_order=0)
    a.save()
    return redirect('/accounts', code=303)


@app.route('/accounts/<id>', methods=['PUT'])
@with_auth
def account_update(id):
    name, balance, notes = validate_form_fields(['name', 'balance', 'notes']).values()
    a = Account.get_by_id(id)
    a.update(name=name, balance=currency_string_to_database(balance), notes=notes)
    a.save()
    return redirect('/accounts', code=303)

# Returns an editable table row for a single account
@app.route('/accounts/<id>/editor', methods=['GET'])
@with_auth
def account_editor(id):
    a = Account.get_by_id(id)
    if a is None:
        return 404
    print(a)
    return render_template('account_editor.html', account=a)

@app.route('/accounts/reorder', methods=['POST'])
@with_auth
def account_reorder():
    order = request.get_json()
    if len(order) == 0:
        return '', 200
    for i in range(len(order)):
        Account.get_by_id(order[i]).update_sort_order(i)
    return redirect('/accounts', code=303)
