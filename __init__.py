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

# Import qgis.core so that the correct SIP versions are loaded in tests
from qgis.core import *

from PyQt4.QtGui import (
    QDesktopServices
)
from PyQt4.QtCore import (
    QDir,
    QFile,
    QTextStream,
    QIODevice
)

#Load third party libraries
third_party_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "third_party"))
font_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "third_party/fontTools"))

if third_party_dir not in sys.path:
    sys.path.append(third_party_dir)
    sys.path.append(font_dir)

#Root to the path plugin directory
#USER_PLUGIN_DIR = QDesktopServices.storageLocation(QDesktopServices.HomeLocation) \
#            + '/.stdm'
USER_PLUGIN_DIR = 'C:\Users\SOLOMON\.stdm'

#Setup logging
LOG_DIR = u'{0}/logs'.format(USER_PLUGIN_DIR)
LOG_FILE_PATH = LOG_DIR + '/stdm_log'


def setup_logger():
    from stdm.settings.registryconfig import debug_logging

    logger = logging.getLogger('stdm')
    logger.setLevel(logging.ERROR)

    # Create log directory if it does not exist
    log_folder = QDir()
    if not log_folder.exists(LOG_DIR):
        status = log_folder.mkpath(LOG_DIR)

        # Log directory could not be created
        if not status:
            raise IOError('Log directory for STDM could not be created.')

    # File handler for logging debug messages
    file_handler = TimedRotatingFileHandler(LOG_FILE_PATH, when='D',
                                            interval=1, backupCount=14)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(file_handler)

    # Enable/disable debugging. Defaults to ERROR level.
    lvl = debug_logging()
    if lvl:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.ERROR)


def copy_core_configuration():
    """
    Copies the basic STDM configuration to the user directory if there is none.
    """

    #check network config exist
    core_config_path = read_network_path()
    if not QFile.exists(core_config_path):
        return
    else:

    # if not core_config_path:
    #     core_config_path = u'{0}/templates/configuration.stc'.format(
    #         os.path.dirname(__file__)
    #     )
    #
    #     #Exit if the core configuration does not exist
    #     if not QFile.exists(core_config_path):
    #         return

        #File name of previous configuration
        v1_1_config_path = u'{0}/stdmConfig.xml'.format(USER_PLUGIN_DIR)

        #Only copy the new one if there is no copy of the previous version
        # since the version updater will automatically handle the upgrade.
        if QFile.exists(v1_1_config_path):
            #Version update will handle the migration
            return

        #Copy config assuming that the plugin user folder has no previous
        # configuration.
        conf_file = QFile(core_config_path)
        conf_dest = u'{0}/configuration.stc'.format(USER_PLUGIN_DIR)

        copy_status = conf_file.copy(conf_dest)


def read_network_path():
    """get the netowrk config file location"""
    network_config = QFile(os.path.join(USER_PLUGIN_DIR,
                                        'network_path.txt'))

    if network_config.open(QIODevice.ReadOnly):
        stream = QTextStream(network_config)
        f_path = stream.readLine()
        if f_path:
            return f_path


def classFactory(iface):
    """
    Load STDMQGISLoader class.
    """
    setup_logger()

    #Copy the basic configuration to the user folder if None exists
    copy_core_configuration()

    from stdm.plugin import STDMQGISLoader
    return STDMQGISLoader(iface)
