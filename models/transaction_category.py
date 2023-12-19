import json
from lib.db import Database

# Class to model the join table between transactions and categories
class TransactionCategory:
    def __init__(self, transaction_id, category_id):
        self.transaction_id = transaction_id
        self.category_id = category_id

        self.repository = SQLiteTransactionCategoryRepository(Database("tuppence.db"))

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, default=str)
    
    def save(self):
        self.repository.create(self)

    def delete(self):
        self.repository.delete(self.transaction_id, self.category_id)

    @classmethod
    def delete_by_transaction_id(self, transaction_id):
        repository = SQLiteTransactionCategoryRepository(Database("tuppence.db"))
        repository.delete_by_transaction_id(transaction_id)

    @classmethod
    def get_by_transaction_id(self, transaction_id):
        repository = SQLiteTransactionCategoryRepository(Database("tuppence.db"))
        return repository.get_by_transaction_id(transaction_id)
    
class SQLiteTransactionCategoryRepository:
    def __init__(self, db):
        self.db = db

    def create(self, transaction_category):
        print(f"Creating transaction category {transaction_category.__dict__}")
        self.db.query("INSERT OR IGNORE INTO transaction_categories (transaction_id, category_id) VALUES (:transaction_id, :category_id)", transaction_category.__dict__)

    def delete(self, transaction_id, category_id):
        self.db.query("DELETE FROM transaction_categories WHERE transaction_id = :transaction_id AND category_id = :category_id", {
            "transaction_id": transaction_id,
            "category_id": category_id
        })

    def get_by_transaction_id(self, transaction_id):
        sql = """
        SELECT category_id
        FROM transaction_categories
        WHERE transaction_id = :transaction_id
        """
        return self.db.fetch_all(sql, {"transaction_id": transaction_id})

    def delete_by_transaction_id(self, transaction_id):
        self.db.query("DELETE FROM transaction_categories WHERE transaction_id = :transaction_id", {"transaction_id": transaction_id})