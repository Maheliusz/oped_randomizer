import logging
import os

import eyed3
import pandas as pd


class LibraryHandler:
    def __init__(self, directory, library_filename='_library.csv', get_all=True):
        super().__init__()
        self.directory = directory
        self.used = self._get_used(directory)
        self.library_filename = library_filename

        audio_files = [x for x in os.listdir(directory) if x.endswith('.mp3')]
        library = self._read_library(directory, audio_files, get_all)
        self.library = library[library['anime'] != 'pass'].set_index('filename')
        logging.info(f'LIBRARY SIZE: {self.library.count()}')

        self.audio_files = [x for x in audio_files if x in self.library.index and x not in self.used]
        self.used = [x for x in self.used if x in self.library.index]
        logging.info(f'AUDIO FILES: {len(self.audio_files)}')

    def __getitem__(self, item):
        return self.library.loc[item]

    def _get_used(self, directory):
        try:
            used = list(open(os.path.join(directory, '_used.txt'), encoding='utf-8').read().splitlines())
            logging.info(f'FOUND {len(used)} USED ENTRIES')
            return used
        except:
            logging.warning("USED NOT FOUND")
            return []

    def write_used(self):
        with open(os.path.join(self.directory, '_used.txt'), 'w', encoding='utf-8') as usedfile:
            logging.info(f'WRITING {len(self.used)} ENTRIES TO USED')
            usedfile.write("\n".join(self.used))

    def _read_library(self, directory, audio_files, get_all):
        columns_to_read = ['filename', 'artist', 'title', 'anime']
        try:
            if not get_all:
                columns_to_read.append('take')
            return pd.read_csv(os.path.join(directory, self.library_filename), encoding='utf-8') \
                [columns_to_read].dropna()
        except:
            logging.warning("{} read failed: fallback to metadata from files".format(self.library_filename))
            data = []
            for name in audio_files:
                audiofile = eyed3.load(os.path.join(directory, name))
                data.append(
                    (
                        name,
                        audiofile.tag.artist,
                        audiofile.tag.title,
                        audiofile.tag.album
                    )
                )

            return pd.DataFrame(data, columns=columns_to_read)
