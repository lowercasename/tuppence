
import json
import sqlite3
from fuzzysearch import find_near_matches

from flask import session
from lib.db import Database

class Category:
    def __init__(self, name=None, id=None):
        self.id = id
        self.name = name
        self.user_id = session['user_id']

        self.repository = SQLiteCategoryRepository(Database("tuppence.db"))

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, default=str)
    
    def save(self):
        if self.id is None:
            self.repository.create(self)
            self.id = self.repository.get_by_name(self.name)['id']

    def delete(self):
        self.repository.delete(self.id)

    @classmethod
    def search(self, query):
        repository = SQLiteCategoryRepository(Database("tuppence.db"))
        return repository.search(query)

    @classmethod
    def get_by_name(self, name):
        repository = SQLiteCategoryRepository(Database("tuppence.db"))
        return repository.get_by_name(name)
    
class SQLiteCategoryRepository:
    fields = ['id', 'name', 'user_id']

    def __init__(self, db):
        self.db = db

    def create(self, category):
        self.db.query("INSERT OR IGNORE INTO categories (name, user_id) VALUES (:name, :user_id)", category.__dict__)

    def delete(self, id):
        user_id = session['user_id']
        self.db.query("DELETE FROM categories WHERE id = :id AND user_id = :user_id", {"id": id, "user_id": user_id})

    def get_by_name(self, name):
        user_id = session['user_id']
        sql = """
        SELECT id
        FROM categories
        WHERE name = :name
        AND user_id = :user_id
        """
        return self.db.fetch_one(sql, {"name": name, "user_id": user_id})
    
    def get_by_id(self, id):
        user_id = session['user_id']
        sql = """
        SELECT id, name
        FROM categories
        WHERE id = :id
        AND user_id = :user_id
        """
        return self.db.fetch_one(sql, {"id": id, "user_id": user_id})

    def search(self, query):
        user_id = session['user_id']
        sql = """
        SELECT name
        FROM categories
        WHERE user_id = :user_id
        ORDER BY name
        """
        matches = []
        for c in self.db.fetch_all(sql, {"user_id": user_id}):
            match = find_near_matches(query, c['name'], max_l_dist=1)
            if len(match) > 0:
                matches.append(c['name'])
        return matches
    
