import sqlite3

db = 'db1.db'


connection = sqlite3.connect(db)

cursor = connection.cursor()



connection.commit()
connection.close()
