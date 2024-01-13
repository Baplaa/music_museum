"""
	Receiver Service
    
    by Tristan Lingat
"""

import logging
import logging.config
import uuid
import datetime
import json
import time
import os
import connexion
import yaml

from connexion import NoContent
from pykafka import KafkaClient

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

hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])

retry_time = app_config["retries"]["retry_time"]
retries = app_config['retries']['max_retries']
retry = 0

while retry < retries:
    logger.info("Kafka Connection Attempt % s out of %d", retry, retries)
    try:
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        break
    except:
        logger.error("Kafka Connection FAILED. Trying again in %s seconds", retry_time)
        time.sleep(retry_time)
        retry += 1


def new_album(body):
    """New Album"""
    uuid_req = uuid.uuid1()
    logger.info('Received event `new_album` request with a trace id of %s', uuid_req)
    body['trace_id'] = str(uuid_req)

    msg = {
        "type": "new_album",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        'Returned event `new_album` request with a trace id of `%s` with status `201`', 
        uuid_req
    )

    return NoContent, 201


def new_single_song(body):
    """New Single Song"""
    uuid_req = uuid.uuid1()
    logger.info('Received event `new_single_song` request with a trace id of %s', uuid_req)
    body['trace_id'] = str(uuid_req)

    msg = {
        "type": "new_single_song",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(
        'Returned event `new_single_song` request with a trace id of `%s` with status `201`', 
        uuid_req
    )

    return NoContent, 201

def health():
    """Health Check"""
    logger.info("Receiver Health Check")
    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "./openapi.yaml", 
    base_path="/receiver", 
    strict_validation=True, 
    validate_responses=True
)

if __name__ == "__main__":
    print('hello world')
    app.run(port=8080)
