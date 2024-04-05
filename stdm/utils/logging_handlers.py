
"""
/***************************************************************************
Name                 : logging_handlers
Description          : Handlers for logging messages
Date                 : 01/06/2023
copyright            : (C) 2023 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import (
    QDir,
    QDateTime
)

class StreamHandler:
    def log(self, msg: str):
        raise NotImplementedError

class StdOutHandler(StreamHandler):
    def log(self, msg: str):
        print(msg)

class FileHandler(StreamHandler):
    _log_file = ''
    def __init__(self, filepath: str=''):
        if FileHandler._log_file =='':
            self.log_file = '{}{}'.format(QDir.home().path(),  filepath)
        else:
            self.log_file = FileHandler._log_file

    @staticmethod
    def set_filepath(filepath: str):
        FileHandler._log_file = '{}{}'.format(QDir.home().path(),  filepath)

    @staticmethod
    def init_logger(logfile: str):
        dtime = QDateTime.currentDateTime().toString('ddMMyyyy_HH.mm')
        home_path = QDir.home().path()
        FileHandler._log_file = f"{home_path}/.stdm/logs/{logfile}_{dtime}.log"
        return FileHandler

    def log(self, msg: str):
        with open(self.log_file, 'a') as lf:
            lf.write(msg)
            lf.write('\n')

class EventLogger:
    def __init__(self, handler:StreamHandler=StdOutHandler):
        self.stream_handler =  handler()

    def log_error(self, msg: str):
        log_msg = 'ERROR: {}'.format(msg)
        self.stream_handler.log(log_msg)

    def log_info(self, msg: str):
        log_msg = 'INFO: {}'.format(msg)
        self.stream_handler.log(log_msg)