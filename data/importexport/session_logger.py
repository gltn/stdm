import os
from PyQt4.QtCore import (
    QUrl,
    QEventLoop,
)
from stdm.settings import (
    get_primary_mapfile,
    current_profile
)
from datetime import datetime
import json

class SessionLogger(object):
    """
    This class for logging info about:
        import data from CSV,
        Download Documents from KoBO,
        Upload Certificates from local path to STDM.
    for use in STDM units:
        ui/support_doc_manager.py,
        ui/import_data.py,
        ui/document_uploader.py
    """
    def __init__(self, sessiontype):
        self.sessiontype = sessiontype
        self.sessionid = ( sessiontype 
                         + datetime.now().strftime('_%Y%m%d%H%M%S%f')
                         )
        self.current_profile = current_profile()

        self.cache_initialrecords = []
        self.cache_successrecords = []
        self.cache_failedrecords = []

        self.root = 'c:\temp' #to be replaced later by config value
        if os.path.exists(get_primary_mapfile()):
            mapfile_path = os.path.dirname(get_primary_mapfile())
            if os.path.exists(mapfile_path):
                self.root = mapfile_path + '\sessions'
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.file_basicinfo = ( self.root 
                              + '\\'
                              + self.sessionid
                              + '_basicinfo.log'
                              )
        self.file_records = ( self.root 
                              + '\\'
                              + self.sessionid
                              + '_initialrecords.log'
                              )
        self.file_success = ( self.root 
                            + '\\'
                            + self.sessionid
                            + '_success.log'
                            )
        self.file_failed =  ( self.root 
                            + '\\'
                            + self.sessionid
                            + '_failed.log'
                            )

    def basicinfo_init(self, starttime, recordscount, datasource):
        self.starttime = starttime
        self.recordscount = recordscount
        self.datasource = datasource
        self.status = 'Corrupted'
        self.endtime = starttime
        self.log_write_basicinfo()

    def basicinfo_updatestatus(self, status, endtime):
        self.status = status
        self.endtime = endtime
        self.log_write_basicinfo()

    def success_cerupload_append(self, filename, hashedfilename,
            supporting_document_id, parent_table, parent_column,
            parent_id, support_doc_table, parent_supporting_doc_id):
            
        self.cache_successrecords.append(
            {
                'filename': filename,
                'hashedfilename': hashedfilename,
                'supporting_document_id': str(supporting_document_id),
                'parent_table': parent_table,
                'parent_id': str(parent_id),
                'support_doc_table': support_doc_table,
                'parent_column': parent_column,
                'parent_supporting_doc_id': str(parent_supporting_doc_id),
            }
        )
        self.write_logfile(
            self.cache_successrecords,
            self.file_success
        )

    def failed_cerupload_append(self, filename, hashedfilename,
            supporting_document_id, parent_table, parent_column,
            parent_id, support_doc_table, parent_supporting_doc_id,
            errormessage):
            
        self.cache_failedrecords.append(
            {
                'filename': filename,
                'hashedfilename': hashedfilename,
                'supporting_document_id': str(supporting_document_id),
                'parent_table': parent_table,
                'parent_id': str(parent_id),
                'support_doc_table': support_doc_table,
                'parent_column': parent_column,
                'parent_supporting_doc_id': str(parent_supporting_doc_id),
                'errormessage': errormessage
            }
        )
        self.write_logfile(
            self.cache_failedrecords,
            self.file_failed
        )

    def success_csvimport_append(self):
        return

    def success_docdownload_append(self):
        return
    
    def write_logfile(self, data, log_file):
        if len(data) == 0:
            return
        with open(log_file, 'w') as f:
            json.dump(data, f, ensure_ascii=True, indent=4)

    def log_write_basicinfo(self):
        self.cache_basicinfo = []
        self.cache_basicinfo.append(
            {
                'sessionid': self.sessionid,
                'sessiontype': self.sessiontype,
                'starttime': self.starttime.strftime('%d-%m-%Y %H:%M:%S'),
                'recordscount': str(self.recordscount),
                'datasource': self.datasource,
                'status': self.status,
                'endtime': self.endtime.strftime('%d-%m-%Y %H:%M:%S')
            }
        )
        self.write_logfile(
            self.cache_basicinfo,
            self.file_basicinfo
        )

    def log_write_successinfo():
        return
    
    def log_write_failedinfo():
        return

    def log_write(self):
        if not os.path.exists(self.root):
            return
        self.log_write_basicinfo
        self.log_write_successinfo
        self.log_write_failedinfo
        