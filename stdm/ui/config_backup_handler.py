
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
    QCoreApplication
)

from stdm.utils.logging_handlers import (
    MessageLogger
)

from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.profile import Profile
from stdm.composer.document_template import DocumentTemplate

from stdm.utils.util import (
    PLUGIN_DIR,
    documentTemplates,
    user_non_profile_views
)

from stdm.settings.registryconfig import RegistryConfig

PG_ADMIN = 'postgres'

class ConfigBackupHandler(QObject):
    update_status = pyqtSignal(str, int)

    def __init__(self):
        QObject.__init__(self, None)
        self._backup_step = 1
        self._stdm_config = StdmConfiguration.instance()

    def profiles(self) ->list:
        return self._stdm_config.profiles.values()

    def profile_templates(self, profile: Profile) ->dict:
        templates = documentTemplates()
        profile_tables = profile.table_names()
        p_templates = {}
        for name, filepath in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, filepath)
            if doc_temp.data_source is None:
                continue
            if doc_temp.data_source.referenced_table_name in profile_tables or \
                 doc_temp.data_source.name() in user_non_profile_views():
                if profile.name in p_templates:
                    p_templates[profile.name].append((doc_temp.name, filepath))
                else:
                    p_templates[profile.name] = []
                    p_templates[profile.name].append((doc_temp.name, filepath))
        return p_templates

    def _config_templates(self) ->list:
        config_templates = []
        for profile in self.profiles():
            templates = self.profile_templates(profile)
            config_templates.append(templates)
        return config_templates


    def backup_configuration(self, user: str, password: str, 
                             backup_folder: str, backup_mode:str) -> tuple[bool, str]:
        
        # Validate user authentication
        reg_config = RegistryConfig()
        settings = reg_config.read(['Host', 'Database', 'Port'])
        db_config =  DatabaseConfig(settings)
        db_params = db_config.read()

        db_con = DatabaseConnection(db_params.Host, db_params.Port, db_params.Database)
        db_con.User = User(user, password)

        valid, msg = db_con.validateConnection()

        if not valid:
            error = f'Authenticaion Failed!'
            return False, error

        db_backup_filename = self._make_db_backup_filename(db_con.Database)

        self._send_message('Backup process started, please wait...')

        db_backup_filepath = f'{backup_folder}/{db_backup_filename}'
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        self._send_message('Backing database...')
        status, msg = self._backup_database(db_con, PG_ADMIN, password, db_backup_filepath,
                                            backup_folder)
        if not status:
            return False, msg

        stdm_folder = '.stdm'
        config_file = 'configuration.stc'
        home_folder = QDir.home().path()
        config_filepath = f'{home_folder}/{stdm_folder}/{config_file}'
        config_backup_filepath = f'{backup_folder}/{config_file}'

        self._send_message('Backing configuration file...')
        self._backup_config_file(config_filepath, config_backup_filepath)

        self._send_message('Backing templates...')
        config_templates = self._config_templates()
        self._backup_templates(config_templates, backup_folder)

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

        self._send_message('Creating backup log file...')
        self._create_backup_log(backup_log, log_filepath)

        if backup_is_compressed:
            compressed_files = []
            compressed_files.append(db_backup_filepath)
            compressed_files.append(config_backup_filepath)
            compressed_files.append(log_filepath)
            backed_templates = self._backed_template_files(all_templates, backup_folder)
            compressed_files += backed_templates

            if self._compress_backup(db_con.Database, backup_folder, compressed_files):
                self._remove_compressed_files(compressed_files)
                
        self._send_message('Backup process completed successfully.')
        return True, ''

    def _profile_entities(self, profile: Profile) ->list[Entity]:
        entities = []
        for entity in profile.entities.values():
            if not entity.user_editable:
                continue
            entities.append(entity)
        return entities

    def _backup_config_file(self, src_config: str, dest_config: str):
        shutil.copyfile(src_config, dest_config)

    def _backup_templates(self, templates: list[dict[str, list[tuple[str, str]]]],
                           backup_folder: str):
        for profile_templates in templates:
            if len(profile_templates) == 0:
                return
            for template in list(profile_templates.values())[0]:
                template_filepath = template[1]
                filename = os.path.basename(template_filepath)
                backup_filepath = f'{backup_folder}/{filename}'
                shutil.copyfile(template_filepath, backup_filepath)

    def _backup_database(self, db_con: DatabaseConnection, user: str, password: str,
                         backup_filepath: str, backup_folder:str) ->tuple[bool, str]:

        base_folder = self._get_pg_base_folder()
        if base_folder == "":
            return False

        dump_tool = "\\bin\\pg_dump.exe"
        backup_util = f"{base_folder}{dump_tool}"

        script_file = "/scripts/dbbackup.bat"
        script_filepath = f"{PLUGIN_DIR}{script_file}"

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

        try:
            self._write_zip_file(files, zip_filepath)
        except BadZipfile:
            self.log_error('Failed to compress backup!')
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

    def _send_message(self, msg):
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

