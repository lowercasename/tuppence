import sqlite3

def migrate():
    conn = sqlite3.connect("tuppence.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
                   UPDATE transactions SET date = created WHERE date IS 0;
                   """)
    conn.commit()

migrate()
