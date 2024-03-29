import logging
import math
import os

from PyQt6.QtCore import QSize, QTimer, Qt, QDir
from PyQt6.QtGui import QIcon, QCloseEvent, QIntValidator
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QCheckBox, QLineEdit, QSizePolicy, QLabel, \
    QPushButton, QButtonGroup, QMenu, QMenuBar, QFileDialog

from modules.helper import HelperWindow
from modules.stop_watch import StopWatch


class ControllerWindow(QWidget):
    def __init__(self, directory, player, library_handler, do_not_write_used):
        super().__init__()
        self.directory = directory
        self.setWindowTitle("Shami")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'shami.png')))

        self.no_used = do_not_write_used

        self.helper_window = HelperWindow(self)
        self.player = player
        self.library_handler = library_handler

        self._layout = QVBoxLayout()
        self.menu_bar = self._prepare_menus()
        self.helper_windows_group = self._prepare_helper_windows_group()
        self.timebox = self._prepare_timebox()
        self.infobox = self._prepare_infobox()
        self.button_group = self._prepare_buttons()

        self._layout.setMenuBar(self.menu_bar)
        self._layout.addWidget(self.helper_windows_group)
        self._layout.addWidget(self.infobox, 1)
        self._layout.addWidget(self.timebox)
        self._layout.addWidget(self.button_group)
        self.setLayout(self._layout)
        self.setMinimumSize(800, 600)
        self._update_track_counter()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.helper_window.close()
        return super(ControllerWindow, self).closeEvent(a0)

    def minimumSizeHint(self):
        return QSize(800, 600)

    def _prepare_menus(self):
        menu_bar = QMenuBar()
        self.menu = QMenu("Menu")

        self.menu.addAction("Open", self._open_directory)
        self.menu.addSeparator()
        self.menu.addAction("Exit", self.close)

        menu_bar.addMenu(self.menu)
        return menu_bar

    def _open_directory(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        path = dialog.getExistingDirectory()
        if path:
            self.directory = path
            self.library_handler.__init__(path)
            self.player.__init__(self.library_handler.audio_files, self.library_handler.used, self.directory)
            self._update_track_counter()

    def _prepare_helper_windows_group(self):
        group = QGroupBox("Helper Window")
        box = QHBoxLayout()

        self.window_check = QCheckBox("Show")
        self.window_check.setChecked(False)
        self.window_check.stateChanged.connect(self._show_helper)
        box.addWidget(self.window_check)
        self.title_check = QCheckBox("Title")
        self.title_check.setChecked(False)
        self.title_check.setEnabled(False)
        self.title_check.stateChanged.connect(self._show_title)
        box.addWidget(self.title_check)
        self.artist_check = QCheckBox("Artist")
        self.artist_check.setChecked(False)
        self.artist_check.setEnabled(False)
        self.artist_check.stateChanged.connect(self._show_artist)
        box.addWidget(self.artist_check)
        self.track_check = QCheckBox("Track")
        self.track_check.setChecked(False)
        self.track_check.setEnabled(False)
        self.track_check.stateChanged.connect(self._show_track)
        box.addWidget(self.track_check)
        self.helper_font_size = QLineEdit()
        self.helper_font_size.setValidator(QIntValidator())
        self.helper_font_size.setMaxLength(3)
        self.helper_font_size.setEnabled(False)
        self.helper_font_size.textChanged.connect(self._change_helper_font_size)
        self.helper_font_size.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.helper_font_size.setText('30')
        box.addWidget(self.helper_font_size)
        box.addWidget(QLabel("Font size"))
        self.show_all_button = QPushButton("Show All")
        self.show_all_button.setEnabled(False)
        self.show_all_button.pressed.connect(self._show_all)
        box.addWidget(self.show_all_button)

        group.setLayout(box)
        return group

    def _change_helper_font_size(self, size_string):
        if size_string.strip() != '':
            self._change_label_font_size(self.helper_window.title_label, size_string)
            self._change_label_font_size(self.helper_window.artist_label, size_string)
            self._change_label_font_size(self.helper_window.artist_label, size_string)
            self._change_label_font_size(self.helper_window.track_label, size_string)
            self._change_label_font_size(self.helper_window.time_label, size_string)
            self._change_label_font_size(self.helper_window.track_count_label, size_string, 2)
            logging.debug(f'HELPER FONT SIZE CHANGED TO: {size_string}')

    def _change_label_font_size(self, label, size_string, div_modifier=1):
        font = label.font()
        font.setPointSize(math.ceil(int(size_string) / div_modifier))
        label.setFont(font)

    def _prepare_infobox(self):
        group = QGroupBox("Info")
        box = QVBoxLayout()
        self.song_counter = QLabel("0/0")
        self.filename = QLabel("<>")
        self.title_label = QLabel("<>")
        self.title_label.setStyleSheet("font-weight: bold")
        self.artist_label = QLabel("<>")
        self.track_label = QLabel("<>")
        self.track_label.setStyleSheet("font-style: italic")
        box.addWidget(self.song_counter, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.filename, stretch=2, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.title_label, stretch=2, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.artist_label, stretch=2, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.track_label, stretch=2, alignment=Qt.AlignmentFlag.AlignCenter)
        group.setLayout(box)
        return group

    def _prepare_timebox(self):
        group = QGroupBox("Timer")
        box = QHBoxLayout()

        self.time_input = QLineEdit("20")
        self.time_input.setValidator(QIntValidator())
        self.time_input.setMaxLength(3)
        self.time_input.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        box.addWidget(self.time_input)

        self.timer = StopWatch(int(self.time_input.text()))
        self.timer.connect_timeout_fun(self._final_timer_event)
        self.timer.connect_tick_fun(self._tick_timer_event)

        self.random_sample_checkbox = QCheckBox("Random Start")
        self.random_sample_checkbox.setChecked(False)
        box.addWidget(self.random_sample_checkbox)

        self.time_label = QLabel('Countdown: ')
        box.addWidget(self.time_label)

        self.time_input.textChanged.connect(self._update_timeout)

        group.setLayout(box)
        return group

    def _update_timeout(self, new_timeout):
        logging.debug(f'New timeout:\t{new_timeout}')
        if not new_timeout:
            new_timeout = 0
            self.time_input.setText('0')
        self.timer.set_time(int(new_timeout))
        self._reset_time_label()

    def _final_timer_event(self):
        self.player.pause()

    def _tick_timer_event(self):
        self.time_label.setText(f'Countdown: {self.timer.time}')
        self.helper_window.time_label.setText(f'{self.timer.time}')

    def _reset_time_label(self):
        self.time_label.setText('Countdown: ')
        if self.window_check.isChecked():
            self._reset_helper_time_label()

    def _reset_helper_time_label(self):
        self.helper_window.time_label.setText(f'{self.timer.time}')

    def _prepare_buttons(self):
        group = QGroupBox("Controls")
        box = QHBoxLayout()
        button_box = QButtonGroup()
        self.previous_button = QPushButton("|<<")
        self.previous_button.pressed.connect(self._prev)
        self.play_button = QPushButton("▷")
        self.play_button.pressed.connect(self._play)
        self.pause_button = QPushButton("||")
        self.pause_button.pressed.connect(self._pause)
        self.next_button = QPushButton(">>|")
        self.next_button.pressed.connect(self._next)
        button_box.addButton(self.previous_button)
        button_box.addButton(self.play_button)
        button_box.addButton(self.pause_button)
        button_box.addButton(self.next_button)
        box.addWidget(self.previous_button)
        box.addWidget(self.play_button)
        box.addWidget(self.pause_button)
        box.addWidget(self.next_button)

        group.setLayout(box)
        return group

    def _play(self):
        if not self.no_used:
            self.library_handler.write_used()
        self.timer.reset()
        self.timer.start()
        if self.random_sample_checkbox.isChecked():
            self.player.play_random()
        else:
            self.player.play_from(0.0)

    def _get_and_set_track_info(self, track):
        track_info = self.library_handler[track]
        logging.debug(f"TRACK INFO: {track_info}")
        self.filename.setText(track)
        self.title_label.setText(track_info['anime'])
        self.artist_label.setText(track_info['artist'])
        self.track_label.setText(track_info['title'])

    def _set_track_info_helper(self, title, artist, track):
        self.helper_window.title_label.setText(title)
        self.helper_window.artist_label.setText(artist)
        self.helper_window.track_label.setText(track)

    def _set_track(self, track):
        logging.debug(f"TRACK: {track}")
        self.player.set_file(track)

    def _update_track_counter(self):
        index, total = self.player.get_index_and_total()
        self.song_counter.setText(f"{index + 1}/{total}")
        if self.window_check.isChecked():
            self.helper_window.track_count_label.setText(f"{index + 1}/{total}")

    def _next(self):
        self.reset_helper()
        track = self.player.next()
        self.timer.reset()
        self._reset_time_label()
        if track is not None:
            self._set_track(track)
            self._get_and_set_track_info(track)
            self._update_track_counter()

    def _prev(self):
        self.reset_helper()
        track = self.player.previous()
        self.timer.reset()
        self._reset_time_label()
        if track is not None:
            self._set_track(track)
            self._get_and_set_track_info(track)
            self._update_track_counter()

    def _pause(self):
        if self.player.is_active():
            self.timer.stop()
        else:
            self.timer.start()
        self.player.pause_unpause()

    def reset_helper(self):
        self.title_check.setChecked(False)
        self.artist_check.setChecked(False)
        self.track_check.setChecked(False)

    def _show_helper(self):
        self._change_helper_font_size(self.helper_font_size.text())
        if self.window_check.isChecked():
            self.title_check.setEnabled(True)
            self.artist_check.setEnabled(True)
            self.track_check.setEnabled(True)
            self.helper_font_size.setEnabled(True)
            self.show_all_button.setEnabled(True)
            self._set_track_info_helper("", "", "")
            self._update_track_counter()
            self._reset_helper_time_label()
            self.helper_window.show()
        else:
            self.title_check.setEnabled(False)
            self.artist_check.setEnabled(False)
            self.track_check.setEnabled(False)
            self.helper_font_size.setEnabled(False)
            self.show_all_button.setEnabled(False)
            self.helper_font_size.setText("")
            self.helper_window.close()

    def _show_title(self):
        if self.title_check.isChecked():
            self._set_track_info_helper(self.title_label.text(), self.helper_window.artist_label.text(),
                                        self.helper_window.track_label.text())
        else:
            self._set_track_info_helper("", self.helper_window.artist_label.text(),
                                        self.helper_window.track_label.text())

    def _show_artist(self):
        if self.artist_check.isChecked():
            self._set_track_info_helper(self.helper_window.title_label.text(), self.artist_label.text(),
                                        self.helper_window.track_label.text())
        else:
            self._set_track_info_helper(self.helper_window.title_label.text(), "",
                                        self.helper_window.track_label.text())

    def _show_track(self):
        if self.track_check.isChecked():
            self._set_track_info_helper(self.helper_window.title_label.text(), self.helper_window.artist_label.text(),
                                        self.track_label.text())
        else:
            self._set_track_info_helper(self.helper_window.title_label.text(), self.helper_window.artist_label.text(),
                                        "")

    def _show_all(self):
        self.title_check.setChecked(True)
        self.track_check.setChecked(True)
        self.artist_check.setChecked(True)
