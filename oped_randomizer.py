import argparse
import datetime
import logging
import os
import random
import sys
import typing

import pandas as pd
import vlc
from PyQt6.QtCore import QTimer, QObject, QSize, Qt
from PyQt6.QtGui import QIcon, QIntValidator, QCloseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QCheckBox, QLineEdit, \
    QButtonGroup, QPushButton, QLabel, QSizePolicy


class StopWatch(QTimer):
    def __init__(self, parent: typing.Optional[QObject] = ...):
        super().__init__(parent)
        self.second_fun = None

    def connect_second(self, fun):
        self.second_fun = fun


class HelperWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.logger = logging.getLogger(type(self).__name__)
        self.setWindowTitle("Momo")
        self.setWindowIcon(QIcon(os.path.join('resources', 'momo.png')))

        self._layout = QVBoxLayout()

        self.title_label = self._create_label()
        self.title_label.setStyleSheet("font-weight: bold;text-decoration: underline;")
        self.artist_label = self._create_label()
        self.track_label = self._create_label()
        self.track_label.setStyleSheet("font-style: italic")

        self.text_font = self.artist_label.font()
        self.title_label.setFont(self.text_font)
        self.artist_label.setFont(self.text_font)
        self.track_label.setFont(self.text_font)
        self._layout.addWidget(self.title_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.artist_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.track_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)

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


class ControllerWindow(QWidget):
    def __init__(self, directory, player, library_handler):
        super().__init__()
        self.directory = directory
        self.logger = logging.getLogger(type(self).__name__)
        self.setWindowTitle("Shami")
        self.setWindowIcon(QIcon(os.path.join('resources', 'shami.png')))

        self.helper_window = HelperWindow(self)
        self.player = player
        self.library_handler = library_handler

        self._layout = QVBoxLayout()
        self.helper_windows_group = self._prepare_helper_windows_group()
        self.timebox = self._prepare_timebox()
        self.infobox = self._prepare_infobox()
        self.button_group = self._prepare_buttons()
        self._layout.addWidget(self.helper_windows_group)
        self._layout.addWidget(self.infobox, 1)
        self._layout.addWidget(self.timebox)
        self._layout.addWidget(self.button_group)
        self.setLayout(self._layout)
        self.setMinimumSize(800, 600)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.helper_window.close()
        return super(ControllerWindow, self).closeEvent(a0)

    def minimumSizeHint(self):
        return QSize(800, 600)

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
        box.addWidget(self.helper_font_size)
        box.addWidget(QLabel("Font size"))

        group.setLayout(box)
        return group

    def _change_helper_font_size(self, text):
        if text.strip() != '':
            font = self.helper_window.text_font
            font.setPointSize(int(text))
            self.helper_window.text_font = font
            self.helper_window.title_label.setFont(self.helper_window.text_font)
            self.helper_window.artist_label.setFont(self.helper_window.text_font)
            self.helper_window.track_label.setFont(self.helper_window.text_font)

    def _prepare_infobox(self):
        group = QGroupBox("Info")
        box = QVBoxLayout()
        self.filename = QLabel("<>")
        self.title_label = QLabel("<>")
        self.title_label.setStyleSheet("font-weight: bold")
        self.artist_label = QLabel("<>")
        self.track_label = QLabel("<>")
        self.track_label.setStyleSheet("font-style: italic")
        box.addWidget(self.filename, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.title_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.artist_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.track_label, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        group.setLayout(box)
        return group

    def _prepare_timebox(self):
        group = QGroupBox("Timer")
        box = QHBoxLayout()

        self.time_input = QLineEdit("30")
        self.time_input.setValidator(QIntValidator())
        self.time_input.setMaxLength(2)
        self.time_input.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        box.addWidget(self.time_input)

        self.timer = QTimer()
        self.timer.timeout.connect(self._final_timer_event)
        self.timer.setSingleShot(True)

        self.random_sample_checkbox = QCheckBox("Random Start")
        self.random_sample_checkbox.setChecked(False)
        box.addWidget(self.random_sample_checkbox)

        group.setLayout(box)
        return group

    def _final_timer_event(self):
        if self.player.media_player.get_state() == vlc.State.Playing:
            self.player.pause()

    def _second_timer_event(self):
        pass

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
        self.library_handler.write_used()
        self.timer.start(1000 * int(self.time_input.text()))
        if self.random_sample_checkbox.isChecked():
            self.player.play_random()
        else:
            self.player.play_from(0.0)

    def _get_and_set_track_info(self, track):
        track_info = self.library_handler.library.loc[track]
        self.logger.debug(f"TRACK INFO: {track_info}")
        self.filename.setText(track)
        self.title_label.setText(track_info['anime'])
        self.artist_label.setText(track_info['artist'])
        self.track_label.setText(track_info['title'])

    def _set_track_info_helper(self, title, artist, track):
        self.helper_window.title_label.setText(title)
        self.helper_window.artist_label.setText(artist)
        self.helper_window.track_label.setText(track)

    def _set_track(self, track):
        self.logger.debug(f"TRACK: {track}")
        self.player.set_file(track)

    def _next(self):
        self.reset_helper()
        track = self.player.next()
        self.timer.stop()
        if track is not None:
            self._set_track(track)
            self._get_and_set_track_info(track)

    def _prev(self):
        self.reset_helper()
        track = self.player.previous()
        self.timer.stop()
        if track is not None:
            self._set_track(track)
            self._get_and_set_track_info(track)

    def _pause(self):
        self.player.pause()

    def reset_helper(self):
        self.title_check.setChecked(False)
        self.artist_check.setChecked(False)
        self.track_check.setChecked(False)

    def _show_helper(self):
        if self.window_check.isChecked():
            self.title_check.setEnabled(True)
            self.artist_check.setEnabled(True)
            self.track_check.setEnabled(True)
            self.helper_font_size.setEnabled(True)
            self.helper_font_size.setText(str(self.helper_window.text_font.pointSize()))
            self._set_track_info_helper("", "", "")
            self.helper_window.show()
        else:
            self.title_check.setEnabled(False)
            self.artist_check.setEnabled(False)
            self.track_check.setEnabled(False)
            self.helper_font_size.setEnabled(False)
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


class Player:
    def __init__(self, audio_files, used, directory):
        self.directory = directory
        self.audio_files = audio_files
        self.used = used
        self.index = len(used)

        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.logger = logging.getLogger(type(self).__name__)

    def set_file(self, track):
        media = self.instance.media_new(os.path.join(self.directory, track))
        self.logger.info(f'MEDIA SET:{track}')
        self.media_player.set_media(media)
        media.parse()

    def next(self):
        self.index = self.index + 1 if len(self.audio_files) > 0 or self.index < len(self.used) else self.index
        try:
            next_track = self.used[self.index]
        except IndexError:
            if len(self.audio_files) == 0:
                self.logger.warning('NO NEXT TRACKS')
                return None
            next_track = random.choice(self.audio_files)
            self.audio_files.remove(next_track)
            self.used.append(next_track)
        self.logger.info(f'NEXT TRACK:{next_track}')
        return next_track

    def previous(self):
        self.index = self.index - 1 if self.index > 0 else self.index
        try:
            previous_track = self.used[self.index]
            self.logger.info(f'PREVIOUS TRACK:{previous_track}')
        except IndexError:
            self.logger.warning('NO PREVIOUS TRACKS')
            return None
        return previous_track

    def play_random(self):
        random_start = random.choice(list(map(lambda num: num / 10, range(1, 9))) + [0.0, ])
        self.play_from(random_start)

    def play_from(self, start):
        self.media_player.play()
        self.media_player.audio_set_mute(True)
        self.media_player.pause()
        self.media_player.set_position(start)
        self.media_player.audio_set_mute(False)
        self.media_player.play()

    def pause(self):
        self.media_player.pause()


class LibraryHandler:
    def __init__(self, directory):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.directory = directory
        audio_files = [x for x in os.listdir(directory) if x.endswith('.mp3')]
        library = pd.read_csv(os.path.join(directory, '_library.csv'), encoding='utf-8').dropna()
        self.library = library[library['anime'] != 'pass'].set_index('filename')
        self.logger.info(f'LIBRARY SIZE: {self.library.count()}')
        self.used = self._get_used(directory)
        self.audio_files = [x for x in audio_files if x in list(self.library.index) and x not in self.used]
        self.logger.info(f'AUDIO FILES: {len(self.audio_files)}')

    def _get_used(self, directory):
        try:
            used = list(open(os.path.join(directory, '_used.txt'), encoding='utf-8').read().splitlines())
            self.logger.info(f'FOUND {len(used)} USED ENTRIES')
            return used
        except:
            self.logger.warning("USED NOT FOUND")
            return []

    def write_used(self):
        with open(os.path.join(self.directory, '_used.txt'), 'w', encoding='utf-8') as usedfile:
            self.logger.info(f'WRITING {len(self.used)} ENTRIES TO USED')
            usedfile.write("\n".join(self.used))


class Application:
    def __init__(self, directory):
        self.qapp = QApplication([])
        self.library_parser = LibraryHandler(directory)
        self.player = Player(self.library_parser.audio_files, self.library_parser.used, directory)
        self.window = ControllerWindow(directory, self.player, self.library_parser)

    def run(self):
        self.window.show()
        sys.exit(self.qapp.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Application for OPED quiz')
    parser.add_argument('--dir', default=os.getcwd(), help='directory with music library')
    parser.add_argument('--log', default='warn', choices=['debug', 'info', 'warn', 'error', 'critical'],
                        help='logging level')
    parser.add_argument('--logfile', action='store_true', default=False)
    args = parser.parse_args()

    logging.basicConfig(level={
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARN,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }[args.log])
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    if args.logfile:
        now = datetime.datetime.now()
        fileLogHandler = logging.FileHandler(f'opedquiz_{now.strftime("%Y%m%dT%H%M%S")}.log', encoding='utf-8')
        fileLogFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M:%S")
        fileLogHandler.setFormatter(fileLogFormatter)
        logging.getLogger().addHandler(fileLogHandler)

    app = Application(args.dir)
    app.run()
