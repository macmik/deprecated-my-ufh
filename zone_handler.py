import logging
from datetime import datetime as DT
from datetime import time

logger = logging.getLogger(__name__)


class ZoneHandler:
    def __init__(self, zone_id, config, controller):
        self._zone_id = zone_id
        self._config = config
        self._zone_location = None
        self._day_temperature = None
        self._night_temperature = None
        self._current_required_temperature = None
        self._latest_temperature = None
        self._day_time_range = None
        self._should_heat = False
        self._heating_started_ts = None
        self._controller = controller

        self._initialize()

    def _initialize(self):
        settings = self._config['settings']['zones'][str(self._zone_id)]
        self._day_temperature = settings["day"]["temperature"]
        self._night_temperature = settings["night"]["temperature"]

        self._day_time_range = (
            time(hour=settings["day"]["hour"], minute=settings["day"]["minute"]),
            time(hour=settings["night"]["hour"], minute=settings["night"]["minute"])
        )

        self._zone_location = [
            sensor["location"] for sensor in self._config["sensors"] if
            sensor["zone"] == self._zone_id
        ]

        logging.debug(f"Zone {self._zone_id} initialized.")
        logging.debug(f"time range = {str(self._day_time_range)}, day temp={self._day_temperature}, "
                      f"night temp={self._night_temperature}")

    def is_heating(self):
        return self._should_heat

    def get_zone_id(self):
        return self._zone_id

    def get_zone_location(self):
        return self._zone_location

    def get_state(self):
        return {
            'heating': self._should_heat,
            'location': self._zone_location,
            'required_temperature': self._current_required_temperature,
            'temperature': self._latest_temperature,
            'heating_started': str(self._heating_started_ts),
        }

    def check_temperature(self, temperature):
        now = DT.now().time()
        self._latest_temperature = temperature
        logger.debug(f'Checking zone_id {self._zone_id}, {self._zone_location}.')
        if self._day_time_range[0] <= now < self._day_time_range[1]:
            logger.debug('We are inside day range!')
            self._check_heating(temperature, self._day_temperature)
            self._current_required_temperature = self._day_temperature

        else:
            logger.debug('We are inside night range!')
            self._check_heating(temperature, self._night_temperature)
            self._current_required_temperature = self._night_temperature

    def _check_heating(self, current_temperature, set_temperature):
        if current_temperature < set_temperature - self._config['hysteresis']:
            if not self._should_heat:
                logger.debug(f'zone id = {self._zone_id}, location = {self._zone_location} heating started!')
                self._should_heat = True
                self._controller.process(self._zone_id, self._should_heat)
                self._heating_started_ts = DT.now()
                return
        elif current_temperature >= set_temperature + self._config['hysteresis']:
            if self._should_heat:
                logger.debug(f'zone id = {self._zone_id}, location = {self._zone_location} heating stopped!')
                self._should_heat = False
                self._controller.process(self._zone_id, self._should_heat)
                return
