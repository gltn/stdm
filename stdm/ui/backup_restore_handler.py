import os
import winreg
import json
import subprocess
from subprocess import Popen
from time import sleep

from qgis.PyQt.QtWidgets import (
    QApplication
)


from qgis.PyQt.QtCore import (
    QObject,
    pyqtSignal,
    QDir,
    QFile
)

from stdm.utils.logging_handlers import (
    StreamHandler,
    FileHandler,
    StdOutHandler,
    MessageLogger
)

from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.stdm_configuration import (
    StdmConfiguration
)
from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User
from stdm.data.pg_utils import _execute

from stdm.settings.registryconfig import (
    RegistryConfig,
    COMPOSER_TEMPLATE
)

from stdm.utils.util import (
    PLUGIN_DIR
)


backup_type = {True: 'COMPRESSED', False: 'FLAT_FILE'}

class BackupRestoreHandler(QObject):
    update_status = pyqtSignal(str, int)

    def __init__(self):
        QObject.__init__(self, None)
        self._backup_info_file = ""
        self._backup_info = None
        self._configuration = None 
        self._config_filename = ""
        self._profiles = []
        self._db_name = ""
        self._db_backup_file = ""
        self._backup_date = ""
        self._backup_type = ""
        self._backup_folder = ""
        self._restore_steps = 1

        self.logger = MessageLogger()

    def _init_handler(self, backup_info: dict):
        self._backup_info = backup_info
        self._configuration =  backup_info['configuration']
        self._config_filename = self.configuration['filename']
        self._profiles = self.configuration['profiles']

        self._db_name = self.configuration['database']['name']
        self._db_backup_file = self.configuration['database']['backup_file']
        self._backup_date = self.configuration['created_on']
        self._backup_type = backup_type[self.configuration['compressed']]
        self._backup_folder = os.path.dirname(self._backup_info_file)

    @property
    def backup_info_file(self):
        return self._backup_info_file

    @property
    def configuration(self) ->dict:
        return self._configuration
    
    @property
    def config_filename(self) ->str:
        return self._config_filename
    
    @property
    def profiles(self) ->list:
        return self._profiles
    
    @property
    def templates(self) ->list:
        temps = []
        for profile in self._profiles:
            temps.extend(profile['templates'])
        return temps

    @property
    def db_name(self) ->str:
        return self._db_name
    
    @db_name.setter
    def db_name(self, value):
        self._db_name = value
    
    @property
    def db_backup_file(self) ->str:
        return self._db_backup_file
    
    @property
    def backup_date(self) ->str:
        return self._backup_date

    @property
    def backup_type(self) ->str:
        return self._backup_type

    @property
    def backup_folder(self) ->str:
        return self._backup_folder


    def _read_templates(self, templates: list) ->dict:
        data = []
        for index, template in enumerate(templates):
            tmpl = {'name':template, 'found': True}
            data.append(tmpl)
        return data

    def read_backup_info_file(self, json_file: str) ->bool:
        self._backup_info_file = json_file
        backup_info = {}
        try:
            with open(json_file, "r") as file:
                backup_info = json.load(file)
        except OSError as e:
            self.logger.log_error(f"{type(e)}: {e}")
            return False

        return True if self._valid_backup_info(backup_info) else False

    def _valid_backup_info(self, backup_info: dict) ->bool:
        if len(backup_info) == 0:
            msg = f"Invalid backup info file"
            self.logger.log_error(msg)
            return False

        self._init_handler(backup_info)

        # find configuration file (.stc)
        config_stc_filepath = f'{self._backup_folder}/{self._config_filename}'
        if not os.path.exists(config_stc_filepath):
            self.logger.log_error(f"File missing: `{self._config_filename}` ")
            return False

        # Check if DB backup file exists
        db_backup_filepath = f'{self._backup_folder}/{self.db_backup_file}'
        if not os.path.exists(db_backup_filepath):
            self.logger.log_error(f"File missing: `{self.db_backup_file}`")
            return False

        # Check if template files exists
        for profile in self._profiles:
            profile['missing_templates'] = []
            for template in profile['templates']:
                temp_file_path = f"{self._backup_folder}/{template}{'.sdt'}"
                if not os.path.exists(temp_file_path):
                    profile['missing_templates'].append(template)

            for template in profile['missing_templates']:
                    self.logger.log_error(f"File missing: `{template}`")

        return True

    def restore_backup(self, username: str, password: str, db_name: str) ->bool:
        msg_title = 'Backup Restore'

        self.send_message('Authenticating user...')

        status, msg, conn_params = self._authenticate_user(username, password)
        if not status:
            error = f"Authentication failed! Incorrect password.\n\n {msg}"
            msg = QApplication.translate(msg_title, error)
            self.logger.log_error(error)
            return msg, False
        else:
            msg = f'Authentication successful.'
            self.logger.log_info(msg)

        self.db_name = db_name
        db_backup_filepath = f'{self.backup_folder}{"/"}{self.db_backup_file}'

        self.send_message('Check if database exists...')
        if self._find_database(db_name):
            error =f"Database `{db_name}` already exists! Restore aborted."
            msg = QApplication.translate(msg_title, error)
            self.logger.log_error(error)
            return msg, False
        else:
            msg = f'Database `{db_name}` not found.'
            self.logger.log_info(msg)

        # # STEP 0: Create DB
        self.send_message('Creating database...')
        if not self._create_database(conn_params, username, password,
                                     db_name):
            error = f'Failed to create database! Restore aborted.'
            msg = QApplication.translate(msg_title, error)
            self.logger.log_error(error)
            return msg, False
        else:
            msg = f'Database `{db_name}` created.'
            self.logger.log_info(msg)

        sleep(1) 

        # STEP 1: Restore database
        self.send_message('Restoring database...')
        if not self._restore_database(conn_params, username, password,
                                     db_name, db_backup_filepath):
            error = f"Failed to restore database!"
            msg =QApplication.translate(msg_title, error)
            return msg, False
        else:
            msg = f'Database restored successfully.'
            self.logger.log_info(msg)

        # STEP 2a: Copy configuration.stc to the 'configurations' folder
        self.send_message('Copying configruation file...')
        restore_location = f'{QDir.homePath()}/.stdm/configurations/{self.db_name}'
        dir = QDir(restore_location)
        if not dir.exists():
            dir.mkpath(restore_location)
            msg = f'Folder `{restore_location}` created.'
        else:
            msg = f'Folder `{restore_location}` already exists. Folder creation skipped.'
        self.logger.log_info(msg)

        src_config_filepath = f'{self.backup_folder}/{self.config_filename}'
        dest_config_filepath = f'{restore_location}/{self.config_filename}'

        if not QFile.exists(dest_config_filepath):
            if not QFile.copy(src_config_filepath, dest_config_filepath):
                error = f'Failed to copy configuration file. Restore aborted.'
                msg = QApplication.translate(msg_title, error) 
                self.logger.log_error(error)
                return msg, False
            else:
                msg = f'Configuration file copied successfully.'
                self.logger.log_info(msg)
        else:
            msg = f'Configuration file already exists. Copy skipped.'
            self.logger.log_info(msg)

        # STEP 2b: Copy log file to configurations folder
        src_logfile_filepath = f'{self.backup_info_file}'
        dest_logfile_filepath = f'{restore_location}/{os.path.basename(self.backup_info_file)}'

        self.send_message('Write log file to configurations folder...')
        if not QFile.exists(dest_logfile_filepath):
            # Update DB name. Restore might happend in a different database.
            self._backup_info['configuration']['database']['name'] = self._db_name

            self._create_backup_log(self._backup_info, dest_logfile_filepath)
            msg = f'Log file {[dest_logfile_filepath]} created successfully.'
            self.logger.log_info(msg)
        else:
            msg = f'Log file already exists. Copy skipped.'
            self.logger.log_info(msg)

        # STEP 3: Copy templates
        reg_config = RegistryConfig()
        templates_path = reg_config.read([COMPOSER_TEMPLATE])
        dest_path = templates_path[COMPOSER_TEMPLATE]

        self.send_message('Copying templates...')
        for template in self.templates:
            src_temp_filepath = f'{self.backup_folder}{"/"}{template}{".sdt"}'
            dest_temp_filepath = f'{dest_path}{"/"}{template}{".sdt"}'

            QFile.copy(src_temp_filepath, dest_temp_filepath)

        if len(self.templates) > 0:
            msg = f'Templates copied successfully.'
            self.logger.log_info(msg)
        else:
            msg = f'No templates found.'
            self.logger.log_info(msg)

        self.send_message('Restore process done.')
        msg = f'Restore process completed. Backup restored successfully.'
        self.logger.log_info(msg)

        return msg, True

    def _find_database(self, database: str) ->bool:
        msg = f'Finding database `{database}`...'
        self.logger.log_info(msg)

        sql = f"SELECT 1 AS found FROM pg_database WHERE datname = '{database}'"
        result = _execute(sql)
        cursor = result.cursor
        data = cursor.fetchall()
        return True if len(data) > 0 else False

    def _create_backup_log(self, log: dict, log_file: str):
        with open(log_file, 'w') as lf:
            json.dump(log, lf, indent=4)

    def _authenticate_user(self, user_name: str, password: str) ->tuple[bool, str, DatabaseConnection]:
        msg = f'Authenticating user `{user_name}`...'
        self.logger.log_info(msg)

        reg_config = RegistryConfig()
        settings = reg_config.read(['Host', 'Database', 'Port'])
        db_config =  DatabaseConfig(settings)

        db_param = db_config.read()
        db_conn = DatabaseConnection(db_param.Host, db_param.Port, db_param.Database)

        user = User(user_name, password)
        db_conn.User = user
        
        valid, msg = db_conn.validateConnection()

        return valid, msg, db_conn

    def _restore_database(self, db_conn_params: DatabaseConnection, user: str,
                         password: str, db_name: str, backup_filepath: str) -> bool:

        base_folder = self._get_pg_base_folder()
        if base_folder == "":
            return False

        restore_util =f'{base_folder}\\bin\\pg_restore.exe'

        script_filepath = f"{PLUGIN_DIR}/scripts/restoredb.bat"

        script_path = f'{PLUGIN_DIR}/scripts/'

        db_name = f"{db_name}"
        host=f"{db_conn_params.Host}"
        port = f"{db_conn_params.Port}"
        user = f"{user}"
        password = f"{password}"

        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |=subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen([script_filepath,
                                    db_name,
                                    host,
                                    port,
                                    user,
                                    password,
                                    restore_util,
                                    backup_filepath,
                                    script_path
                                    ],
                                    startupinfo=startup_info)

        stdout, stderr = process.communicate()
        process.wait()
        result_code = process.returncode
        
        return True
        
    def _create_database(self, db_conn_params: DatabaseConnection, user: str,
                         password: str, db_name: str) ->bool:

        msg = f'Creating database `{db_name}`...'
        self.logger.log_info(msg)

        base_pg_folder =  self._get_pg_base_folder()
        if base_pg_folder == "":
            return False
        
        createdb_util = f'{base_pg_folder}\\bin\createdb.exe'
        createdb_script_filepath = f'{PLUGIN_DIR}/scripts/createdb.bat'

        script_path = f'{PLUGIN_DIR}/scripts/'
        db_name = f"{db_name}"
        host = f"{db_conn_params.Host}"
        port =  f"{db_conn_params.Port}"
        user = f"{user}"
        password = f"{password}"

        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |=subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen([createdb_script_filepath,
                                    db_name,
                                    host,
                                    port,
                                    user,
                                    password,
                                    createdb_util,
                                    script_path
                                    ],
                                    startupinfo=startup_info)

        stdout, stderr = process.communicate()
        process.wait()
        result_code = process.returncode

        return True

    def send_message(self, msg: str):
        self.update_status.emit(msg, self._restore_steps)
        self._restore_steps = self._restore_steps + 1
        QApplication.processEvents()

    def _get_pg_base_folder(self) ->str:
            """
            PostgrSQL base folder
            """
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\PostgreSQL\\Installations\\")
            pg_base_value = ""
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)

                    for j in range(winreg.QueryInfoKey(subkey)[1]):
                        name, value,_ = winreg.EnumValue(subkey, j)
                        if name == "Base Directory":
                            pg_base_value = value
                            break
                    if not pg_base_value == "":
                        break
                    winreg.CloseKey(subkey)
                except OSError:
                    pass
            winreg.CloseKey(reg_key)

            return pg_base_value