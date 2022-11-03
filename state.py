class State:
    def __init__(self, config):
        self._config = config
        self._mac_to_location_map = {
            sensor['MAC']: sensor['location'] for sensor in self._config['sensors']
        }
        self._state = {}

    def update_state(self, ts, mac, measurement):
        self._state[mac] = [ts, measurement]

    def get_json(self):
        return {
            self._mac_to_location_map[mac]: {
                'mac': mac,
                'temperature': measurement.temperature,
                'battery': measurement.battery,
                'ts': str(ts),
            }
            for mac, (ts, measurement) in self._state.items()
        }
