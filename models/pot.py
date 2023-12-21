import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import session

from lib.db import Database


class Pot:
    def __init__(self, id=None, created=None, user_id=None, name=None, balance=None, auto_assign=False, assign_amount=0, goal_type=None, goal_amount=0, goal_date=None, recurring_day=None, type=None, sort_order=None):
        self.id = id
        self.created = datetime.strptime(
            created, '%Y-%m-%d %H:%M:%S') if created is not None else None
        self.user_id = user_id  
        self.sort_order = sort_order
        self.name = name
        # Balances are stored in cents as integers
        self.balance = int(balance) if balance is not None else 0
        # Boolean
        self.auto_assign = auto_assign
        # If auto_assign is true, this is the amount to assign each month
        self.assign_amount = assign_amount * 100
        # Enum: none, goal-amount, goal-date, recurring
        # none: no goal
        # goal-amount: assign a certain amount
        # goal-date: assign a certain amount by a certain date
        # recurring: assign a certain amount every month on a certain date
        self.goal_type = goal_type
        self.goal_type_label = self.goal_type_to_string()
        # If goal_type is goal-amount, this is the amount to assign
        self.goal_amount = goal_amount
        # If goal_type is goal-date, this is the date to assign by
        # goal-date is always the first of the month
        self.goal_date = datetime.strptime(
            f"{goal_date[:8]}01", '%Y-%m-%d') if goal_date is not None else None
        # If goal_type is recurring, this is the day of the month to assign on
        self.recurring_day = recurring_day
        # Enum: user, system
        # user: created by the user
        # system: created by the system
        self.type = type
        # If pot goal is 'goal-date', calculate the amount we need
        # to assign each month to reach the goal by the goal date,
        # based on the current balance.
        self.recommended_assign_amount = 0
        self.months_remaining = 0
        self.percent_complete = 0
        self.goal_remaining = self.goal_amount - self.balance
        if self.goal_remaining < 0:
            self.goal_remaining = 0
        if self.goal_type == 'goal-date':
            first_of_this_month = datetime.today().replace(day=1)
            r = relativedelta(self.goal_date, first_of_this_month)
            months = r.years * 12 + r.months + 1
            if months > 0:
                self.recommended_assign_amount = round(
                    self.goal_remaining / months, 2)
            self.months_remaining = months
            self.percent_complete = round(
                (self.balance / self.goal_amount) * 100, 2)
        elif self.goal_type == 'goal-amount' or self.goal_type == 'recurring':
            self.percent_complete = round(
                (self.balance / self.goal_amount) * 100, 2)
        if self.percent_complete > 100:
            self.percent_complete = 100

        self.repository = SQLitePotRepository(Database("tuppence.db"))

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def save(self):
        if self.id is None:
            self.repository.create(self)
        else:
            self.repository.update(self.id, self)

    def delete(self):
        self.repository.delete(self.id)

    def update(self, name, balance, auto_assign, assign_amount, goal_type, goal_amount, goal_date, recurring_day, type):
        self.name = name
        self.balance = balance
        self.auto_assign = auto_assign
        self.assign_amount = assign_amount
        self.goal_type = goal_type
        self.goal_amount = goal_amount
        self.goal_date = goal_date
        self.recurring_day = recurring_day
        self.type = type 

    def update_sort_order(self, sort_order):
        self.sort_order = sort_order
        self.repository.update_sort_order(self.id, sort_order)

    @classmethod
    def get_by_id(self, id):
        repository = SQLitePotRepository(Database("tuppence.db"))
        return repository.get_by_id(id)
    
    @classmethod
    def get_all(self):
        repository = SQLitePotRepository(Database("tuppence.db"))
        return repository.get_all()

    def goal_type_to_string(self):
        if self.goal_type == 'goal-amount':
            return 'Save a certain amount'
        elif self.goal_type == 'goal-date':
            return 'Save a certain amount by a certain date'
        elif self.goal_type == 'recurring':
            return 'Recurring expense'
        else:
            return 'Simple pot'

class SQLitePotRepository:
    fields = ['id', 'created', 'user_id', 'name', 'balance', 'auto_assign',
              'assign_amount', 'goal_type', 'goal_amount', 'goal_date',
              'recurring_day', 'type', 'sort_order']

    def __init__(self, db):
        self.db = db

    def create(self, pot):
        self.db.query("INSERT INTO pots (user_id, name, balance, auto_assign, assign_amount, goal_type, goal_amount, goal_date, recurring_day, type, sort_order) VALUES (:user_id, :name, :balance, :auto_assign, :assign_amount, :goal_type, :goal_amount, :goal_date, :recurring_day, :type, :sort_order)", pot.__dict__)

    def get_by_id(self, id):
        fields = ', '.join(self.fields)
        user_id = session['user_id']
        p = self.db.fetch_one(f"SELECT {fields} FROM pots WHERE id = ? AND user_id = ?", (id, user_id))
        if p is None:
            return None
        return Pot(**p)

    def get_all(self):
        fields = ', '.join(self.fields)
        user_id = session['user_id']
        p = self.db.fetch_all(f"SELECT {fields} FROM pots WHERE user_id = ? ORDER BY sort_order ASC, name DESC", (user_id,))
        return [Pot(**p) for p in p]

    def delete(self, id):
        user_id = session['user_id']
        self.db.query("DELETE FROM pots WHERE id = ? AND user_id = ?", (id, user_id))

    def update(self, id, pot):
        pot.id = id
        pot.user_id = session['user_id']
        self.db.query("UPDATE pots SET name = :name, balance = :balance, auto_assign = :auto_assign, assign_amount = :assign_amount, goal_type = :goal_type, goal_amount = :goal_amount, goal_date = :goal_date, recurring_day = :recurring_day, type = :type WHERE id = :id AND user_id = :user_id", pot.__dict__)

    def update_sort_order(self, id, sort_order):
        self.db.query("UPDATE pots SET sort_order = :sort_order WHERE id = :id AND user_id = :user_id", {
            'id': id,
            'sort_order': sort_order,
            'user_id': session['user_id']
        })
