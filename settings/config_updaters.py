from collections import OrderedDict
from datetime import datetime, date, time
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtXml import QDomDocument
from stdm.data.configuration.columns import (
    DateColumn
)
from stdm.settings.config_utils import ConfigurationUtils

from stdm.data.configfile_paths import FilePaths
from stdm.settings.database_updaters import DatabaseUpdater

class ConfigurationUpdater(QObject):
    update_complete = pyqtSignal(QDomDocument)
    update_progress = pyqtSignal(str)

    def __init__(self, document, parent=None):
        QObject.__init__(self, parent)
        self.file_handler = FilePaths()
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )
        self.base_updater = ConfigurationVersionUpdater(
            document, self.log_file_path
        )
        self.document = document


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

    def version_updater(self, version):
        if version in self.base_updater.UPDATERS:
            return self.base_updater.UPDATERS[version]
        else:
            return None

    def exec_(self):
        version = self.version()
        updater = self.version_updater(version)


        if not updater is None:
            self.append_log(
                'Found updater - {}.'.format(updater)
            )
            updater_instance = updater(
                self.document, self.log_file_path
            )
            updater_instance.update_progress.connect(
                self.on_update_progress
            )
            updater_instance.update_complete.connect(
                self.on_update_complete
            )
            status, document, db_updater = updater_instance.exec_()
            updater_instance.update_complete.connect(
                self.on_update_complete
            )
            return status, document, db_updater
        else:

            self.append_log(
                'No updater found for this configuration '
                'with version number {}.'.format(version)
            )

    def on_update_progress(self, message):
        """
        A slot raised when an update progress signal
        is emitted in the updaters.
        :return:
        :rtype:
        """
        self.update_progress.emit(message)

    def on_update_complete(self, document):
        """
        A slot raised when an update complete
        signal is emitted in the last updater.
        :param document: The updated dom document
        :type document: QDomDocument
        :return:
        :rtype:
        """
        self.update_complete.emit(document)



class ConfigurationVersionUpdater(QObject):
    FROM_VERSION = None
    TO_VERSION = None
    UPDATERS = OrderedDict()
    NEXT_UPDATER = None
    update_complete = pyqtSignal(QDomDocument)
    update_progress = pyqtSignal(str)

    def __init__(self, document, log_file, parent=None):
        QObject.__init__(self, parent)
        self.document = document
        self.log_file = log_file
        self.config_utils = ConfigurationUtils(document)
        self.db_updater = DatabaseUpdater(document)


    @classmethod
    def register(cls):
        """
        Registers a class in UPDATERS dictionary.
        :param cls: The updater class to be registered.
        :type cls: Class
        :return:
        :rtype:
        """
        if len(ConfigurationVersionUpdater.UPDATERS) > 0:
            updaters = ConfigurationVersionUpdater.UPDATERS.values()
            previous_updater = updaters[len(updaters) - 1]
            previous_updater.NEXT_UPDATER = cls

        #Add our new updater to the collection
        ConfigurationVersionUpdater.UPDATERS[cls.FROM_VERSION] = cls

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

class ConfigVersionUpdater13(ConfigurationVersionUpdater):
    FROM_VERSION = 1.2
    TO_VERSION = 1.3

    VALIDITY_TAG = 'Validity'
    START_TAG = 'Start'
    END_TAG = 'End'
    MINIMUM = 'minimum'
    MAXIMUM = 'maximum'

    def _add_validity(self, str_element, tag_name, min_max, value):
        # Get validity node
        validities = str_element.elementsByTagName(
            self.VALIDITY_TAG
        )
        if validities.count() == 0:
            validity_el = self.document.createElement(
                self.VALIDITY_TAG
            )
            str_element.appendChild(validity_el)
        else:
            validity_node = validities.item(0)
            validity_el = validity_node.toElement()

        # Append start date
        if tag_name == self.START_TAG:
            start_tags = validity_el.elementsByTagName(
                self.START_TAG
            )
            if start_tags.count() == 0:
                start_el = self.document.createElement(
                    self.START_TAG
                )
                validity_el.appendChild(start_el)
            else:
                start_node = start_tags.item(0)
                start_el = start_node.toElement()

            # Set minimum or maximum
            start_el.setAttribute(min_max, str(value))

        # Append end date
        if tag_name == self.END_TAG:
            end_tags = validity_el.elementsByTagName(
                self.END_TAG
            )
            if end_tags.count() == 0:
                end_el = self.document.createElement(
                    self.END_TAG
                )
                validity_el.appendChild(end_el)
            else:
                end_node = end_tags.item(0)
                end_el = end_node.toElement()

            # Set minimum or maximum
            end_el.setAttribute(min_max, str(value))

    def exec_(self):
        """
        Run the current version update and starts
        the next version update.
        :return:
        :rtype:
        """

        self.append_log(
            'Started the backup the database version {}.'
                .format(self.FROM_VERSION)
        )

        self.db_updater.backup_database()

        self.append_log(
            'Successfully backed up up the database to version {}.'
                .format(self.TO_VERSION))

        social_tenure_elements = self.config_utils.\
            social_tenure_elements()
        # Emit start progress
        self.update_progress.emit(
            'Starting to update to configuration version {}'.format(
                self.TO_VERSION
            )
        )
        self.append_log(
            'Starting to update to configuration version {}'.format(
                self.TO_VERSION
            )
        )
        # sql_min = DateColumn.SQL_MIN
        sql_min = '1900-01-01'
        # sql_max = DateColumn.SQL_MAX
        sql_max = '3999-12-31'

        # Add validity node and elements
        for parent_node, str_element in social_tenure_elements.iteritems():
            self._add_validity(
                str_element, self.START_TAG, self.MINIMUM, sql_min
            )
            self._add_validity(
                str_element, self.START_TAG, self.MAXIMUM, sql_max
            )
            self._add_validity(
                str_element, self.END_TAG, self.MINIMUM, sql_min
            )
            self._add_validity(
                str_element, self.END_TAG, self.MAXIMUM, sql_max
            )
            parent_node.appendChild(str_element)


        # Initialize the next updater if it exists.
        if not self.NEXT_UPDATER is None:
            next_updater = self.NEXT_UPDATER(
                self.document, self.log_file
            )
            self.update_progress.emit(
                'Started updating configuration version {}'.format(
                    self.NEXT_UPDATER.TO_VERSION
                )
            )

            self.append_log(
                'Initializing {}'.format(
                    self.NEXT_UPDATER
                )
            )
            next_updater.exec_()
        #TODO add an if condition if the to version is the ...
        # latest version to be sure when emitting update_complete signal.
        else:

            self.update_complete.emit(self.document)

            self.append_log(
                'Successfully updated dom_document to version'.format(
                    self.TO_VERSION
                )
            )
            return True, self.document, self.db_updater

ConfigVersionUpdater13.register()
