"""
	Health Service

	by Tristan Lingat
"""

import datetime
import logging
import logging.config
import json
import os
import connexion
import requests
import yaml

from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

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

def health_check():
    """Health Check on all Microservices"""
    logger.info("Starting Service Health Checks")
    if not os.path.exists(app_config['datastore']['filename']):
        services = {
            "receiver": "Down",
            "storage": "Down",
            "processing": "Down",
            "audit": "Down",
            "last_datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(app_config['datastore']['filename'], 'w', encoding='utf-8') as f:
            json.dump(services, f, indent=4)
    else:
        with open(app_config['datastore']['filename'], 'r', encoding='utf-8') as f:
            services = json.load(f)

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        logger.info("Checking Receiver...")
        receiver_check = requests.get(app_config['events']['receiver'], timeout=5)
        if receiver_check.status_code == 200:
            services['receiver'] = "Running"
    except:
        services['receiver'] = "Down"
    logger.info("Receiver Health: %s", {services['receiver']})
    try:
        logger.info("Checking Storage...")
        storage_check = requests.get(app_config['events']['storage'], timeout=5)
        if storage_check.status_code == 200:
            services['storage'] = "Running"
    except:
        services['storage'] = "Down"
    logger.info("Storage Health: %s", {services['storage']})
    try:
        logger.info("Checking Processing...")
        processing_check = requests.get(app_config['events']['processing'], timeout=5)
        if processing_check.status_code == 200:
            services['processing'] = "Running"
    except:
        services['processing'] = "Down"
    logger.info("Processing Health: %s", {services['processing']})
    try:
        logger.info("Checking Audit...")
        audit_check = requests.get(app_config['events']['audit'], timeout=5)
        if audit_check.status_code == 200:
            services['audit'] = "Running"
    except:
        services['audit'] = "Down"
    logger.info("Audit Health: %s", {services['audit']})
    services['last_datetime'] = current_datetime

    with open(app_config['datastore']['filename'], 'w', encoding='utf-8') as f:
        json.dump(services, f, indent=4, encoding='utf-8')

    logger.info("Finished Service Health Checks")
    logger.debug('Health of Services: %s', {services})

    return services, 200

def init_scheduler():
    """Initialize Scheduler"""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        health_check,
        'interval',
        seconds=app_config['scheduler']['period_sec']
    )
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api(
    "./openapi.yaml", 
    base_path="/health", 
    strict_validation=True, 
    validate_responses=True
)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)
