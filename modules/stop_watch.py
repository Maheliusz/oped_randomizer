import typing

from PyQt6.QtCore import QTimer, QObject


class StopWatch(QTimer):
    def __init__(self, parent: typing.Optional[QObject] = ...):
        super().__init__(parent)
        self.second_fun = None

    def connect_second(self, fun):
        self.second_fun = fun