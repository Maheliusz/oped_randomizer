import logging
import os

import pandas as pd
from eyed3 import mp3


class LibraryHandler:
    def __init__(self, directory):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.directory = directory
        audio_files = [x for x in os.listdir(directory) if x.endswith('.mp3')]
        library = self._read_library(directory, audio_files)
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

    def _read_library(self, directory, audio_files):
        try:
            return pd.read_csv(os.path.join(directory, '_library.csv'), encoding='utf-8').dropna()
        except FileNotFoundError:
            self.logger.warning("'_library.csv' FILE NOT FOUND: fallback to metadata from files")
            paths = [(name, os.path.join(directory, name)) for name in audio_files]
            return pd.DataFrame(
                [(x[0], mp3.Mp3AudioFile(x[1]).tag.artist, mp3.Mp3AudioFile(x[1]).tag.title,
                  '.'.join(x[0].split('.')[:-1]), 1) for x in paths],
                columns=['filename', 'artist', 'title', 'anime', 'pick'])
