"""
    New Single SQL Class
"""

import datetime
from sqlalchemy import Column, Integer, String
from base import Base

class NewSingle(Base):
    """ New Single """

    __tablename__ = "single_songs"

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, nullable=False)
    song_name = Column(String(250), nullable=False)
    song_duration = Column(Integer, nullable=False)
    artist_name = Column(String(100), nullable=False)
    date_created = Column(String(100), nullable=False)
    trace_id =  Column(String(300), nullable=False)

    def __init__(self, song_id, song_name, song_duration, artist_name, trace_id):
        """ Initializes a new single song """
        self.song_id = song_id
        self.song_name = song_name
        self.song_duration = song_duration
        self.artist_name = artist_name
        self.trace_id = trace_id

        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        self.date_created = timestamp

    def to_dict(self):
        """ Dictionary Representation of a new single song """
        dict = {}
        dict['id'] = self.id
        dict['song_id'] = self.song_id
        dict['song_name'] = self.song_name
        dict['song_duration'] = self.song_duration
        dict['artist_name'] = self.artist_name
        dict['trace_id'] = self.trace_id

        return dict
