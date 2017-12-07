# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Database Updater
Description          : Updates the STDM database to newer versions.
Date                 : 10/January/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from collections import OrderedDict
from datetime import datetime
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QApplication
from PyQt4.QtXml import QDomDocument

from stdm.data.pg_utils import (
    copy_from_column_to_another,
    remove_constraint,
    drop_column,
    add_constraint,
    pg_table_exists,
    table_column_names
)
from stdm.data.configfile_paths import FilePaths

from stdm.data.configuration.stdm_configuration import StdmConfiguration

class DatabaseUpdater(QObject):
    db_update_complete = pyqtSignal(QDomDocument)
    db_update_progress = pyqtSignal(str)
    def __init__(self, document, parent=None):
        QObject.__init__(self, parent)
        self.file_handler = FilePaths()
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )
        self.document = document

        self.base_updater = DatabaseVersionUpdater(
            self.log_file_path
        )

    def version(self):
        # Load items afresh
        # Check tag and version attribute first
        doc_element = self.document.documentElement()
        # Check version
        config_version = doc_element.attribute('version')

        if config_version:
            config_version = float(config_version)
            self.append_log(
                'Detected configuration version {}'.format(
                    config_version
                )
            )

        else:
            # Fatal error
            self.append_log('Error extracting version '
                            'number from the '
                            'configuration file.'
            )
        return config_version
    def version_updater(self):

        if self.version() in self.base_updater.UPDATERS:
            return self.base_updater.UPDATERS[self.version()]
        else:
            return None


    def append_log(self, info):
        """
        Append info to a single file
        :param info: update information to save to file
        :type info: str
        """
        info_file = open(self.log_file_path, "a")
        time_stamp = datetime.now().strftime(
            '%d-%m-%Y %H:%M:%S'
        )
        info_file.write('\n')
        info_file.write('{} - '.format(time_stamp))

        info_file.write(info)
        info_file.write('\n')
        info_file.close()

    def upgrade_database(self):
        """
        Updates database to the configuration version one step newer.
        :return:
        :rtype:
        """
        updater = self.version_updater()
        updater_instance = updater(self.log_file_path)
        updater_instance.db_update_progress.connect(self.db_update_progress)

        updater_instance.exec_()

    def on_update_progress(self, message):
        """
        A slot raised when an update progress signal
        is emitted in the updaters.
        :return:
        :rtype:
        """
        self.db_update_progress.emit(message)

    def on_update_complete(self, document):
        """
        A slot raised when an update complete
        signal is emitted in the last updater.
        :param document: The updated dom document
        :type document: QDomDocument
        :return:
        :rtype:
        """
        self.db_update_complete.emit(document)

    def on_db_update_progress(self, message):
        """
        A slot raised when the database update progress signal is emitted.
        :param message: The progress message
        :type message: String
        """
        self.db_update_progress.emit(message)

class DatabaseVersionUpdater(QObject):
    FROM_VERSION = None
    TO_VERSION = None
    UPDATERS = OrderedDict()
    NEXT_UPDATER = None
    db_update_complete = pyqtSignal()
    db_update_progress = pyqtSignal(str)

    def __init__(self, log_file, parent=None):
        """
        Database version updater that registers all database updaters.
        :param log_file: The log file object
        :type log_file: Object
        :param parent: The parent of the QObject
        :type parent: QWidget/NoneType
        """
        QObject.__init__(self, parent)
        self.config = StdmConfiguration.instance()
        self.log_file = log_file

    @classmethod
    def register(cls):
        """
        Registers a class in UPDATERS dictionary.
        :param cls: The updater class to be registered.
        :type cls: Class
        :return:
        :rtype:
        """
        if len(DatabaseVersionUpdater.UPDATERS) > 0:
            updaters = DatabaseVersionUpdater.UPDATERS.values()
            previous_updater = updaters[len(updaters) - 1]
            previous_updater.NEXT_UPDATER = cls

        #Add our new updater to the collection
        DatabaseVersionUpdater.UPDATERS[cls.FROM_VERSION] = cls

    def append_log(self, info):
        """
        Append info to a single file
        :param info: update information to save to file
        :type info: str
        """
        info_file = open(self.log_file, "a")
        time_stamp = datetime.now().strftime(
            '%d-%m-%Y %H:%M:%S'
        )
        info_file.write('\n')
        info_file.write('{} - '.format(time_stamp))

        info_file.write(info)
        info_file.write('\n')
        info_file.close()

class DatabaseVersionUpdater13(DatabaseVersionUpdater):
    FROM_VERSION = 1.2
    TO_VERSION = 1.3

    columns = {}
    def __init__(self, log_file):
        DatabaseVersionUpdater.__init__(self, log_file)

    def backup_database(self):
        """
        Backups up the database and emits signals on the progress.
        """
        self.append_log('Started the backup the database version {}.'
            .format(self.FROM_VERSION)
        )
        self.append_log('Successfully backed up up the database to version {}.'
            .format(self.TO_VERSION)
        )
        message = QApplication.translate(
            'DatabaseVersionUpdater13',
            'Successfully backed up the database version {}.'.format(
                self.TO_VERSION
            )
        )
        self.db_update_progress.emit(message)

    def update_str_table(self):
        """
        Updates the database to the next version.
        """
        for profile in self.config.profiles.values():

            social_tenure = profile.social_tenure
            if not pg_table_exists(social_tenure.name, False):
                return
            parties = social_tenure.parties
            if len(parties) < 1:
                return
            party = parties[0].short_name.lower()
            party_table = parties[0].name
            old_column = 'party_id'
            if not old_column in table_column_names(social_tenure.name):
                return
            new_column = '{}_id'.format(party)
            if old_column != new_column:
                copy_from_column_to_another(
                    str(social_tenure.name), old_column, new_column
                )

                add_constraint(str(social_tenure.name), new_column, party_table)

    def exec_(self):
        """
        Run the current version update and starts
        the next version update.
        :return:
        :rtype:
        """
        self.backup_database()
        self.update_str_table()
        # Initialize the next updater if it exists.
        if not self.NEXT_UPDATER is None:
            pass
            # if there is next updater, show progress
        #TODO add an if condition if the to version is the ...
        # latest version to be sure when emitting update_complete signal.
        else:

            self.db_update_complete.emit()

            self.append_log(
                'Successfully updated the database to version {}'.format(
                    self.TO_VERSION
                )
            )
            message = QApplication.translate(
                'DatabaseVersionUpdater13',
                'Successfully updated the database to version 1.5'
            )
            self.db_update_progress.emit(message)

DatabaseVersionUpdater13.register()
