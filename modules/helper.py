import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout


class HelperWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setWindowTitle("Momo")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'momo.png')))

        self._layout = QVBoxLayout()

        self.title_label = self._create_label()
        self.title_label.setStyleSheet("font-weight: bold;text-decoration: underline;")
        self.artist_label = self._create_label()
        self.track_label = self._create_label()
        self.track_label.setStyleSheet("font-style: italic")

        self._layout.addWidget(self.title_label, stretch=3, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.artist_label, stretch=3, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.track_label, stretch=3, alignment=Qt.AlignmentFlag.AlignCenter)

        self.info_group = QGroupBox()
        self._info_group_layout = QHBoxLayout()
        self.time_label = self._create_label()
        self.track_count_label = self._create_label()
        self._info_group_layout.addWidget(self.time_label, stretch=1, alignment=Qt.AlignmentFlag.AlignLeft)
        self._info_group_layout.addWidget(self.track_count_label, stretch=1, alignment=Qt.AlignmentFlag.AlignRight)
        self.info_group.setLayout(self._info_group_layout)
        self._layout.addWidget(self.info_group)

        self.setLayout(self._layout)
        self.setMinimumSize(640, 480)

    @staticmethod
    def _create_label():
        label = QLabel("<>")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.parent_window.reset_helper()
        self.parent_window.window_check.setChecked(False)
        return super(HelperWindow, self).closeEvent(a0)
