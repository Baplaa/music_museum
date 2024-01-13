"""
	Storage Service

    by Tristan Lingat
"""
import logging
import logging.config
import datetime
import json
import time
import os
from threading import Thread
import connexion
import yaml

from connexion import NoContent

from pykafka import KafkaClient
from pykafka.common import OffsetType

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from base import Base
from new_album import NewAlbum
from new_single import NewSingle

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yaml"
    LOG_CONF_FILE = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    APP_CONF_FILE = "app_conf.yaml"
    LOG_CONF_FILE = "log_conf.yaml"
with open(APP_CONF_FILE, 'r', encoding='utf-8') as f:
    app_config = yaml.safe_load(f.read())
with open(LOG_CONF_FILE, 'r', encoding='utf-8') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s", APP_CONF_FILE)
logger.info("Log Conf File: %s", LOG_CONF_FILE)

DB_ENGINE = create_engine(
    f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}"
)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_new_album(timestamp, end_timestamp):
    """Get New Album"""
    logger.info("test")
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    albums = session.query(NewAlbum).filter(
        and_(
            NewAlbum.date_created >= timestamp_datetime,
            NewAlbum.date_created < end_timestamp_datetime
        )
    )

    results_list = []

    for album in albums:
        results_list.append(album.to_dict())
    session.close()

    logger.info(
        'Query for New Album events after %s returns %d results', timestamp, len(results_list)
    )

    return results_list, 200


def get_new_single_song(timestamp, end_timestamp):
    """Get New Single Song"""
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    singles = session.query(NewSingle).filter(
        and_(
            NewSingle.date_created >= timestamp_datetime,
            NewSingle.date_created < end_timestamp_datetime
        )
    )

    results_list = []

    for single in singles:
        results_list.append(single.to_dict())
    session.close()

    logger.info(
        'Query for New Album events after %s returns %d results', timestamp, len(results_list)
    )

    return results_list, 200


def process_messages():
    """Process event messages"""
    logger.info("Starting message processing thread")

    hostname = "%s:%d", (app_config["events"]["hostname"], app_config["events"]["port"])

    retry_time = app_config["retries"]["retry_time"]
    retries = app_config["retries"]["max_retries"]
    retry = 0

    while retry < retries:
        logger.info("Kafka Connection Attempt %s out of %d", retry, retries)
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.error("Kafka Connection FAILED. Trying again in %s seconds", retry_time)
            time.sleep(retry_time)
            retry += 1

    consumer = topic.get_simple_consumer(
        consumer_group=b'event_group',
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST
    )

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s", msg)

        payload = msg["payload"]

        if msg["type"] == "new_album":
            logger.info("New Album Payload Committed")
            session = DB_SESSION()

            album = NewAlbum(payload['album_id'],
                payload["album_name"],
                payload["album_track_count"],
                payload["artist_name"],
                payload["trace_id"])

            session.add(album)
            session.commit()
            session.close()

            logger.debug(
                'Stored event `new_album` request with a trace id of %s', payload["trace_id"]
            )
        elif msg["type"] == "new_single_song":
            logger.info("New Single Song Payload Committed")
            session = DB_SESSION()

            single = NewSingle(payload['song_id'],
                payload["song_name"],
                payload["song_duration"],
                payload["artist_name"],
                payload["trace_id"])

            session.add(single)
            session.commit()
            session.close()

            logger.debug(
                'Stored event `new_single_song` request with a trace id of %s', payload["trace_id"]
            )

        consumer.commit_offsets()

    logger.info("Ending message processing thread")

def health():
    """ Health Check """
    logger.info("Storage Health Check")
    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("./openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logger.info(
        'Connecting to DB. Hostname: %s, Port: %d', 
        app_config["datastore"]["hostname"],
        app_config["datastore"]["port"]
    )

    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)
