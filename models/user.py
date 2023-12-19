from datetime import datetime, timedelta
from lib.strings import generate_login_token
import json
from lib.db import Database

class User:
    def __init__(self, id=None, created=None, email_address=None, login_token=None, login_token_expiry=None):
        self.id = id
        self.email_address = email_address
        self.login_token = login_token
        self.login_token_expiry = datetime.strptime(login_token_expiry, '%Y-%m-%d %H:%M:%S.%f') if login_token_expiry is not None else None
        self.repository = SQLiteUserRepository(Database("tuppence.db"))

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)
    
    def save(self):
        if self.id is None:
            self.repository.create(self)
        else:
            self.repository.update(self.id, self)

    def update(self, email_address):
        self.email_address = email_address

    def delete(self):
        self.repository.delete(self.id)

    @classmethod
    def get_by_email_address(self, email_address):
        self.repository = SQLiteUserRepository(Database("tuppence.db"))
        return self.repository.get_by_email_address(email_address)

    @classmethod
    def get_by_login_token(self, login_token):
        repository = SQLiteUserRepository(Database("tuppence.db"))
        return repository.get_by_login_token(login_token)

    def generate_login_token(self):
        self.login_token = generate_login_token()
        self.login_token_expiry = datetime.now() + timedelta(hours=1)

    @classmethod
    def login(self, login_token):
        repository = SQLiteUserRepository(Database("tuppence.db"))
        user = repository.get_by_login_token(login_token)
        if user is None:
            return None
        if user.login_token != login_token or user.login_token_expiry < datetime.now():
            return None
        # User has logged in successfully, so clear the login token
        user.login_token = None
        user.login_token_expiry = None
        user.save()
        return user

class UserRepository:
    @classmethod
    def create(cls, user: User):
        raise NotImplementedError
    
    @classmethod
    def get_by_id(cls, id):
        raise NotImplementedError
    
    @classmethod
    def get_by_email_address(cls, email_address):
        raise NotImplementedError

    @classmethod
    def get_by_login_token(cls, login_token):
        raise NotImplementedError
    
    @classmethod
    def update(cls, id, user: User):
        raise NotImplementedError
    
    @classmethod
    def delete(cls, id):
        raise NotImplementedError

class SQLiteUserRepository(UserRepository):
    fields = ['id', 'created', 'email_address', 'login_token', 'login_token_expiry']

    def __init__(self, db):
        self.db = db

    def create(self, user: User):
        self.db.query("INSERT INTO users (email_address, login_token, login_token_expiry) VALUES (:email_address, :login_token, :login_token_expiry)", user.__dict__)

    def get_by_id(self, id):
        u = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (id,))
        if u is None:
            return None
        return User(**u)
    
    def get_by_email_address(self, email_address):
        u = self.db.fetch_one("SELECT * FROM users WHERE email_address = ?", (email_address,))
        if u is None:
            return None
        return User(**u)

    def get_by_login_token(self, login_token):
        u = self.db.fetch_one("SELECT * FROM users WHERE login_token = ?", (login_token,))
        if u is None:
            return None
        return User(**u)

    def update(self, id, user: User):
        user.id = id
        self.db.query("UPDATE users SET email_address = :email_address, login_token = :login_token, login_token_expiry = :login_token_expiry WHERE id = :id", user.__dict__)

    def delete(self, id):
        self.db.query("DELETE FROM users WHERE id = ?", (id,))
