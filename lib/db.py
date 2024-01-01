import sqlite3
from hashids import Hashids


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        
    def init_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                email_address TEXT UNIQUE NOT NULL,
                login_token TEXT,
                login_token_expiry DATETIME
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                name TEXT UNIQUE NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS pots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                name TEXT UNIQUE NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                auto_assign BOOLEAN NOT NULL DEFAULT 0,
                assign_amount INTEGER NOT NULL DEFAULT 0,
                goal_type TEXT NOT NULL DEFAULT 'none',
                goal_amount INTEGER NOT NULL DEFAULT 0,
                goal_date DATETIME,
                recurring_day INTEGER,
                type TEXT NOT NULL DEFAULT 'user',
                sort_order INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashid TEXT UNIQUE NOT NULL DEFAULT '',
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                pot_id INTEGER,
                account_id INTEGER,
                amount INTEGER NOT NULL,
                description TEXT NOT NULL,
                is_transfer BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (pot_id) REFERENCES pots (id),
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (user_id, name)
            );""")
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transaction_categories (
                transaction_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id),
                FOREIGN KEY (category_id) REFERENCES categories (id),
                UNIQUE (transaction_id, category_id)
            );""")
        # Create a trigger to update the referenced account and pot balances when a transaction is created
        self.cur.execute("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_insert
            AFTER INSERT ON transactions
            BEGIN
                UPDATE accounts SET balance = balance + NEW.amount WHERE id = NEW.account_id;
                UPDATE pots SET balance = balance + NEW.amount WHERE id = NEW.pot_id;
            END;""")
        # Create a trigger to update the referenced account and pot balances when a transaction is updated
        self.cur.execute("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_update
            AFTER UPDATE ON transactions
            BEGIN
                UPDATE accounts SET balance = balance - OLD.amount WHERE id = OLD.account_id;
                UPDATE pots SET balance = balance - OLD.amount WHERE id = OLD.pot_id;
                UPDATE accounts SET balance = balance + NEW.amount WHERE id = NEW.account_id;
                UPDATE pots SET balance = balance + NEW.amount WHERE id = NEW.pot_id;
            END;""")
        # Create a trigger to update the referenced account and pot balances when a transaction is deleted
        self.cur.execute("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_delete
            AFTER DELETE ON transactions
            BEGIN
                UPDATE accounts SET balance = balance - OLD.amount WHERE id = OLD.account_id;
                UPDATE pots SET balance = balance - OLD.amount WHERE id = OLD.pot_id;
            END;""")
        self.cur.execute("""
            INSERT OR IGNORE INTO settings (name, value) VALUES ('allow_registration', '1');
        """)
        self.conn.commit()

    def query(self, query, args=()):
        self.cur.execute(query, args)
        self.conn.commit()
        return self.cur
    
    def multi_query(self, queries):
        for query in queries:
            self.cur.execute(query.query, query.args)
        self.conn.commit()
        return self.cur

    def fetch_one(self, query, args=()):
        self.cur.execute(query, args)
        self.conn.commit()
        row = self.cur.fetchone()
        return dict(row) if row is not None else None

    def fetch_all(self, query, args=()):
        self.cur.execute(query, args)
        self.conn.commit()
        rows = self.cur.fetchall()
        return [dict(row) for row in rows]

    def last_row_id(self):
        return self.cur.lastrowid

    def generate_hashid(self, id=None) -> str:
        if id == None:
            # Hash the last row id
            id = self.last_row_id()
        return Hashids(min_length=6).encode(id)

    def set_hashid(self, table, id=None):
        if id == None:
            id = self.last_row_id()
        hashid = self.generate_hashid(id)
        self.query(f"UPDATE {table} SET hashid = ? WHERE id = ?", (hashid, id))

    def __del__(self):
        self.conn.close()
