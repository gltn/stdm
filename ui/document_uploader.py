from distutils.log import error
from gettext import gettext
from msilib.schema import File
from posixpath import splitext
import sys
import os
import hashlib
import shutil
from unittest import result
from xml.etree.ElementTree import tostring
import ConfigParser
from datetime import datetime

from collections import OrderedDict

#from qgis.core import *
#from PyQt4.QtCore import *

from PyQt4.QtGui import (
        QApplication,
        QMainWindow,
        QFileDialog,
        QFileSystemModel,
        QMessageBox,
        QColor,
        QFrame,
        QLabel
        )

from PyQt4.QtCore import (
        Qt,
        QObject,
        pyqtSignal,
        QDir,
        SIGNAL,
        QThread
        )

from stdm.settings import (
    get_primary_mapfile,
    current_profile
)

from stdm.settings.registryconfig import (
        RegistryConfig,
        NETWORK_DOC_RESOURCE
)

from stdm.data.pg_utils import (
    pg_parent_supporting_document_exists,
    get_value_by_column,
    pg_create_supporting_document,
    pg_create_parent_supporting_document
)

from stdm.data.importexport import (
    uploadFileDir,
    setUploadFileDir
)

from ui_document_uploader import Ui_DocumentUploader


NETWORK_DOC_RESOURCE = 'NetDocumentResource'

class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

# ------------- DownloadUploader -----------------------#

class DocumentUploader(QMainWindow, Ui_DocumentUploader):

    INFORMATION, WARNING, ERROR = range(0, 3)

    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())

        self.setWindowFlags(
                Qt.Window|
                Qt.WindowTitleHint|
                Qt.WindowMinimizeButtonHint|
                Qt.WindowSystemMenuHint|
                Qt.WindowCloseButtonHint|
                Qt.CustomizeWindowHint
                );

        self.dir_model = None

        self.setupUi(self)

        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        filter = "*.pdf" 
        self.file_model.setNameFilters([filter]) 
        self.file_model.setNameFilterDisables(False)

        self.upload_thread = None

        self.file_model.directoryLoaded.connect(self.directory_loaded)
        self.btnFolder.clicked.connect(self.get_folder)
        self.cbAll.stateChanged.connect(self.toggle_selection)
        self.btnUpload.clicked.connect(self.start_upload_worker)

        self.current_profile = current_profile()
        self.set_default_folder()
        self.create_status_bar()
        
    def create_status_bar(self):
        self.lbl_files_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_files_count)
        self.lbl_selected_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_selected_count)
        self.lbl_uploaded_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_uploaded_count)
        

    def set_status_bar(self, files_count, selected_count, uploaded_count):
        self.lbl_files_count.setText("Files Count: " + files_count)
        self.lbl_selected_count.setText("Selection Count: " + selected_count)
        self.lbl_uploaded_count.setText("Uploaded Count: " + uploaded_count)
        
        #self.statusBar().showMessage("File Count: ")
        #self.statusbar().clearMessage()
        #self.statusBar().addPermanentWidget(VLine())
        #self.statusBar().addPermanentWidget(self.lbl_selected_files)

    def start_upload(self, msg):
        self.btnUpload.setEnabled(False)
        self.edtProgress.append(msg+" Started ...")
        QApplication.prcessEvents()

    def upload_progress(self, info_id, msg):
        if info_id == DocumentUploader.INFORMATION:
            self.edtProgress.setTextColor(QColor('black'))
            self.uploaded_count = str(int(self.uploaded_count) + 1)
            self.set_status_bar(self.files_count, self.selected_count, self.uploaded_count)
        if info_id == DocumentUploader.WARNING:
            self.edtProgress.setTextColor(QColor(225,170,0))
        if info_id == DocumentUploader.ERROR:
            self.edtProgress.setTextColor(QColor('red'))

        self.edtProgress.append(msg)
        QApplication.processEvents()
        
    def upload_completed(self, msg):
        self.btnUpload.setEnabled(True)
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.setFontWeight(75)
        self.edtProgress.append(msg+" completed.")
        self.upload_thread.quit()

    def uploader_thread_started(self):
        self.upload_worker.start_upload()

    def start_upload_worker(self):
        self.upload_worker = UploadWorker(self.edtFolder.text(), self.lvFiles.selectedIndexes(),self.cbDelAfterUpload.checkState(), self.cbAllowDuplicate.checkState())
        self.upload_thread = QThread(self)
        self.upload_worker.moveToThread(self.upload_thread)

        self.upload_worker.upload_started.connect(self.start_upload)
        self.upload_worker.upload_progress.connect(self.upload_progress)
        self.upload_worker.upload_completed.connect(self.upload_completed)

        self.upload_thread.started.connect(self.uploader_thread_started)

        self.upload_thread.start()
        setUploadFileDir(self.edtFolder.text())


    def set_default_folder(self):
        path = uploadFileDir()
        if not os.path.exists(path):
            path = 'D:\Tmp\ScanDocs'
        self.edtFolder.setText(path)
        self.set_file_model_path(path)

    def directory_loaded(self, loaded_path):
        folder_index = self.file_model.index(self.edtFolder.text())
        if self.file_model.canFetchMore(folder_index):
            self.file_model.fetchMore(folder_index)
            return
        self.files_count = str( self.file_model.rowCount(folder_index) )
        self.selected_count = "0"
        self.uploaded_count = "0"
        self.edtProgress.clear()
        self.set_status_bar(self.files_count, self.selected_count, self.uploaded_count)

    def selectedfiles_changed(self):
        self.selected_count = str(len(self.lvFiles.selectionModel().selectedRows()))
        self.set_status_bar(self.files_count, self.selected_count, self.uploaded_count)

    def get_folder(self):
        dialog = QFileDialog()
        doc_folder =  dialog.getExistingDirectory(self, 'Select document directory',self.edtFolder.text())

        if doc_folder != "":
            self.edtFolder.setText(doc_folder)
            self.set_file_model_path(doc_folder)

    def set_file_model_path(self, path):
        self.lvFiles.setModel(self.file_model)
        self.lvFiles.setRootIndex(self.file_model.setRootPath(path))
        self.lvFiles.selectionModel().selectionChanged.connect(self.selectedfiles_changed)

    def toggle_selection(self, state):
        if state == Qt.Checked:
            self.lvFiles.selectAll()
        if state == Qt.Unchecked:
            self.lvFiles.clearSelection()


# --------------- UploadWorker ----------------------- #

class UploadWorker(QObject):
    upload_started = pyqtSignal(unicode)
    upload_progress = pyqtSignal(int, unicode)
    upload_completed = pyqtSignal(unicode)

    INFORMATION, WARNINING, ERROR = range(0, 3)

    def __init__(self, file_path, selected_files, del_after_upload, allow_duplicates, parent=None):
        QObject.__init__(self, parent)
        self.file_path = file_path
        self.selected_files = selected_files
        self.del_after_upload = del_after_upload
        self.allow_duplicates = allow_duplicates
        
        mapfile_path = os.path.dirname(get_primary_mapfile())
        self.support_doc_map = self.mapfile_section( os.path.join( mapfile_path,'property_mapfile.ini'), 'support_doc-map')
        self.curr_profile = current_profile()

    def start_upload(self):
        scanned_certs = self.fetch_scanned_certs()
        self.upload_scanned_certs(scanned_certs)

    def upload_scanned_certs(self, scanned_certs):
        if len(scanned_certs) == 0:
            return

        parent_table = self.support_doc_map['parent_table']
        support_doc_table = self.support_doc_map['parent_support_table']
        ref_column = self.support_doc_map['scanned_cert_ref_column']
        #parent_column=self.support_doc_map['parent_column']
        parent_column=parent_table[3:] + '_id'

        doc_type_cache={}

        for key, value in scanned_certs.iteritems():
            ref_code = value[0]['key_field_value'].split('.')[0]
            try:
                parent_id = self.get_parent_id(parent_table, ref_code, ref_column)
            except:
                parent_id = -1
            
            if parent_id == -1:
                msg = 'No parent found for this docoment: `'+ref_code+'`' 
                self.upload_progress.emit(UploadWorker.ERROR, msg)
                continue

            for scanned_cert in scanned_certs[key]:
                src_doc_type_id = scanned_cert['doc_type_id']
                short_filename = scanned_cert['key_field_value']
                full_filename = scanned_cert['full_filename']

                if not os.path.exists(full_filename):
                    msg = 'File not found: `'+full_filename+'`'
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue
                
                support_doc = self.make_supporting_doc(full_filename)
                support_doc_duplicated = False
                if not self.allow_duplicates:
                    try:
                        support_doc_id = self.get_value_by_column(support_doc['support_doc_table'], 'id', 'document_identifier', "'" + support_doc['hashed_filename'] + "'")
                        support_doc_duplicated = self.supporting_document_isduplicated(support_doc_table, parent_column, support_doc_id, parent_id, int(src_doc_type_id))
                    except:
                        pass

                if support_doc_duplicated:
                    msg = 'Canceled uploading document due to duplication: `'+support_doc['doc_filename']+'`' 
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                found_error = False
                try:
                    result = self.pg_create_supporting_document(support_doc)
                    #next_support_doc_id = 1 # result.fetchone()[0]
                    next_support_doc_id = result.fetchone()[0]
                except:
                    msg = "Error creating supporting document record: `"+support_doc['support_doc_table']+"`"
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    found_error = True

                if found_error:
                    continue

                # Create a record in the parent table supporting document table
                try:
                    #pass
                    self.create_supporting_doc(support_doc_table, next_support_doc_id, parent_id, int(src_doc_type_id),parent_column)
                except:
                    # Error creating supporting doc
                    found_error = True
        
                if found_error:
                    continue

                # copy file to STDM supporting document folder
                try:
                    if src_doc_type_id in doc_type_cache:
                        doc_type = doc_type_cache[src_doc_type_id]
                    else:
                        doc_type = self.get_value_by_column(self.support_doc_map['doc_type_lookup_table'], 'value', 'id', src_doc_type_id)
                        doc_type_cache[src_doc_type_id] = doc_type

                    new_filename = support_doc['hashed_filename']
                    self.create_new_support_doc_file(scanned_cert, new_filename, doc_type)

                except:
                    msg = "Error creating file: `"+new_filename+"`"
                    self.upload_progress.emit(UploadWorker.ERROR, msg)

                msg = "Finished creating file: `"+new_filename+"`"
                self.upload_progress.emit(UploadWorker.INFORMATION, msg)
                #Delete After Upload
                if self.del_after_upload:
                    try:
                        old_filename=scanned_cert['full_filename']
                        os.remove(old_filename)
                        msg = "Removed file: `"+old_filename+"`"
                        self.upload_progress.emit(UploadWorker.INFORMATION, msg)
                    except:
                        msg = "Failed to Removed file: `"+old_filename+"`"
                        self.upload_progress.emit(UploadWorker.ERRORINFORMATION, msg)


    def create_supporting_doc(self, table_name, next_doc_id, property_id, doc_type_id,parent_column):
        self.pg_create_parent_supporting_document(table_name,  next_doc_id, property_id, doc_type_id,parent_column)


    def pg_create_parent_supporting_document(self, table_name, doc_id, property_id, doc_type_id, parent_column):
        return pg_create_parent_supporting_document(table_name, doc_id, property_id, doc_type_id, parent_column)

    def create_new_support_doc_file(self, old_file, new_filename, doc_type):
        reg_config = RegistryConfig()
        support_doc_path = reg_config.read([NETWORK_DOC_RESOURCE])
        
        old_file_type = old_file['doc_type_id']
        old_filename = old_file['full_filename']

        name, file_ext = os.path.splitext(old_file['key_field_value'])

        doc_path = support_doc_path.values()[0]

        profile_name = self.curr_profile.name

        entity_name = self.support_doc_map['parent_table']
        doc_type = doc_type.replace(' ','_').lower()

        dest_path = doc_path+'/'+profile_name.lower()+'/'+entity_name+'/'+doc_type+'/'
        dest_filename = dest_path+new_filename+file_ext
        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        shutil.copy(old_filename, dest_filename)


    def make_supporting_doc(self, doc_name):
        doc_size = os.path.getsize(doc_name)
        path, filename = os.path.split(str(doc_name))
        ht = hashlib.sha1(filename.encode('utf-8'))
        document = {}

        document['support_doc_table'] = self.support_doc_map['main_table']
        document['creation_date']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        document['hashed_filename'] = ht.hexdigest()
        document['source_entity'] = self.support_doc_map['parent_table']
        document['doc_filename'] = filename
        document['document_size'] = doc_size

        return document
    

    def get_parent_id(self, parent_table, value, parent_ref_column):
        target_col = 'id'
        where_col = parent_ref_column
        value = "'"+value+"'"
        
        id = self.get_value_by_column(parent_table, target_col, where_col, value)
        return id


    def get_value_by_column(self, parent_table, target_column, where_column, value):
        id = get_value_by_column(parent_table, target_column, where_column, value)
        if id == None:
            return -1
        return id         
        #return "scanned certificate"
        
    def fetch_scanned_certs(self):
        doc_type = "'" + 'Scanned certificate' + "'"
        doc_files = {}
        #doc_type_id = 2  # get from mapfile

        doc_type_id = self.get_value_by_column(self.support_doc_map['doc_type_lookup_table'],'id', 'value',doc_type)
        if doc_type_id == None:
            ErrMessage("To Add Filetype")
            return

        for index in self.selected_files:
            if index.column() == 0:
                doc_src = []
                #filename = index.data().toString()
                filename = index.data()
                full_filename = self.file_path+'\\'+filename
                doc_src.append({'doc_type_id': doc_type_id,
                                'key_field_value':unicode(filename),
                                'full_filename':full_filename})
                doc_files[unicode(filename)]=doc_src
        return doc_files

    def pg_create_supporting_document(self, document):
        return pg_create_supporting_document(document)

    def supporting_document_isduplicated(self, table_name, parent_col, doc_id, parent_id, doctype_id):
        return pg_parent_supporting_document_exists(table_name, parent_col, doc_id, parent_id, doctype_id) != None 

    def mapfile_section(self, mapfile, section):
        map_section = OrderedDict()
        config_parser = ConfigParser.ConfigParser()
        config_parser.readfp(open(mapfile))
        if section in config_parser.sections():
            map_section = OrderedDict(config_parser.items(unicode(section)))
        return map_section

def ErrMessage(message):
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    du = DocumentUploader();
    du.showNormal()
    sys.exit(app.exec_())

