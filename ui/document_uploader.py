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

from PyQt4 import QtGui
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
    pg_table_exists,
    pg_table_column_exists,
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

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(
            context,
            text,
            disambig,
            _encoding
        )
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(
            context,
            text,
            disambig
        )


class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)

# ------------- DownloadUploader -----------------------#

class DocumentUploader(QMainWindow, Ui_DocumentUploader):

    INFORMATION, WARNING, ERROR = range(0, 3)

    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowCloseButtonHint |
            Qt.CustomizeWindowHint
        )
        self.dir_model = None
        self.setupUi(self)

        # Create file_model/Filter=pdf documents
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        filter = '*.pdf'
        self.file_model.setNameFilters([filter])
        self.file_model.setNameFilterDisables(False)

        self.upload_thread = None

        # Set Controls' Evenets
        self.file_model.directoryLoaded.connect(self.directory_loaded)
        self.btnFolder.clicked.connect(self.get_folder)
        self.cbAll.stateChanged.connect(self.toggle_selection)
        self.btnUpload.clicked.connect(self.start_upload_worker)

        # Init Variables & Conrtols' Initial Attributes
        self.current_profile = current_profile()
        self.set_default_folder()
        self.create_status_bar()

    def create_status_bar(self):
        self.lbl_crtfiles_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_crtfiles_count)
        self.lbl_selected_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_selected_count)
        self.lbl_uploaded_count = QLabel()
        self.statusBar().addWidget(VLine())
        self.statusBar().addWidget(self.lbl_uploaded_count)

    def set_status_bar(self, files_count, selected_count, uploaded_count):
        if files_count is None:
            local_files_count = 0
        else: 
            local_files_count = files_count
        if selected_count is None:
            local_selected_count = 0
        else: 
            local_selected_count = selected_count
        if uploaded_count is None:
            local_uploaded_count = 0
        else: 
            local_uploaded_count = uploaded_count    
        
        self.lbl_crtfiles_count.setText(
            _translate(
                'DocumentUploader',
                u'Files Count: {0}',
                None
            ).format(local_files_count)
        )
        self.lbl_selected_count.setText(
            _translate(
                'DocumentUploader',
                u'Selection Count: {0}',
                None
            ).format(local_selected_count)
        )
        self.lbl_uploaded_count.setText(
            _translate(
                'DocumentUploader',
                u'Uploaded Count: {0}',
                None
            ).format(local_uploaded_count)
        )

    def start_upload(self, msg):
        self.btnUpload.setEnabled(False)
        self.edtProgress.append(msg + ' Started ...')
        QApplication.prcessEvents()

    def upload_progress(self, info_id, msg):
        if info_id == DocumentUploader.INFORMATION:
            self.edtProgress.setTextColor(QColor('black'))
            self.uploaded_count = self.uploaded_count + 1
            self.set_status_bar(
                self.files_count,
                self.selected_count,
                self.uploaded_count
            )

        if info_id == DocumentUploader.WARNING:
            self.edtProgress.setTextColor(QColor(225, 170, 0))

        if info_id == DocumentUploader.ERROR:
            self.edtProgress.setTextColor(QColor('red'))

        self.edtProgress.append(msg)
        QApplication.processEvents()

    def upload_completed(self, msg):
        self.btnUpload.setEnabled(True)
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.setFontWeight(75)
        self.edtProgress.append(msg + ' completed.')
        self.upload_thread.quit()

    def uploader_thread_started(self):
        self.upload_worker.start_upload()

    def start_upload_worker(self):
        self.upload_worker = UploadWorker(
            self.edtFolder.text(),
            self.lvFiles.selectedIndexes(),
            self.cbDelAfterUpload.checkState(),
            self.cbAllowDuplicate.checkState()
        )
        self.upload_thread = QThread(self)
        self.upload_worker.moveToThread(self.upload_thread)

        self.upload_worker.upload_started.connect(self.start_upload)
        self.upload_worker.upload_progress.connect(self.upload_progress)
        self.upload_worker.upload_completed.connect(self.upload_completed)

        self.upload_thread.started.connect(self.uploader_thread_started)

        self.upload_thread.start()
        setUploadFileDir(self.edtFolder.text())

    def set_default_folder(self):
        self.files_count = 0
        path = uploadFileDir()
        if not os.path.exists(path):
            path = os.getcwd()
        self.edtFolder.setText(path)
        self.set_file_model_path(path)

    def directory_loaded(self, loaded_path):
        self.files_count = 0
        self.selected_count = 0
        self.uploaded_count = 0
        if self.edtFolder is None:
            return
        if not os.path.exists(self.edtFolder.text()):
            return
        if not self.file_model is None:
            return
        folder_index = self.file_model.index(self.edtFolder.text())
        if self.file_model.canFetchMore(folder_index):
            self.file_model.fetchMore(folder_index)
            return
        self.files_count = self.file_model.rowCount(folder_index)
        self.set_status_bar(
            self.files_count,
            self.selected_count,
            self.uploaded_count
        )

    def selectedfiles_changed(self):
        self.selected_count = len(
            self.lvFiles.selectionModel().selectedRows()
        )
        self.set_status_bar(
            self.files_count,
            self.selected_count,
            self.uploaded_count
        )

    def get_folder(self):
        dialog = QFileDialog()
        doc_folder = dialog.getExistingDirectory(
            self,
            _translate(
                'DocumentUploader',
                'Select document directory',
                None
            ),
            self.edtFolder.text()
        )
        if doc_folder != '':
            self.edtFolder.setText(doc_folder)
            self.set_file_model_path(doc_folder)
            self.edtProgress.clear()

    def set_file_model_path(self, path):
        self.lvFiles.setModel(self.file_model)
        self.lvFiles.setRootIndex(self.file_model.setRootPath(path))
        self.lvFiles.selectionModel().selectionChanged.connect(
            self.selectedfiles_changed
        )

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

    def __init__(self, file_path, selected_files, del_after_upload,
            allow_duplicates, parent=None):
        QObject.__init__(self, parent)

        self.curr_profile = current_profile()

        self.file_path = file_path
        self.selected_files = selected_files
        self.del_after_upload = del_after_upload
        self.allow_duplicates = allow_duplicates

        self.support_doc_map = None
        if not os.path.exists(get_primary_mapfile()):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'Primary mapfile not exists',
                    None
                )
            )
            return

        mapfile_path = os.path.dirname(get_primary_mapfile())
        if not os.path.exists(mapfile_path):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'Mapfile Path does not exist',
                    None
                )
            )
            return

        self.support_doc_map_filename = os.path.normpath(
            os.path.join(mapfile_path, 'property_mapfile.ini')
        )
        if not os.path.exists(self.support_doc_map_filename):
            _translate(
                'DocumentUploader',
                'Mapfile does not exist',
                None
            )
            return

        self.support_doc_map = self.mapfile_section(
            self.support_doc_map_filename,
            'support_doc-map'
        )

    def start_upload(self):
        scanned_certs = self.fetch_scanned_certs()
        self.upload_scanned_certs(scanned_certs)

    def upload_scanned_certs(self, scanned_certs):
        if len(scanned_certs) == 0:
            return

        parent_table = self.support_doc_map_getvalue(
            'parent_table',
            '',
            _translate(
                'DocumentUploader',
                'Check mapfile Param parent_table',
                None
            )
        )
        if not pg_table_exists(parent_table):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'DB: parent_table does not exists',
                    None
                )
            )
            return

        support_doc_table = self.support_doc_map_getvalue(
            'parent_support_table',
            '',
            _translate(
                'DocumentUploader',
                'Check mapfile Param parent_support_table',
                None
            )
        )
        if not pg_table_exists(support_doc_table):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'DB: parent_support_table does not exists',
                    None
                )
            )
            return

        ref_column = self.support_doc_map_getvalue(
            'scanned_cert_ref_column',
            '',
            _translate(
                'DocumentUploader',
                'Check mapfile Param scanned_cert_ref_column',
                None
            )
        )
        if not pg_table_column_exists(parent_table, ref_column):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'DB: scanned_cert_ref_column does not exists',
                    None
                )
            )
            return

        if len(parent_table) <= 3:
            ErrMessage(
                _translate('DocumentUploader',
                           'Invalid parent_table name',
                           None)
            )
            return
        parent_column = parent_table[3:] + '_id'
        if not pg_table_column_exists(support_doc_table, parent_column):
            ErrMessage(
                _translate(
                    'DocumentUploader',
                    'DB: parent_column does not exist',
                    None
                )
            )
            return

        doc_type_cache = {}

        for key, value in scanned_certs.iteritems():
            ref_code, value_file_ext = value[0]['key_field_value'].split('.')
            parent_id = self.get_parent_id(
                parent_table,
                ref_code,
                ref_column
            )
            if parent_id == -1:
                msg = _translate(
                    'DocumentUploader',
                    u'No parent found for this docoment: {0}',
                    None
                    ).format('`' + ref_code + '`')
                self.upload_progress.emit(UploadWorker.ERROR, msg)
                continue

            for scanned_cert in scanned_certs[key]:
                src_doc_type_id = scanned_cert['doc_type_id']
                short_filename = scanned_cert['key_field_value']
                full_filename = scanned_cert['full_filename']

                if not os.path.exists(full_filename):
                    msg = _translate(
                        'DocumentUploader',
                        u'File not found: {0}',
                        None
                        ).format('`' + full_filename + '`')
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                support_doc = self.make_supporting_doc(full_filename)
                support_doc_duplicated = False
                if not self.allow_duplicates:
                    support_doc_id = self.get_value_by_column(
                        support_doc['support_doc_table'],
                        'id',
                        'document_identifier',
                        "'" + support_doc['hashed_filename'] + "'"
                    )
                    support_doc_duplicated = self.supporting_document_exists(
                        support_doc_table,
                        parent_column,
                        support_doc_id,
                        parent_id,
                        int(src_doc_type_id)
                    )

                if support_doc_duplicated:
                    msg = _translate(
                        'DocumentUploader',
                        u'Canceled uploading document due to duplication: {0}',
                        None
                        ).format( '`' + support_doc['doc_filename'] + '`')
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                found_error = True
                result = self.pg_create_supporting_document(support_doc)
                if result != None:
                    next_support_doc_id = result.fetchone()[0]
                    if next_support_doc_id != None:
                        found_error = False

                if found_error:
                    msg = _translate(
                        'DocumentUploader',
                        u'Error creating supporting document record: {0}',
                        None
                        ).format( '`' + support_doc['support_doc_table'] + '`')
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                # Create a record in the parent supporting document table
                parent_supporting_doc_id = self.create_parent_supporting_doc(
                    support_doc_table,
                    next_support_doc_id,
                    parent_id,
                    int(src_doc_type_id), parent_column
                )
                if parent_supporting_doc_id is None:
                    msg = _translate(
                        'DocumentUploader',
                        u'Error creating parent supporting document '\
                            'record: {0}',
                        None
                        ).format( '`' + support_doc['support_doc_table'] + '`')
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                # copy file to STDM supporting document folder
                doc_copy_error = ''
                if src_doc_type_id in doc_type_cache:
                    doc_type = doc_type_cache[src_doc_type_id]
                else:
                    doc_type_lookup_table = self.support_doc_map_getvalue(
                        'doc_type_lookup_table',
                        '',
                        ''
                    )
                    if doc_type_lookup_table == '':
                        doc_copy_error = 'doctype: Mapfile Param Missed'
                    else:
                        doc_type = self.get_value_by_column(
                            self.support_doc_map['doc_type_lookup_table'],
                            'value',
                            'id',
                            src_doc_type_id
                        )
                        doc_type_cache[src_doc_type_id] = doc_type

                new_filename = ''
                if not 'hashed_filename' in support_doc:
                    doc_copy_error = doc_copy_error + ' Key hashed_filename'
                else:
                    new_filename = support_doc['hashed_filename']

                doc_copy_result = False
                if doc_copy_error == '':
                    doc_type_cache[src_doc_type_id] = doc_type
                    doc_copy_result = self.create_new_support_doc_file(
                        scanned_cert,
                        new_filename,
                        doc_type
                    )

                if not doc_copy_result:
                    msg = _translate(
                        'DocumentUploader',
                        u'Error creating file: {0}',
                        None
                        ).format( '`' + new_filename + '`')
                    self.upload_progress.emit(UploadWorker.ERROR, msg)
                    continue

                msg = _translate(
                    'DocumentUploader',
                    u'Finished creating file: {0}',
                    None
                    ).format( '`' + new_filename + '`')
                self.upload_progress.emit(UploadWorker.INFORMATION, msg)

                # Delete After Upload
                if self.del_after_upload:
                    old_filename = scanned_cert['full_filename']
                    os.remove(old_filename)
                    msg =  _translate(
                        'DocumentUploader',
                        u'Removed file: {0}',
                        None
                        ).format('`' + old_filename + '`')
                    self.upload_progress.emit(
                        UploadWorker.INFORMATION,
                        msg
                    )
                    if os.path.exists(old_filename):
                        msg = _translate('DocumentUploader',
                            'Failed to Removed file: {0}',
                            None).format( '`' + old_filename + '`')
                        self.upload_progress.emit(
                            UploadWorker.ERRORINFORMATION,
                            msg
                        )

    def support_doc_map_getvalue(self, key, notexists_value, notexists_msg):
        result = notexists_value
        if self.support_doc_map is None:
            return result
        if not key in self.support_doc_map:
            if notexists_msg != '':
                ErrMessage(notexists_msg)
            return result
        result = self.support_doc_map[key]
        return result

    def create_parent_supporting_doc(self, table_name, next_doc_id,
            property_id, doc_type_id, parent_column):
        return pg_create_parent_supporting_document(
            table_name,
            next_doc_id,
            property_id,
            doc_type_id,
            parent_column
        )

    def create_new_support_doc_file(self, old_file, new_filename, doc_type):
        reg_config = RegistryConfig()
        support_doc_path = reg_config.read([NETWORK_DOC_RESOURCE])

        old_file_type = old_file['doc_type_id']
        old_filename = old_file['full_filename']

        name, file_ext = os.path.splitext(old_file['key_field_value'])

        doc_path = support_doc_path.values()[0]

        profile_name = self.curr_profile.name

        entity_name = self.support_doc_map_getvalue(
            'parent_table',
            '',
            ''
        )

        if entity_name == '':
            return False
        doc_type = doc_type.replace(' ', '_').lower()

        dest_path = (doc_path
                     + '/' + profile_name.lower()
                     + '/' + entity_name
                     + '/' + doc_type
                     + '/'
                     )
        dest_filename = dest_path + new_filename + file_ext

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        shutil.copy(old_filename, dest_filename)
        return True

    def make_supporting_doc(self, doc_name):
        doc_size = os.path.getsize(doc_name)
        path, filename = os.path.split(str(doc_name))
        ht = hashlib.sha1(filename.encode('utf-8'))
        document = {}

        document['support_doc_table'] = self.support_doc_map['main_table']
        document['creation_date'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        document['hashed_filename'] = ht.hexdigest()
        document['source_entity'] = self.support_doc_map['parent_table']
        document['doc_filename'] = filename
        document['document_size'] = doc_size

        return document

    def get_parent_id(self, parent_table, value, parent_ref_column):
        target_col = 'id'
        where_col = parent_ref_column
        value = "'" + value + "'"

        id = self.get_value_by_column(
            parent_table,
            target_col,
            where_col,
            value
        )
        return id

    def get_value_by_column(self, parent_table, target_column,
            where_column, value):
        id = get_value_by_column(
            parent_table,
            target_column,
            where_column,
            value
        )
        if id is None:
            return -1
        return id

    def fetch_scanned_certs(self):
        doc_type = "'" + 'Scanned certificate' + "'"
        doc_files = {}

        if self.support_doc_map is None:
            return doc_files

        doc_type_id = self.get_value_by_column(
            self.support_doc_map['doc_type_lookup_table'],
            'id',
            'value',
            doc_type
        )

        if doc_type_id is None:
            ErrMessage('To Add Filetype')
            return

        for index in self.selected_files:
            if index.column() == 0:
                doc_src = []
                filename = index.data()
                full_filename = self.file_path+'\\'+filename
                doc_src.append(
                    {'doc_type_id': doc_type_id,
                     'key_field_value': unicode(filename),
                     'full_filename': full_filename}
                )
                doc_files[unicode(filename)] = doc_src
        return doc_files

    def pg_create_supporting_document(self, document):
        return pg_create_supporting_document(document)

    def supporting_document_exists(self, table_name, parent_col,
            doc_id, parent_id, doctype_id):
        result = pg_parent_supporting_document_exists(
            table_name,
            parent_col,
            doc_id,
            parent_id,
            doctype_id
        )
        return result

    def mapfile_section(self, mapfile, section):
        map_section = OrderedDict()
        config_parser = ConfigParser.ConfigParser()
        config_parser.readfp(open(mapfile))
        if section in config_parser.sections():
            map_section = OrderedDict(config_parser.items(unicode(section)))
        return map_section


def ErrMessage(message):
    # Error Message Box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    du = DocumentUploader()
    du.showNormal()
    sys.exit(app.exec_())
