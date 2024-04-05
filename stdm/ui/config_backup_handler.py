
"""
/***************************************************************************
Name                 : ConfigBackupHandler
Description          : Class to handle configuration backup
Date                 : 12/07/2023
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
import os
import errno
import shutil
import winreg
import json
import subprocess
from subprocess import Popen
from zipfile import ZipFile

from qgis.PyQt.QtCore import (
    QObject,
    pyqtSignal,
    QDateTime,
    QDir,
    QCoreApplication,
    QFile
)

from stdm.utils.logging_handlers import (
    EventLogger
)

from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.profile import Profile
from stdm.composer.document_template import DocumentTemplate

from stdm.utils.logging_handlers import (
    StdOutHandler,
    FileHandler,
    EventLogger
)

from stdm.utils.util import (
    PLUGIN_DIR,
    documentTemplates,
    user_non_profile_views
)

from stdm.settings.registryconfig import RegistryConfig

PG_ADMIN = 'postgres'

class ConfigBackupHandler(QObject):
    update_status = pyqtSignal(str, int)

    def __init__(self, log_mode: str='STDOUT'):
        QObject.__init__(self, None)
        self._log_mode = log_mode
        self._backup_step = 1
        self._stdm_config = StdmConfiguration.instance()

        self._logger = self._make_logger()

    def _make_logger(self)->EventLogger:
        if self._log_mode == 'FILE':
            dtime = QDateTime.currentDateTime().toString('ddMMyyyy_HH.mm')
            backup_log_file = '/.stdm/logs/config_backup_{}.log'.format(dtime)
            FileHandler.set_filepath(backup_log_file)
            return EventLogger(handler=FileHandler)

        if self._log_mode == 'STDOUT':
            return EventLogger(handler=StdOutHandler)



    def profiles(self) ->list:
        return self._stdm_config.profiles.values()

    def profile_templates(self, profile: Profile) ->dict:
        """
        Configuration *can* contain multiple profiles, so for
        each profile we get templates related to it.
        """
        templates = documentTemplates()
        profile_tables = profile.table_names()
        p_templates = {}
        template_count = 0
        for name, filepath in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, filepath)
            if doc_temp.data_source is None:
                continue
            if doc_temp.data_source.referenced_table_name in profile_tables or \
                 doc_temp.data_source.name() in user_non_profile_views():

                template_count += 1

                if profile.name in p_templates:
                    p_templates[profile.name].append((doc_temp.name, filepath))
                else:
                    p_templates[profile.name] = []
                    p_templates[profile.name].append((doc_temp.name, filepath))
        return p_templates, template_count

    def _config_templates(self) ->tuple[list, int]:
        config_templates = []
        count = 0
        for profile in self.profiles():
            templates, template_count = self.profile_templates(profile)
            count += template_count
            config_templates.append(templates)
        return config_templates, count

    def _log_error(self, msg: str):
        self._logger.log_error(msg)
        self._show_progress(msg)

    def _log_info(self, msg: str):
        self._logger.log_info(msg)
        self._show_progress(msg)


    def do_configuration_backup(self, user: str, password: str, 
                             backup_folder: str, backup_mode:str) -> tuple[bool, str]:
        
        # Validate user authentication
        reg_config = RegistryConfig()
        settings = reg_config.read(['Host', 'Database', 'Port'])
        db_config =  DatabaseConfig(settings)
        db_params = db_config.read()

        db_con = DatabaseConnection(db_params.Host, db_params.Port, db_params.Database)
        db_con.User = User(user, password)

        self._log_info("Verifying DB connection...")

        valid, msg = db_con.validateConnection()

        if not valid:
            error = f'DB authenticaion Failed!'
            self._log_error(error)
            return False, error

        self._log_info('Authentication successful.')

        db_backup_filename = self._make_db_backup_filename(db_con.Database)

        self._log_info('Backup process started...')

        db_backup_filepath = f'{backup_folder}/{db_backup_filename}'
        try:
            if not os.path.exists(backup_folder):
                self._log_info('Creating backup folder...')
                os.makedirs(backup_folder)
                self._log_info('Backup folder created.')
        except OSError as e:
            create_msg = f'Failed to create backup folder: `{db_backup_filepath}`'
            self._log_error(create_msg)
            return False, "Error creating backup folder."

        backup_name = f'Backing database: `{db_backup_filename}`.'
        backup_path = f'Backup path: {db_backup_filepath}'
        self._log_info(backup_name)
        self._log_info(backup_path)

        status, msg = self._backup_database(db_con, PG_ADMIN, password, db_backup_filepath,
                                            backup_folder)
        if not status:
            backup_msg = f'Failed to to backup database: {msg}'
            self._log_error(backup_msg)
            return False, msg

        self._log_info('Database backup... Done.')

        stdm_folder = '.stdm'
        config_file = 'configuration.stc'
        home_folder = QDir.home().path()
        config_filepath = f'{home_folder}/{stdm_folder}/{config_file}'
        config_backup_filepath = f'{backup_folder}/{config_file}'

        config_msg = f'Backing configuration file: `{config_backup_filepath}`'
        self._log_info(config_msg)

        config_backed, msg = self._backup_config_file(config_filepath, config_backup_filepath)

        if not config_backed:
            config_msg = f'Failed backing configuration file: error: {msg}' 
            self._log_error(config_msg)
            return False, config_msg

        self._log_info('Cofiguration file backup... Done.')


        self._log_info('Fetching profile templates...')
        config_templates, count = self._config_templates()

        templates_msg = f'[{count}]- templates found.'
        self._log_info(templates_msg)

        if len(config_templates) > 0:
            template_backed, msg = self._backup_templates(config_templates, backup_folder)
            if not template_backed:
                temp_msg = f'Failed to backup all template files: {msg}'
                self._log_error(temp_msg)
                return False, temp_msg

            self._log_info('Template files backup... Done.')

        log_dtime = self._dtime_str()
        log_filename = f'backuplog_{log_dtime}.json'
        log_filepath = f'{backup_folder}/{log_filename}'

        profiles = []
        all_templates = []
        for profile in self.profiles():
            entities = [e.short_name for e in self._profile_entities(profile)]

            for profile_templates in config_templates:
                templates = []
                for profile_name, template_names in profile_templates.items():
                    if profile_name == profile.name:
                        templates = [template[0] for template in template_names]

            profiles.append({'name':profile.name, 'entities': entities, 'templates': templates})

            all_templates += templates

        backup_is_compressed = False
        if backup_mode == 'ZIP-FILE':
            backup_is_compressed = True

        backup_log = self._make_log(profiles, db_con.Database,
                                     db_backup_filename, log_dtime, backup_is_compressed)

        log_file_msg = f'Creating backup log file: `{log_filepath}'
        self._log_info(log_file_msg)
        self._create_backup_log(backup_log, log_filepath)
        self._log_info('Log file created.')

        if backup_is_compressed:
            compressed_files = []
            compressed_files.append(db_backup_filepath)
            compressed_files.append(config_backup_filepath)
            compressed_files.append(log_filepath)
            backed_templates = self._backed_template_files(all_templates, backup_folder)
            compressed_files += backed_templates

            self._log_info('Compressing backup files...')
            if self._compress_backup(db_con.Database, backup_folder, compressed_files):
                self._log_info('Backup files compressed.')
                self._remove_compressed_files(compressed_files)
            else:
                self._log_error('Failed to compress backup files')
                
        self._log_info('Backup process completed successfully.')
        return True, ''

    def _profile_entities(self, profile: Profile) ->list[Entity]:
        entities = []
        for entity in profile.entities.values():
            if not entity.user_editable:
                continue
            entities.append(entity)
        return entities

    def _backup_config_file(self, src_config: str, dest_config: str)->tuple[bool, str]:
        try:
            shutil.copyfile(src_config, dest_config)
            return True, 'OK'
        except OSError as e:
            return False, e

    def _backup_templates(self, templates: list[dict[str, list[tuple[str, str]]]],
                           backup_folder: str)->tuple[bool, str]:
        try:
            for profile_templates in templates:
                if len(profile_templates) == 0:
                    return False, 'EMPTY'

                for template in list(profile_templates.values())[0]:
                    template_filepath = template[1]
                    filename = os.path.basename(template_filepath)
                    backup_filepath = f'{backup_folder}/{filename}'
                    tmp_copy = f'Backing template: `{template_filepath}`'
                    self._log_info(tmp_copy)
                    shutil.copyfile(template_filepath, backup_filepath)
        except OSError as e:
            return False, e

        return True, 'OK'
    

    def _backup_database(self, db_con: DatabaseConnection, user: str, password: str,
                         backup_filepath: str, backup_folder:str) ->tuple[bool, str]:

        base_folder = self._get_pg_base_folder()
        if base_folder == "":
            pg_folder = f'PostgreSQL folder: {base_folder} ... NOT found.'
            self._log_error(pg_folder)
            return False, pg_folder

        pg_folder = f'PostgreSQL folder: {base_folder} ... Found.'
        self._log_info(pg_folder)

        dump_tool = "\\bin\\pg_dump.exe"
        backup_util = f"{base_folder}{dump_tool}"

        if not os.path.exists(backup_util):
            util_msg = f'Backup utility: `{backup_util}` ... NOT found.'
            self._log_error(util_msg)
            return False, util_msg

        util_msg = f'Backup utility: `{backup_util}` ... Found.'
        self._log_info(util_msg)

        script_file = "/scripts/dbbackup.bat"
        script_filepath = f"{PLUGIN_DIR}{script_file}"

        if not os.path.exists(script_filepath):
            script_msg = f'Backup script: `{script_filepath}` ... NOT found. '
            self._log_error(script_msg)
            return False, script_msg

        script_msg = f'Backup script: `{script_filepath}` ... Found.'
        self._log_info(script_msg)

        self._log_info('Launching backup script in a subprocess.')

        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |=subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen([script_filepath, db_con.Database, 
            db_con.Host, str(db_con.Port), user, password, backup_folder, backup_util,
            backup_filepath], startupinfo=startup_info)

        stdout, stderr = process.communicate()
        process.wait()

        if process.returncode == 0:
            return True, ''
        else:
            return False, stderr

    def _backed_template_files(self, template_file_names: list, backup_folder: str) -> list[str]:
        temp_files = []
        for template_name in template_file_names:
            filename = f"{backup_folder}/{template_name}.sdt"
            temp_files.append(filename)
        return temp_files

    def _compress_backup(self, compressed_filename:str, backup_folder: str, 
                         files:list[str]) -> bool:
        """
        param: files
        type: list
        """
        dtime = self._dtime_str()
        zip_filepath = f"{backup_folder}/{compressed_filename}_{dtime}.zip"

        zip_msg = f'Zip filename: `{zip_filepath}`'
        self._log_info(zip_msg)
        
        try:
            self._write_zip_file(files, zip_filepath)
        except BadZipfile:
            return False

        return True

    def _write_zip_file(self, file_list: list, zip_file: str):
        with ZipFile(zip_file, 'w') as zf:
            for file in file_list:
                basename = os.path.basename(file)
                zf.write(file, arcname=basename)

    def _remove_compressed_files(self, files: list[str]):
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    def _make_log(self, profiles: list, db_name: str, db_backup_filename: str,
            log_dtime: str, is_compressed: bool) -> dict:

        backup_log = {'configuration':{'filename':'configuration.stc',
                                       'profiles':profiles,
               'database':{'name':db_name,
                           'backup_file':db_backup_filename},
               'created_on':log_dtime,
               'compressed':is_compressed
              }}

        return backup_log

    def _create_backup_log(self, log: dict, log_file: str):
        with open(log_file, 'w') as lf:
            json.dump(log, lf, indent=4)

    def _make_db_backup_filename(self, db_name:str) ->str:
        backup_filename = f'{db_name}_{self._dtime_str()}.backup'
        return backup_filename

    def _dtime_str(self) ->str:
        return QDateTime.currentDateTime().toString('ddMMyyyyHHmm')

    def _show_progress(self, msg):
        self.update_status.emit(msg, self._backup_step)
        QCoreApplication.processEvents()
        self._backup_step = self._backup_step + 1

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

