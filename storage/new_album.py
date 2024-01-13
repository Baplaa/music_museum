"""
    New Album SQL Class
"""

import datetime
from sqlalchemy import Column, Integer, String
from base import Base

class NewAlbum(Base):
    """ New Album """

    __tablename__ = "albums"

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, nullable=False)
    album_name = Column(String(250), nullable=False)
    album_track_count = Column(Integer, nullable=False)
    artist_name = Column(String(100), nullable=False)
    date_created = Column(String(100), nullable=False)
    trace_id = Column(String(300), nullable=False)

    def __init__(self, album_id, album_name, album_track_count, artist_name, trace_id):
        """ Initializes a new album """
        self.album_id = album_id
        self.album_name = album_name
        self.album_track_count = album_track_count
        self.artist_name = artist_name
        self.trace_id = trace_id

        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        self.date_created = timestamp

    def to_dict(self):
        """ Dictionary Representation of a new album """
        dict = {}
        dict['id'] = self.id
        dict['album_id'] = self.album_id
        dict['album_name'] = self.album_name
        dict['album_track_count'] = self.album_track_count
        dict['artist_name'] = self.artist_name
        dict['trace_id'] = self.trace_id

        return dict
