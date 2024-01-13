"""
	Processing Service

    by Tristan Lingat
"""

import logging
import logging.config
import datetime
import json
import os
import requests
import connexion
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
from flask_cors import CORS

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yaml"
    LOG_CONF_FILE = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    APP_CONF_FILE = "app_conf.yaml"
    LOG_CONF_FILE = "log_conf.yaml"

with open(APP_CONF_FILE, 'r', encoding="utf-8") as f:
    app_config = yaml.safe_load(f.read())
with open(LOG_CONF_FILE, 'r', encoding="utf-8") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s", APP_CONF_FILE)
logger.info("Log Conf File: %s", LOG_CONF_FILE)

def populate_stats():
    """ Periodically update stats """
    logger.info('Start Periodic Processing')
    logger.info("test")

    if not os.path.exists(app_config['datastore']['filename']):
        stats = {
            "num_album_events": 0,
            "num_single_events": 0,
            "max_album_events": 0,
            "max_single_events": 0,
            "last_datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(app_config['datastore']['filename'], 'w', encoding='utf-8') as file:
            json.dump(stats, file, indent=4)
    else:
        with open(app_config['datastore']['filename'], 'r', encoding='utf-8') as file:
            stats = json.load(file)

    last_datetime = stats['last_datetime']
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {"Content-Type": "application/json"}

    new_album_events = requests.get(
        app_config['eventstore']['url'] + '/events/new_album?timestamp=' + last_datetime + "&end_timestamp=" + current_datetime, headers=headers
    ).json()
    new_single_song_events = requests.get(
        app_config['eventstore']['url'] + '/events/new_single_song?timestamp=' + last_datetime + "&end_timestamp=" + current_datetime, headers=headers
    ).json()

    logger.info('Number of new album events: %d', len(new_album_events))
    logger.info('Number of new single song events: %d', len(new_single_song_events))

    if stats['max_album_events'] < (stats['num_album_events'] + len(new_album_events)):
        stats['max_album_events'] = stats['num_album_events'] + len(new_album_events)
    if stats['max_single_events'] < (stats['num_single_events'] + len(new_single_song_events)):
        stats['max_single_events'] = stats['num_single_events'] + len(new_single_song_events)

    updated_stats = {
        "num_album_events": stats['num_album_events'] + len(new_album_events),
        "num_single_events": stats['num_single_events'] + len(new_single_song_events),
        "max_album_events": stats['max_album_events'],
        "max_single_events": stats['max_single_events'],
        "last_datetime": current_datetime
    }

    with open(app_config['datastore']['filename'], 'w', encoding='utf-8') as file:
        json.dump(updated_stats, file, indent=4)

    logger.debug('Updated stats: %d', updated_stats)
    logger.info('End Periodic Processing')


def init_scheduler():
    """Initialize the scheduler with the job store"""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
		populate_stats,
		'interval',
		seconds=app_config['scheduler']['period_sec']
	)
    sched.start()


def get_stats():
    """ Get Statistics """
    logger.info('Starting GET stats')

    if os.path.exists(app_config['datastore']['filename']):
        with open(app_config['datastore']['filename'], 'r', encoding='utf-8') as file:
            stats = json.load(file)
            logger.debug('Statistics: %d', stats)
    else:
        missing_stats = logger.error("Statistics do not exist")
        return missing_stats, 404

    logger.debug("Statistics retrieved: %d", stats)
    logger.info("Finished GET stats")

    return stats, 200

def health():
    """ Health Check """
    logger.info("Processing Health Check")
    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir="")

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS']='Content-Type'

app.add_api(
    "./openapi.yaml", 
    base_path="/processing", 
    strict_validation=True, 
    validate_responses=True
)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
