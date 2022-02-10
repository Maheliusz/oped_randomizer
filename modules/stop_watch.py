from PyQt6.QtCore import QTimer


class StopWatch:
    def __init__(self, timeout):
        self._secret_timer = QTimer()
        self._initial_time: int = timeout
        self.time = self._initial_time
        self._timeout_fun = lambda: None
        self._tick_fun = lambda: None
        self._secret_timer.timeout.connect(self._tick)
        self._secret_timer.setSingleShot(False)

    def start(self):
        self._secret_timer.start(1000)

    def stop(self):
        self._secret_timer.stop()

    def reset(self):
        self.stop()
        self.time = self._initial_time

    def connect_timeout_fun(self, fun):
        self._timeout_fun = fun

    def connect_tick_fun(self, fun):
        self._tick_fun = fun

    def set_time(self, time):
        self._initial_time = time
        self.time = time

    def _tick(self):
        self.time = self.time - 1
        self._tick_fun()
        if self.time == 0:
            self._timeout_fun()
            self._secret_timer.stop()
