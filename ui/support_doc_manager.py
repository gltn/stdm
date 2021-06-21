import os
import hashlib
import shutil
import requests
import json
from datetime import datetime

from stdm.settings import (
        current_profile
        )

from stdm.utils.util import (
        getIndex, 
        mapfile_section,
        get_working_mapfile
    )

from PyQt4.QtCore import (
    Qt,
    QObject,
    pyqtSignal,
    QFile,
    QFileInfo,
    SIGNAL,
    QSignalMapper,
    QThread
)

from stdm.data.pg_utils import (
    pg_create_supporting_document,
    pg_create_parent_supporting_document,
    get_lookup_data
)

from stdm.settings.registryconfig import (
        RegistryConfig,
        NETWORK_DOC_RESOURCE
)

class SupportDocManager(QObject):
    download_started = pyqtSignal(unicode)
    #Signal contains message type and message
    download_progress = pyqtSignal(int, unicode)

    download_counter = pyqtSignal(int)

    #Signal indicates True if the update succeeded, else False.
    download_completed = pyqtSignal(unicode)

    upload_started = pyqtSignal(unicode)
    upload_progress = pyqtSignal(int, unicode)
    upload_counter = pyqtSignal(int)
    upload_completed = pyqtSignal(unicode)

    INFORMATION, WARNING, ERROR = range(0, 3)

    def __init__(self, target_table, working_mapfile, parent=None):
        QObject.__init__(self, parent)

        self.target_table = target_table
        self.working_mapfile = working_mapfile
        self.columns = {}
        self.doc_type_columns = {}
        self.doc_path = {}
        self.main_table = ''
        self.parent_table = ''
        self.parent_support_table = ''
        self.doc_type_lookup_table = ''
        self.doc_type_lookup_data = {}
        self.src_key_field_name = ''
        self.doc_details = {}
        self.docs = []
        self.download_docs = False

        self.current_doc_name =''
        self.current_column_name = ''
        self.current_parent_id = -1
        self.current_profile = current_profile()

        self.kobo_url = ''
        self.kobo_username = ''
        self.kobo_password = ''

        self.download_log_file = ''
        self.upload_log_file = ''

        self.download_cache = []
        self.upload_cache = []

        self.setup()

    def append_doc(self):
        type_name = self.doc_type_columns[self.current_column_name] 
        doc = {'filename': self.current_doc_name,
                'parent_id': self.current_parent_id,
                'type_name': type_name,
                'doc_type_id':self.get_doc_id(type_name),
                'doc_column': self.columns[self.current_column_name]
                }
        self.docs.append(doc)
        self.current_doc_name =''
        self.current_column_name = ''
        self.current_parent_id = -1

    def get_mapfile_section(self, section):
        return mapfile_section(self.working_mapfile, section)

    def support_doc_column(self, column_name):
        return True if column_name in self.columns.keys() else False

    def get_doc_id(self, type_name):
        doc_id = -1
        for id, type in self.doc_type_lookup_data.items():
            if type == type_name:
                doc_id = id
                break
        return doc_id

    def setup(self):
        self.columns = self.get_mapfile_section('support_doc-column')
        if (len(self.columns) == 0):
            return

        self.download_docs = True

        self.doc_type_columns = self.get_mapfile_section('support_doc-type')
        self.doc_path = self.get_mapfile_section('support_doc-path')

        doc_map = self.get_mapfile_section('support_doc-map')

        self.main_table = doc_map['main_table']
        self.parent_table = doc_map['parent_table']
        self.parent_ref_column = doc_map['parent_ref_column']
        self.parent_support_table = doc_map['parent_support_table']
        self.doc_type_lookup_table = doc_map['doc_type_lookup_table']
        self.src_key_field_name = doc_map['src_key_field_column']

        self.doc_type_lookup_data = get_lookup_data(self.doc_type_lookup_table)

        log_path = os.path.dirname(os.path.abspath(self.working_mapfile))
        self.download_log_file = log_path+'\\'+self.target_table+'_download.json'

        self.download_cache = self.read_log(self.download_log_file)

        self.upload_log_file = log_path+'\\'+self.target_table+'_upload.json'
        self.upload_cache =  self.read_log(self.upload_log_file)

    def size(self):
        return len(self.docs)

    def start_download(self):
        self.download_started.emit('Download')
        self.download_files()
        self.download_completed.emit('Download')
        self.upload_files()
        #if self.upload_after:
            #self.upload_downloaded_files(downloaded_files)
        self.upload_completed.emit('Upload')

    def download_files(self):
        downloaded = []
        for n, doc in enumerate(self.docs):
            if n == 10:
                break
            short_filename = doc['filename']
            if short_filename == '':
                continue
            if short_filename in self.download_cache:
                continue
            self.download_progress.emit(SupportDocManager.INFORMATION, 'Downloading...'+short_filename)
            self.download_counter.emit(n+1)
            src_url = self.kobo_url+short_filename
            dest_filename = self.doc_path[doc['doc_column']]+'\\'+short_filename

            # First check if the file exists locally before downloading
            if not os.path.exists(dest_filename):
                self.kobo_download(src_url, dest_filename, self.kobo_username, self.kobo_password)

            downloaded.append({'doc_type':doc['type_name'], 'filename':short_filename})
        self.write_log(downloaded, self.download_log_file)
        return []

    def upload_files(self):
        self.upload_started.emit('Upload')
        uploaded = []
        for n, doc in enumerate(self.docs):
            if n == 10:
                break
            short_filename = doc['filename']
            if short_filename in self.upload_cache:
                continue
            self.upload_progress.emit(SupportDocManager.INFORMATION, 'Uploading...'+short_filename)
            self.upload_counter.emit(n+1)

            doc_type_id = doc['doc_type_id']
            full_filepath = self.doc_path[doc['doc_column']]+'\\'+short_filename
            parent_id = doc['parent_id']
            doc_type_name = doc['type_name']

            support_doc = self.make_supporting_doc_dict(full_filepath)

            result_obj = self.pg_create_supporting_doc(support_doc)
            new_doc_id = result_obj.fetchone()[0]

            parent_column = self.parent_table[3:]+'_id'

            self.create_supporting_doc(self.parent_support_table, new_doc_id,
                    parent_id, doc_type_id, parent_column)

            # copy file to STDM supporting document path
            new_doc_filename = support_doc['hashed_filename']

            self.create_new_support_doc_file(doc_type_id, doc_type_name, full_filepath, 
                    new_doc_filename, self.parent_table, self.current_profile)

            uploaded.append({'doc_type':doc['type_name'], 'filename':short_filename})
        self.write_log(uploaded, self.upload_log_file)

    def create_new_support_doc_file(self, doc_type_id, doc_type_name, doc_filename,
            new_filename, parent_table, profile):
        """
        :param doc_type_id: ID of the document type found in the lookup table
        :type doc_type_id: int
        :param doc_type_name: Name of the supporting document type
         found in the lookup table
        :type doc_type_name: str
        :param doc_filename: Name of the supporting file to upload (jpg)
        :type doc_filename: str
        :param new_filename: New filename hashed from doc_filename
        :type new_filename: str
        :param parent_table: Main table linked to this supporting document
        :type parent_table: str
        :param profile: Current profile object
        :type profile: Profile
        """
        try:
            self.reg_config = RegistryConfig()
            support_doc_path = self.reg_config.read([NETWORK_DOC_RESOURCE])
            doc_path = support_doc_path.values()[0]

            name, file_ext = os.path.splitext(doc_filename)
            doc_type_name = doc_type_name.replace(' ','_').lower()

            dest_path = doc_path+'/'+profile.name.lower()+'/'+parent_table+'/'+doc_type_name+'/'
            dest_filename = dest_path+new_filename+file_ext

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            shutil.copy(doc_filename, dest_filename)
        except:
            msg = "ERROR. Unable to copy file `{}` to destination!".format(doc_filename)
            self.download_progress.emit(SupportDocManager.ERROR, msg)

    def write_log(self, data, log_file):
        if len(data) == 0:
            return
        with open(log_file, 'a') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def read_log(self, log_file):
        """
        Returns a list of logged filenames
        :rtype: list
        """
        logs = [] 
        if not os.path.exists(log_file):
            return logs
        if os.path.getsize(log_file) == 0:
            return logs
        with open(log_file) as data_file:
            data = json.load(data_file)
            for log in data:
                logs.append(log['filename'])
        return logs

    def make_supporting_doc_dict(self, doc_name):
        doc_size = os.path.getsize(doc_name)
        path, filename = os.path.split(doc_name)
        ht = hashlib.sha1(filename.encode('utf-8'))
        document = {}
        document['support_doc_table'] = self.main_table
        document['creation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        document['hashed_filename'] = ht.hexdigest()
        document['source_entity'] = self.parent_table
        document['doc_filename'] = filename
        document['document_size'] = doc_size
        return document

    def pg_create_supporting_doc(self, support_doc):
        try:
            return pg_create_supporting_document(support_doc)
        except:
            msg = "ERROR: Unable to create record in table `{}`".support_doc['support_doc_table']
            self.download_progress.emit(SupportDocManager.ERROR, msg)

    def create_supporting_doc(self, table_name, new_doc_id, parent_id,
            doc_type_id, parent_column):
        try:
            pg_create_parent_supporting_document(table_name, new_doc_id, 
                    parent_id, doc_type_id, parent_column)
        except:
            msg = "ERROR: Unable to create record in table `{}`!".table_name
            self.download_progress.emit(SupportDocManager.ERROR, msg)

    def kobo_download(self, src_url, dest_filename, username, password):

        req = requests.get(src_url, auth=(username,password))

        with open(dest_filename, 'wb') as f:
            f.write(req.content)

        return req.status_code
