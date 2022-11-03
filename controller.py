import RPi.GPIO as GPIO


class Controller:
    def __init__(self, config):
        self._config = config
        self._zone_id_to_gpio = {}
        self._initialize()

    def _initialize(self):
        self._zone_id_to_gpio = {sensor['zone']: sensor['gpio'] for sensor in self._config['sensors']}
        GPIO.setmode(GPIO.BOARD)
        [GPIO.setup(gpio, GPIO.OUT) for gpio in self._zone_id_to_gpio.values()]
        [GPIO.setup(gpio, GPIO.HIGH) for gpio in self._zone_id_to_gpio.values()]

    def process(self, zone_id, should_heat):
        gpio = self._zone_id_to_gpio[zone_id]
        if should_heat:
            GPIO.setup(gpio, GPIO.LOW)
        else:
            GPIO.setup(gpio, GPIO.HIGH)
