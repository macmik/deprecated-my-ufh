import sys
import json
import logging
from os import environ
from datetime import datetime as DT
from pathlib import Path
from threading import Event
from queue import Queue

from flask import Flask, jsonify, render_template

from sensor.mija.worker import Worker
from zone_handler import ZoneHandler
from dispatcher import Dispatcher
from controller import Controller


def setup_logging():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    log_level = environ.get("LOG_LVL", "dump")
    if log_level == "dump":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "error":
        level = logging.ERROR
    elif log_level == "warning":
        level = logging.WARNING
    else:
        logging.error('"%s" is not correct log level', log_level)
        sys.exit(1)
    if getattr(setup_logging, "_already_set_up", False):
        logging.warning("Logging already set up")
    else:
        logging.basicConfig(format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", level=level)
        setup_logging._already_set_up = True


def create_app():
    app = Flask(__name__, static_folder='templates')

    setup_logging()
    config = json.loads(Path('config.json').read_text())
    queue = Queue()
    event = Event()

    mija_worker = Worker(stop_event=event, queue=queue, config=config)

    enabled_zones = config['enabled_zones']
    controller = Controller(config)
    zone_handlers = [ZoneHandler(zone_id, config, controller) for zone_id in enabled_zones]

    dispatcher = Dispatcher(config, queue, event, zone_handlers)

    mija_worker.start()
    dispatcher.start()

    app.worker = dispatcher
    app.zone_handlers = zone_handlers

    return app


app = create_app()


@app.route('/state')
def state():
    return jsonify(app.worker.get_state())


@app.route('/heating')
def heating():
    return jsonify({
        zone.get_zone_id(): zone.get_state() for zone in app.zone_handlers
    })


@app.route('/temp')
def temp():
    return render_template('charts.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
