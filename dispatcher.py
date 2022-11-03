import logging
from threading import Thread

from dumper import Dumper
from state import State

logger = logging.getLogger(__name__)


class Dispatcher(Thread):
    def __init__(self, config, queue, stop_event, zone_handlers):
        super().__init__()
        self._config = config
        self._queue = queue
        self._stop_event = stop_event
        self._zone_handlers = zone_handlers
        self._sensor_mac_to_zone_handler = {
            sensor['MAC']: self._get_zone_handler_by_zone_id(sensor['zone']) for sensor in self._config['sensors']
        }
        self._dumper = Dumper(self._config)
        self._state = State(config)

    def _get_zone_handler_by_zone_id(self, zone):
        for zone_handler in self._zone_handlers:
            if zone_handler.get_zone_id() == zone:
                return zone_handler

    def run(self):
        logger.info('Starting dispatcher!')
        while not self._stop_event.is_set():
            ts, mac, measurement = self._queue.get()
            self._state.update_state(ts, mac, measurement)
            self._dumper.dump(ts, mac, measurement)
            self._sensor_mac_to_zone_handler[mac].check_temperature(measurement.temperature)

    def get_state(self):
        return self._state.get_json()
