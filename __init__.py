"""
/***************************************************************************
Name                 : Social Tenure Domain Model
Description          : QGIS Entry Point for Social Tenure Domain Model
Date                 : 04-01-2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
import sys
import os

import logging
from logging.handlers import TimedRotatingFileHandler

from PyQt4.QtGui import (
    QDesktopServices
)
from PyQt4.QtCore import (
    QDir
)

#Load third party libraries
third_party_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "third_party"))
font_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "third_party/fontTools"))

if third_party_dir not in sys.path:
    sys.path.append(third_party_dir)
    sys.path.append(font_dir)

#Setup logging
LOG_DIR = QDesktopServices.storageLocation(QDesktopServices.HomeLocation) \
               + '/.stdm/logs'
LOG_FILE_PATH = LOG_DIR + '/stdm.log'

def setup_logger():
    logger = logging.getLogger('stdm')
    logger.setLevel(logging.DEBUG)

    #Create log directory if it does not exist
    log_folder = QDir()
    if not log_folder.exists(LOG_DIR):
        status = log_folder.mkpath(LOG_DIR)

        #Log directory could not be created
        if not status:
            raise IOError('Log directory for STDM could not be created.')

    #File handler for logging debug messages
    file_handler = TimedRotatingFileHandler(LOG_FILE_PATH, when='D',
                                            interval=30, backupCount=4)
    file_handler.setLevel(logging.DEBUG)

    #Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    #Add handler to the logger
    logger.addHandler(file_handler)


def classFactory(iface):
    """
    Load STDMQGISLoader class.
    """
    setup_logger()

    from stdm.plugin import STDMQGISLoader
    return STDMQGISLoader(iface)
