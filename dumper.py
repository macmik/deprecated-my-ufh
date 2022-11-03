from pathlib import Path


class Dumper:
    DUMP_FILE_NAME = 'results.csv'

    def __init__(self, config):
        self._config = config
        self._dump_enabled = self._config['dump_enabled']
        self._dump_path = Path(self._config['dump_path'])

        if self._dump_enabled and not self._dump_path.exists():
            self._dump_path.mkdir()

    def dump(self, ts, mac, measurement):
        if self._dump_enabled:
            with open(self._dump_path / self.DUMP_FILE_NAME, 'a') as fo:
                fo.write(','.join([mac, str(ts), str(measurement.temperature), str(measurement.battery), '\n']))

