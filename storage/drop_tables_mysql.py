import mysql.connector

db_conn = mysql.connector.connect(
    host="AZURE_VM_DNS",
    user="REDACTED",
    password="REDACTED",
    database="REDACTED"
)

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE albums, single_songs
                  ''')

db_conn.commit()
db_conn.close()
