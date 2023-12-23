import json
from datetime import datetime

from flask import session

from lib.db import Database
from models.category import Category
from models.transaction_category import TransactionCategory

class Transaction:
    def __init__(self, id=None, hashid=None, created=None, user_id=None, amount=0, description=None, is_transfer=None, account_id=None, account_name=None, category_names=None):
        self.id = id
        self.hashid = hashid
        self.created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S') if created is not None else None
        self.user_id = user_id
        self.account_id = account_id
        self.account_name = account_name
        self.amount = amount
        self.description = description
        self.is_transfer = is_transfer
        # If category_names is a string, split it into a list
        if isinstance(category_names, str):
            self.category_names = category_names.split(',')
        elif category_names is None:
            self.category_names = []
        else:
            self.category_names = category_names

        self.repository = SQLiteTransactionRepository(Database("tuppence.db"))

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, default=str)

    def save(self):
        if self.id is None:
            self.repository.create(self)
            # Save any categories associated with this transaction
            for category_name in self.category_names:
                print(f"Saving category {category_name}")
                category = Category(name=category_name)
                category.save()
                transaction_category = TransactionCategory(self.id, category.id)
                transaction_category.save()
        else:
            self.repository.update(self.id, self)
            # Delete any categories associated with this transaction
            TransactionCategory.delete_by_transaction_id(self.id)
            # Save any categories associated with this transaction
            for category_name in self.category_names:
                print(f"Updating category {category_name}")
                category = Category(name=category_name)
                category.save()
                transaction_category = TransactionCategory(self.id, category.id)
                transaction_category.save()

    def delete(self):
        # Delete any categories associated with this transaction
        TransactionCategory.delete_by_transaction_id(self.id)
        # Delete the transaction
        self.repository.delete(self.id)

    def update(self, account_id, amount, description, category_names):
        self.account_id = account_id
        self.amount = amount
        self.description = description
        self.category_names = category_names
        
    @classmethod
    def get_by_id(self, id):
        repository = SQLiteTransactionRepository(Database("tuppence.db"))
        return repository.get_by_id(id)
    
    @classmethod
    def get_all(self, month: int, year: int):
        repository = SQLiteTransactionRepository(Database("tuppence.db"))
        return repository.get_all(month, year)

class SQLiteTransactionRepository:
    fields = ['id', 'hashid', 'created', 'user_id', 'account_id', 'amount', 'description', 'is_transfer']

    def __init__(self, db):
        self.db = db

    def create(self, transaction):
        transaction.user_id = session['user_id']
        self.db.query("""
                    INSERT INTO transactions (user_id, account_id, amount, description, is_transfer)
                    VALUES (:user_id, :account_id, :amount, :description, :is_transfer)
                    """, transaction.__dict__)
        self.db.set_hashid("transactions")
        transaction.id = self.db.last_row_id()

    def get_all(self, month=None, year=None):
        user_id = session['user_id']
        sql = """
        SELECT t.id, t.hashid, t.created, t.user_id, t.amount, t.description, t.is_transfer, a.id as account_id, a.name as account_name, 
        GROUP_CONCAT(c.name) as category_names
        FROM transactions t
            LEFT OUTER JOIN accounts a on a.id = t.account_id
            LEFT OUTER JOIN transaction_categories tc on tc.transaction_id = t.id
            LEFT OUTER JOIN categories c on c.id = tc.category_id
        WHERE t.user_id = :user_id
        {{date_sql}}
        GROUP BY t.id
        ORDER BY t.created DESC;
        """
        if month is not None and year is not None:
            date_sql = "AND strftime('%m', t.created) = :month AND strftime('%Y', t.created) = :year"
            sql = sql.replace("{{date_sql}}", date_sql)
            t = self.db.fetch_all(sql, {
                'user_id': user_id,
                'month': f'{month:02}',
                'year': str(year)
            })
        else:
            t = self.db.fetch_all(sql, {
                'user_id': user_id
            })
        return [Transaction(**t) for t in t]

    def get_by_id(self, id):
        user_id = session['user_id']
        t = self.db.fetch_one("""
            SELECT t.id, t.hashid, t.created, t.user_id, t.amount, t.description, t.is_transfer, a.id as account_id, a.name as account_name, 
            GROUP_CONCAT(c.name) as category_names
            FROM transactions t
                LEFT OUTER JOIN accounts a on a.id = t.account_id
                LEFT OUTER JOIN transaction_categories tc on tc.transaction_id = t.id
                LEFT OUTER JOIN categories c on c.id = tc.category_id
            WHERE t.id = :id    
            AND t.user_id = :user_id
            GROUP BY t.id
            ORDER BY t.created DESC;
        """, ({
            'id': id,
            'user_id': user_id
        }))
        if t is None:
            return None
        return Transaction(**t)

    def delete(self, id):
        user_id = session['user_id']
        self.db.query("DELETE FROM transactions WHERE id = ? AND user_id = ?", (id, user_id))
 
    def update(self, id, transaction):
        transaction.id = id
        transaction.user_id = session['user_id']
        self.db.query("""
            UPDATE transactions
            SET account_id = :account_id, amount = :amount, description = :description
            WHERE id = :id
            AND user_id = :user_id
        """, transaction.__dict__)
        self.db.set_hashid("transactions")
