from flask import render_template, request, redirect, session
from app import app
from lib.auth import with_auth
from lib.server import MissingFieldException, validate_form_fields
from lib.strings import currency_string_to_database
from models.pot import Pot
from models.transaction import Transaction
from models.account import Account

@app.route('/pots')
@with_auth
def pot_list():
    p = Pot.get_all()
    return render_template('pots.html', pots=p)


@app.route('/pots/<id>')
@with_auth
def pot_get(id):
    p = Pot.get_by_id(id)
    if p is None:
        return 404
    return render_template('pot_single.html', pot=p)


@app.route('/pots/<id>/editor', methods=['GET'])
@with_auth
def pot_editor(id):
    p = Pot.get_by_id(id)
    if p is None:
        return 404
    return render_template('pot_editor.html', pot=p)


@app.route('/pots/<id>', methods=['DELETE'])
@with_auth
def pot_delete(id):
    Pot.get_by_id(id).delete()
    return redirect('/pots', code=303)


@app.route('/pots', methods=['POST'])
@with_auth
def pot_create():
    print(request.form)
    name, balance, goal_type = validate_form_fields(
        ['name', 'balance', 'goal_type']).values()
    goal_amount = 0
    goal_date = None
    recurring_day = None
    if goal_type == 'goal-amount' or goal_type == 'recurring':
        if 'goal_amount' not in request.form:
            raise MissingFieldException('Missing field: goal_amount')
        goal_amount = request.form['goal_amount']
        if goal_type == 'recurring':
            if 'recurring_day' not in request.form:
                raise MissingFieldException('Missing field: recurring_day')
            recurring_day = request.form['recurring_day']
        goal_date = None
    elif goal_type == 'goal-date':
        if 'goal_amount' not in request.form:
            raise MissingFieldException('Missing field: goal_amount')
        if 'goal_date' not in request.form:
            raise MissingFieldException('Missing field: goal_date')
        goal_amount = request.form['goal_amount']
        goal_date = request.form['goal_date']
    user_id = session['user_id']
    p = Pot(user_id=user_id, name=name, balance=currency_string_to_database(balance), goal_type=goal_type,
            goal_amount=currency_string_to_database(goal_amount), goal_date=goal_date, recurring_day=recurring_day, type="user",
            sort_order=0)
    p.save()
    return redirect('/pots', code=303)


@app.route('/pots/<id>', methods=['PUT'])
@with_auth
def pot_update(id):
    name, balance, goal_type = validate_form_fields(
        ['name', 'balance', 'goal_type']).values()
    goal_amount = 0
    goal_date = None
    recurring_day = None
    if goal_type == 'goal-amount' or goal_type == 'recurring':
        if 'goal_amount' not in request.form:
            raise MissingFieldException('Missing field: goal_amount')
        goal_amount = request.form['goal_amount']
        if goal_type == 'recurring':
            if 'recurring_day' not in request.form:
                raise MissingFieldException('Missing field: recurring_day')
            recurring_day = request.form['recurring_day']
        goal_date = None
    elif goal_type == 'goal-date':
        if 'goal_amount' not in request.form:
            raise MissingFieldException('Missing field: goal_amount')
        if 'goal_date' not in request.form:
            raise MissingFieldException('Missing field: goal_date')
        goal_amount = request.form['goal_amount']
        goal_date = request.form['goal_date']
    p = Pot.get_by_id(id)
    p.update(name=name, balance=currency_string_to_database(balance), goal_type=goal_type,
            goal_amount=currency_string_to_database(goal_amount), goal_date=goal_date, recurring_day=recurring_day, type="user")
    p.save()
    return redirect('/pots', code=303)

@app.route('/pots/reorder', methods=['POST'])
@with_auth
def pot_reorder():
    order = request.get_json()
    if len(order) == 0:
        return '', 200
    for i in range(len(order)):
        Pot.get_by_id(order[i]).update_sort_order(i)
    return redirect('/pots', code=303)