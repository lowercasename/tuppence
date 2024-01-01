from lib.db import Database


class Settings:
    @staticmethod   
    def get(name):
        repository = SQLiteSettingsRepository(Database("tuppence.db"))
        s = repository.get(name)
        if s is None:
            return None
        try:
            return bool(int(s))
        except ValueError: 
            return s

    @staticmethod
    def update(name, value):
        repository = SQLiteSettingsRepository(Database("tuppence.db"))
        repository.update(name, value)
        return Settings.get(name)

class SQLiteSettingsRepository:
    def __init__(self, db):
        self.db = db

    def get(self, name):
        s = self.db.fetch_one("SELECT * FROM settings WHERE name = ?", (name,))
        if s is None:
            return None
        return s['value']

    def update(self, name, value):
        self.db.query("UPDATE settings SET value = ? WHERE name = ?", (value, name))