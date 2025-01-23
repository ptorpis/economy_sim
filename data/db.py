import sqlite3

db = 'db1.db'

try:
    with sqlite3.connect(db) as conn:
        print(f'Opened SQLite database with version {sqlite3.sqlite_version}')
        cursor = conn.cursor()

        
except sqlite3.OperationalError as e:
    print('Failed to open database:', )