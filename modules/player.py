import logging
import os
import random

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData


class Player:
    def __init__(self, audio_files, used, directory):
        self.directory = directory
        self.audio_files = audio_files
        self.used = used
        self.index = len(used)
        self.currently_played = None

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(100)

    def set_file(self, track):
        self.media_player.setSource(QUrl.fromLocalFile(os.path.join(self.directory, track)))
        logging.info(f'MEDIA SET:{track}')

    def next(self):
        try:
            logging.debug(f'NEXT_INDEX:{self.index}')
            self.used[self.index]
            self.index = self.index + 1 if len(self.audio_files) > 0 or self.index < len(self.used) else self.index
            next_track = self.used[self.index]
        except IndexError:
            if len(self.audio_files) == 0:
                logging.warning('NO NEXT TRACKS')
                return None
            next_track = random.choice(self.audio_files)
        logging.info(f'NEXT TRACK:{next_track}')
        self.currently_played = next_track
        return next_track

    def previous(self):
        try:
            logging.debug(f'PREV_INDEX:{self.index}')
            self.index = self.index - 1 if self.index > 0 else self.index
            previous_track = self.used[self.index]
            logging.info(f'PREVIOUS TRACK:{previous_track}')
        except IndexError:
            logging.warning('NO PREVIOUS TRACKS')
            previous_track = None
        return previous_track

    def play_random(self):
        random_start = random.choice(list(map(lambda num: num / 10, range(1, 9))) + [0.0, ])
        self.play_from(random_start)

    def play_from(self, start):
        if self.currently_played in self.audio_files:
            self.audio_files.remove(self.currently_played)
            self.used.append(self.currently_played)
        if not self.media_player.source().isEmpty():
            self.media_player.setPosition(int(start * self.media_player.metaData().value(QMediaMetaData.Key.Duration)))
            self.media_player.play()

    def pause_unpause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        elif self.media_player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.media_player.play()

    def pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()

    def get_index_and_total(self):
        return self.index, len(self.used)+len(self.audio_files)
