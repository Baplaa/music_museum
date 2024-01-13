"""
	Audit Microservice

    by Tristan Lingat
"""

import logging
import logging.config
import json
import os
import connexion
import yaml

from pykafka import KafkaClient
from flask_cors import CORS
from connexion import NoContent

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

def get_album(index):
    """Get Album by Index"""
    hostname = "%s:%d", (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving Album at index %d", index)
    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'new_album':
                if i == index:
                    logger.info("Found Album at index %d", index)
                    return { "event": msg }, 200
                i += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find album at index %d", index)
    return { "message": "Not Found" }, 404


def get_single_song(index):
    """Get Single Song by Index"""
    hostname = "%s:%d", (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving Single Song at index %d", index)
    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'new_single_song':
                if i == index:
                    logger.info("Found Single Song at index %d", index)
                    return { "event": msg }, 200
                i += 1
    except:
        logger.error("No more messages found")
    logger.error("Could not find single song at index %d", index)
    return { "message": "Not Found" }, 404

def health():
    """Health Check Endpoint for Health Microservice"""
    logger.info("Audit Health Check")
    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir="")

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS']='Content-Type'

app.add_api(
	"./openapi.yaml", 
	base_path="/audit_log", 
	strict_validation=True, 
	validate_responses=True
)

if __name__ == '__main__':
    app.run(port=8200)
