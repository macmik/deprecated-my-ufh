import logging
from threading import Thread
from datetime import datetime as DT
from sensor.mija.bluetooth_utils import (
    toggle_device, parse_le_advertising_events, enable_le_scan, raw_packet_to_str, decode_data_atc
)
from temperature_measurement import Measurement

import bluetooth._bluetooth as bluez


logger = logging.getLogger(__name__)


class Worker(Thread):
    def __init__(self, config, stop_event, queue):
        super().__init__()
        self._config = config
        self._stop_event = stop_event
        self._queue = queue
        self._enabled_macs = [sensor['MAC'] for sensor in self._config['sensors']]
        self._device_id = self._config['device_id']

    def run(self):
        try:
            toggle_device(self._device_id, enable=True)
            sock = bluez.hci_open_dev(self._device_id)
            enable_le_scan(sock, filter_duplicates=False)
            logger.debug("Starting bluetooth scanner.")
            parse_le_advertising_events(
                sock=sock,
                handler=self._le_advertise_packet_handler,
                debug=False,
                mac_addr=self._enabled_macs,
                stop_event=self._stop_event,
            )
        except Exception as e:
            logger.error(e)
            toggle_device(self._device_id, enable=False)

    def _le_advertise_packet_handler(self, mac, adv_type, data, rssi):
        data_str = raw_packet_to_str(data)
        measurement = Measurement(0, 0, 0, 0, 0, 0, 0, 0)
        measurement = decode_data_atc(mac, adv_type, data_str, rssi, measurement)

        logger.debug(f'Detected {measurement} for {mac}.')
        self._queue.put((DT.now(), mac, measurement))



