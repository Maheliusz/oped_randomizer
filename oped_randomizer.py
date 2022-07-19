import argparse
import datetime
import logging
import os
import sys

from PyQt6.QtWidgets import QApplication

from modules.controller import ControllerWindow
from modules.library import LibraryHandler
from modules.player import Player


class Application:
    def __init__(self, directory, do_not_write_used):
        self.qapp = QApplication([])
        self.library_parser = LibraryHandler(directory)
        self.player = Player(self.library_parser.audio_files, self.library_parser.used, directory)
        self.window = ControllerWindow(directory, self.player, self.library_parser, do_not_write_used)

    def run(self):
        self.window.show()
        sys.exit(self.qapp.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Application for OPED quiz')
    parser.add_argument('--dir', default=os.getcwd(), help='directory with music library')
    parser.add_argument('--library', default='_library.csv', help='name of library file')
    parser.add_argument('--log', default='warn', choices=['debug', 'info', 'warn', 'error', 'critical'],
                        help='logging level')
    parser.add_argument('--logfile', action='store_true', default=False,
                        help='name of file to store logs (else logs are output to console)')
    parser.add_argument('--noused', action='store_true', default=False, help='ignore used file')
    parser.add_argument('--all', action='store_true', default=False,
                        help='load all entries from library, ignore "taken"')
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

    app = Application(args.dir, args.noused)
    app.run()
