import json
from datetime import datetime
import commonmark
from lib.db import Database
from flask import session

class Account:
    def __init__(self, id=None, created=None, user_id=None, name=None, balance=None, notes=None, sort_order=None, archived=None):
        self.id = id
        self.created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S') if created is not None else None
        self.user_id = user_id
        self.name = name
        self.balance = int(balance) if balance is not None else 0
        self.notes = notes if notes is not None else ""
        self.notes_html = commonmark.commonmark(notes) if notes is not None else ""
        self.sort_order = sort_order
        self.archived = archived

        self.repository = SQLiteAccountRepository(Database("tuppence.db"))

    def save(self):
        if self.id is None:
            self.repository.create(self)
        else:
            self.repository.update(self.id, self)

    def delete(self):
        self.repository.delete(self.id)

    def update(self, name, balance, notes, archived):
        self.name = name
        self.balance = balance
        self.notes = notes
        self.notes_html = commonmark.commonmark(notes)
        self.archived = archived

    def update_sort_order(self, sort_order):
        self.sort_order = sort_order
        self.repository.update_sort_order(self.id, sort_order)

    @classmethod
    def get_by_id(self, id):
        repository = SQLiteAccountRepository(Database("tuppence.db"))
        return repository.get_by_id(id)

    @classmethod
    def get_all(self):
        repository = SQLiteAccountRepository(Database("tuppence.db"))
        return repository.get_all()

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, default=str, indent=4)
    

class SQLiteAccountRepository:
    fields = ['id', 'created', 'user_id', 'name', 'balance', 'notes', 'sort_order', 'archived']

    def __init__(self, db):
        self.db = db

    def create(self, account):
        self.db.query("INSERT INTO accounts (user_id, name, balance, notes, sort_order, archived) VALUES (:user_id, :name, :balance, :notes, :sort_order, 0)", account.__dict__)

    def get_by_id(self, id):
        fields = ', '.join(self.fields)
        user_id = session['user_id']
        a = self.db.fetch_one(f"SELECT {fields} FROM accounts WHERE id = ? AND user_id = ?", (id, user_id))
        if a is None:
            return None
        return Account(**a)

    def get_all(self):
        fields = ', '.join(self.fields)
        user_id = session['user_id']
        a = self.db.fetch_all(f"SELECT {fields} FROM accounts WHERE user_id=? ORDER BY sort_order ASC, name DESC", (user_id,))
        return [Account(**a) for a in a]

    def delete(self, id):
        user_id = session['user_id']
        self.db.query("DELETE FROM accounts WHERE id = ? AND user_id = ?", (id, user_id))

    def update(self, id, account):
        account.id = id
        account.user_id = session['user_id']
        self.db.query("UPDATE accounts SET name = :name, balance = :balance, notes = :notes, archived = :archived WHERE id = :id AND user_id = :user_id", account.__dict__)

    def update_sort_order(self, id, sort_order):
        self.db.query("UPDATE accounts SET sort_order = :sort_order WHERE id = :id AND user_id = :user_id", {
            'id': id,
            'sort_order': sort_order,
            'user_id': session['user_id']
        })