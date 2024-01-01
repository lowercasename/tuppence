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
    unarchived = [x for x in a if not x.archived]
    archived = [x for x in a if x.archived]
    return render_template('accounts.html', unarchived=unarchived, archived=archived)

@app.route('/accounts/<id>')
@with_auth
def account_get(id):
    a = Account.get_by_id(id)
    if a is None:
        return 404
    return render_template('account_single.html', account=a)


# @app.route('/accounts/<id>', methods=['DELETE'])
# @with_auth
# def account_delete(id):
#     Account.get_by_id(id).delete()
#     return redirect('/accounts', code=303)


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
    a.update(name=name, balance=currency_string_to_database(balance), notes=notes, archived=False)
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
    order = request.form.getlist('account_id')   
    if len(order) == 0:
        return 400
    for i in range(len(order)):
        a = Account.get_by_id(order[i])
        if a is None:
            return 400
        a.update_sort_order(i)
    return redirect('/accounts', code=303)

@app.route('/accounts/<id>/archive', methods=['POST'])
@with_auth
def account_archive(id):
    a = Account.get_by_id(id)
    if a is None:
        return 404
    a.update(name=a.name, balance=a.balance, notes=a.notes, archived=True)
    a.save()
    return redirect('/accounts', code=303)

@app.route('/accounts/<id>/unarchive', methods=['POST'])
@with_auth
def account_unarchive(id):
    a = Account.get_by_id(id)
    if a is None:
        return 404
    a.update(name=a.name, balance=a.balance, notes=a.notes, archived=False)
    a.save()
    return redirect('/accounts', code=303)
