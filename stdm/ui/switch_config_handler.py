import os
import json
import glob
import time
import hashlib
from shutil import copyfile

from qgis.PyQt.QtWidgets import (
    QApplication
)

from qgis.PyQt.QtCore import (
    QFile,
    QDir,
    QDateTime
)

from stdm.utils.logging_handlers import (
    MessageLogger
)
from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.profile import Profile
from stdm.data.configuration.entity import Entity
from stdm.composer.document_template import DocumentTemplate

from stdm.settings.registryconfig import RegistryConfig

from stdm.utils.util import(
    documentTemplates,
    user_non_profile_views
)

class SwitchConfigHandler():
    def __init__(self):
        self._config_info_file = ''
        self._config_info = None
        self._configuration = None
        self._config_filename = ""
        self._profiles = []
        self._db_name = ""
        self._backup_date = ""
        self._db_backup_file = ""
        self.logger = MessageLogger()

        reg_config = RegistryConfig()
        settings = reg_config.read(['Host', 'Database', 'Port'])
        self.db_config      = DatabaseConfig(settings)
        self.db_param = self.db_config.read()

        self._active_config_name = self.db_param.Database 

    @property
    def config_info_file(self) ->str:
        return self._config_info_file

    @property
    def active_config_name(self) ->str:
        return self._active_config_name

    @property
    def config_store_folder(self) ->str:
        return self._config_store_folder

    @property
    def config_info(self) ->str:
        return self._config_info
    
    @property
    def configuration(self) ->dict:
        return self._configuration
    
    @property
    def config_filename(self) ->str:
        return self._config_filename

    @property
    def profiles(self) ->list:
        return self._profiles
    
    def templates(self) ->list:
        temps = []
        for profile in self._profiles:
            temps.extend(profile['templates'])
        return temps

    @property
    def db_name(self) ->str:
        return self._db_name
    
    @property
    def db_backup_file(self) ->str:
        return self._db_backup_file
    
    @property
    def backup_date(self) ->str:
        return self._backup_date
    
    def _init_handler(self, config_info: dict):
        self._config_info = config_info
        self._configuration = config_info['configuration']
        self._config_filename = self._configuration['filename']
        self._profiles = self._configuration['profiles']
        self._db_name = self._configuration['database']['name']
        self._backup_date = self._configuration['created_on']
        self._db_backup_file = self._configuration['database']['backup_file']

    def read_config_info_file(self, config_info_file: str) ->bool:
        self._config_info_file = config_info_file
        self._config_store_folder = os.path.dirname(config_info_file)

        config_info = {}
        try:
            with open(config_info_file, "r") as file:
                config_info = json.load(file)
        except OSError as e:
            self.logger.log_error(f'{type(e)} : {e}')
            return False

        return True if self._config_info_is_valid(config_info) else False

    def _config_info_is_valid(self, config_info: dict) ->bool:
        if len(config_info) == 0:
            self.logger.log_error(f"Empty config info. Process aborted.")
            return False

        # We check if we have a configuration.stc file
        config_stc_filepath = f'{self.config_store_folder}/{self.config_filename}'
        if not os.path.exists(config_stc_filepath):
            msg = f'Configuration file missing: `{self.configuration}. Switch aborted'
            self.logger.log_error(msg)
            return False

        self._init_handler(config_info)
        return True


    def _tag_origin(self) ->bool:
        # STEP 0: Backup original configuration file
        print(self.config_info_file)
        print(self.config_store_folder)

        tags_folder = f'{self.config_store_folder}/.tags'
        dir = QDir(tags_folder)
        if not dir.exists():
            dir.mkpath(tags_folder)
            msg = f'Folder `{tags_folder}` created.'
            self.logger.log_info(msg)

        current_config = f'{self.config_store_folder}/{self.config_filename}'

        # STEP 1: Lets find the latest configuration in the tags folder
        latest_tagged_config = self._get_latest_config(tags_folder)
        latest_tagged_config_filepath = f'{tags_folder}/{latest_tagged_config}'

        tagging_ok = True

        if latest_tagged_config == '':
            tagging_ok = self._tag_file(current_config)
        else:
            if not self._configs_are_same(latest_tagged_config_filepath, current_config):
                tagging_ok = self._tag_file(current_config)

        if not tagging_ok:
            msg = f'Failed to tag origin file. Switch aborted'
            self.logger.log_error(msg)
            return False

        return True

    def _tag_master(self) -> bool:
        # STEP 2: Check if te 'master' config has a entry in the config
        # store location. Master config is the configuration that is currently
        # in use
        config_filename = 'configuration.stc'
        origin_master_dir = f'{QDir.homePath()}/.stdm/configurations/{self.active_config_name}'

        m_dir = QDir(origin_master_dir)
        if not m_dir.exists():
            m_dir.mkpath(origin_master_dir)
            msg = f'Created origin master folder: `{origin_master_dir}.'
            self.logger.log_info(msg)

        master_config_tags_folder  = f'{origin_master_dir}/.tags'
        t_dir = QDir(master_config_tags_folder)
        if not t_dir.exists():
            t_dir.mkpath(master_config_tags_folder)
            msg = f'Created origin master tag folder: `{master_config_tags_folder}.'
            self.logger.log_info(msg)

        active_master_filepath = f'{QDir.homePath()}/.stdm/{config_filename}'
        origin_master_filepath = f'{origin_master_dir}/{config_filename}'

        # No origin master - make a copy and return
        if not QFile.exists(origin_master_filepath):
            copyfile(active_master_filepath, origin_master_filepath)
            self.logger.log_info('Copied active master to origin master.')
            if not self._log_file_exists(origin_master_dir):
                self._make_logfile(origin_master_dir)
            return True

        if not self._configs_are_same(active_master_filepath, origin_master_filepath):
                tagging_ok = self._tag_file(origin_master_filepath)
                if not tagging_ok:
                    msg = f'Failed to tag original master. Switch aborted.'
                    self.logger.log_error(msg)
                    return False

        # Copy active master to origin
        copyfile(active_master_filepath, origin_master_filepath)

        copied = True

        return True if copied else False

    def switch_config(self):
        if not self._tag_origin():
            return False

        if not self._tag_master():
            return False
        
        self._switch_db()

        switch_result = self._perform_switch()

        if switch_result:
            msg = f'Configuration switched successfully.'
            self.logger.log_info(msg)
        else:
            msg = f'Failed to switch config. Switch aborted.'
            self.logger.log_error(msg)

        return switch_result

    def _switch_db(self):
        host = self.db_param.Host
        port = self.db_param.Port
        database_name = self.db_name
        db_conn = DatabaseConnection(host, port, database_name)
        self.db_config.write(db_conn)

        msg = f'Database`{self.db_name}` switched successfully.'
        self.logger.log_info(msg)

    def _perform_switch(self) ->bool:
        config_filename = 'configuration.stc'
        new_config = f'{self.config_store_folder}/{config_filename}'
        active_config = f'{QDir.homePath()}/.stdm/{config_filename}'
        copyfile(new_config, active_config)
        return True

    def _get_master_config_name(self):
        # Master config name is the database name
        #db_config = DatabaseConfig()
        db_param = self.db_config.read()
        return db_param.Database

    def _get_latest_config(self, tags_folder: str) ->str:
        tags = os.path.join(tags_folder, "*.stc")
        tagged_files = glob.glob(tags)
        if len(tagged_files) == 0:
            msg =f'No tagged configurations in folder {tags_folder}'
            self.logger.log_info(msg)
            return ""

        # We assume last modified file is the latest file
        file_stats = []
        for tagged_file in tagged_files:
            file_stat = os.stat(tagged_file)
            file_age = time.time() - file_stat.st_mtime
            file_name = os.path.basename(tagged_file)
            file_stats.append({'filename':file_name, 'age':float(format(file_age, '.4f'))})

        # Sort by age
        sorted_file_stats = sorted(file_stats, key=lambda x: x['age'])
        return sorted_file_stats[0]['filename']

    def _tag_file(self, src_file: str) ->bool:
        if src_file == '':
            return False

        store_location = f'{os.path.dirname(src_file)}'
        basefile_no_ext = os.path.basename(src_file).split('.')[0]
        tagged_file = f'{basefile_no_ext}_{self._dtime_str()}.stc'

        dest_file = f'{store_location}/.tags/{tagged_file}'
        result = QFile.copy(src_file, dest_file)

        return result

    def _configs_are_same(self, first_config: str, second_config: str) ->bool:
        first_hash = self._get_file_hash(first_config)
        second_hash = self._get_file_hash(second_config)
        return True if first_hash == second_hash else False

    def _log_file_exists(self, config_path: str) ->bool:
        folder = os.path.join(config_path, '*.json')
        json_files = glob.glob(folder)
        return True if len(json_files) > 0 else False

    def _make_logfile(self, config_path: str):
        log_dtime = self._dtime_str()
        log_filename = f'backuplog_{log_dtime}.json'
        log_filepath = f'{config_path}/{log_filename}'
        #log_filepath = f'{QDir.homePath()}/.stdm/configurations/{self.active_config_name}/{log_filename}'

        profiles = []
        all_templates = []

        stdm_config = StdmConfiguration.instance()
        config_templates = []

        for profile in stdm_config.profiles.values():
            entities = [e.short_name for e in self._profile_entities(profile)]

            templates = self._profile_templates(profile)
            config_templates.append(templates)
            for profile_templates in config_templates:
                templates = []
                for profile_name, template_names in profile_templates.items():
                    if profile_name == profile.name:
                        templates = [template[0] for template in template_names]
            profiles.append({'name': profile.name, 'entities': entities, 'templates': templates})
            all_templates += templates


        config_log  = {'configuration':{'filename':'configuration.stc',
                                       'profiles':profiles,
               'database':{'name':self.active_config_name,
                           'backup_file':log_filename},
               'created_on':QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm'),
               'compressed':False
              }}
                
        with open(log_filepath, 'w') as lf:
            json.dump(config_log, lf, indent=4)


    def _profile_entities(self, profile: Profile) ->list[Entity]:
        entities = []
        for entity in profile.entities.values():
            if not entity.user_editable:
                continue
            entities.append(entity)
        return entities

    def _profile_templates(self, profile: Profile) ->dict:
        templates = documentTemplates()
        profile_tables = profile.table_names()
        profile_templates = {}
        for name, filepath in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, filepath)
            if doc_temp.data_source is None:
                continue
            if doc_temp.data_source.referenced_table_name in profile_tables or \
                 doc_temp.data_source.name() in user_non_profile_views():
                if profile.name in profile_templates:
                    profile_templates[profile.name].append((doc_temp.name, filepath))
                else:
                    profile_templates[profile.name] = []
                    profile_templates[profile.name].append((doc_temp.name, filepath))
        return profile_templates

    def _get_file_hash(self, filename):
        h = hashlib.sha256()
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def _dtime_str(self):
        return QDateTime.currentDateTime().toString('ddMMyyyyHHmm')



            

