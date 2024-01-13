import mysql.connector

db_conn = mysql.connector.connect(
  host="AZURE_VM_DNS",
  user="REDACTED",
  password="REDACTED",
  database="REDACTED"
)

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  CREATE TABLE albums (
                    id INT NOT NULL AUTO_INCREMENT,
                    album_id INTEGER NOT NULL,
                    album_name VARCHAR(250) NOT NULL,
                    album_track_count INTEGER NOT NULL,
                    artist_name VARCHAR(100) NOT NULL,
                    date_created VARCHAR(100) NOT NULL,
                    trace_id VARCHAR(300) NOT NULL,
                    CONSTRAINT albums_pk PRIMARY KEY (id)  
                    )
                ''')

db_cursor.execute('''
                  CREATE TABLE single_songs (
                    id INT NOT NULL AUTO_INCREMENT,
                    song_id INTEGER NOT NULL,
                    song_name VARCHAR(250) NOT NULL,
                    song_duration INTEGER NOT NULL,
                    artist_name VARCHAR(100) NOT NULL,
                    date_created VARCHAR(100) NOT NULL,
                    trace_id VARCHAR(300) NOT NULL,
                    CONSTRAINT single_songs_pk PRIMARY KEY (id)  
                    )
                ''')

db_conn.commit()
db_conn.close()
