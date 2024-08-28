import os
from os.path import isfile, join
import fnmatch
import shutil
import sys
import copy
from collections import OrderedDict
from datetime import datetime
import hashlib
import requests

import time

from PyQt4.QtGui import (
        QApplication,
        QDialog,
        QMainWindow,
        QFileDialog,
        QMessageBox,
        QLineEdit,
        QColor
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

from stdm.data.importexport import (
    vectorFileDir,
    setVectorFileDir
)

from stdm.settings import (
        current_profile,
        get_media_url,
        get_kobo_user,
        get_kobo_pass,
        get_family_photo,
        get_sign_photo,
        get_house_photo,
        get_house_pic,
        get_id_pic,
        get_scanned_doc,
        get_scanned_hse_map,
        get_scanned_hse_pic,
        get_scanned_id_doc,
        save_media_url,
        save_kobo_user,
        save_kobo_pass,
        save_family_photo,
        save_sign_photo,
        save_house_photo,
        save_house_pic,
        save_id_pic,
        save_scanned_doc,
        save_scanned_hse_map,
        save_scanned_hse_pic,
        save_scanned_id_doc
        )

from stdm.settings.registryconfig import (
        RegistryConfig,
        NETWORK_DOC_RESOURCE
)

from stdm.utils.util import mapfile_section

from stdm.data.pg_utils import (
    get_last_id,
    get_value_by_column,
    pg_create_supporting_document,
    pg_create_parent_supporting_document,
    pg_fix_auto_sequence
)

from stdm.data.importexport.reader import OGRReader

from ui_document_downloader_win import Ui_DocumentDownloader

DOWNLOAD_DOCS = 0
UPLOAD_DOCS = 1

class DocumentDownloader(QMainWindow, Ui_DocumentDownloader):
    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())

        self.setWindowFlags( 
                Qt.Window|
                Qt.WindowTitleHint|
                Qt.WindowMinimizeButtonHint|
                Qt.WindowSystemMenuHint|
                Qt.WindowCloseButtonHint|
                Qt.CustomizeWindowHint);

        self.setupUi(self)

        self.btnBrowseSource.clicked.connect(self.set_source_file)

        self.rbKoboMedia.clicked.connect(self.kobo_media_clicked)
        self.rbSupportDoc.clicked.connect(self.support_doc_clicked)
        self.rbScannedDoc.clicked.connect(self.scanned_doc_clicked)

        self.tbFamilyFolder.clicked.connect(self.family_folder)
        self.tbSignFolder.clicked.connect(self.sign_folder)
        self.tbHouseFolder.clicked.connect(self.house_folder)
        self.tbHousePic.clicked.connect(self.house_pic_folder)
        self.tbIdPic.clicked.connect(self.id_pic_folder)
        self.tbScannedDoc.clicked.connect(self.scanned_doc_folder)
        self.tbScannedHseMap.clicked.connect(self.scanned_hse_map_folder)
        self.tbScannedHsePic.clicked.connect(self.scanned_hse_pic_folder)
        self.tbScannedIdDoc.clicked.connect(self.scanned_id_doc_folder)

        self.btnDownload.clicked.connect(self.download_media)
        self.btnDownload.setStyleSheet("QPushButton{ background-color: rgb(85,255,127) }")

        self.btnFamilyBrowse.clicked.connect(self.show_family_folder)
        self.btnSignFolder.clicked.connect(self.show_sign_folder)
        self.btnHouseFolder.clicked.connect(self.show_house_folder)
        self.btnHousePic.clicked.connect(self.show_house_pic_folder)
        self.btnIdPic.clicked.connect(self.show_id_pic_folder)
        self.btnScannedDoc.clicked.connect(self.show_scanned_doc_folder)
        self.btnScannedHseMap.clicked.connect(self.show_scanned_hse_map_folder)
        self.btnScannedHsePic.clicked.connect(self.show_scanned_hse_pic_folder)
        self.btnScannedIdDoc.clicked.connect(self.show_scanned_id_doc_folder)

        self.cbFamilyPhoto.toggled.connect(self.enable_family_photo)
        self.cbSign.toggled.connect(self.enable_signature)
        self.cbHousePhoto.toggled.connect(self.enable_house_photo)
        self.cbHousePic.toggled.connect(self.enable_house_pic)
        self.cbIdPic.toggled.connect(self.enable_id_pic)
        self.cbScannedDoc.toggled.connect(self.enable_scanned_doc)
        self.cbScannedHseMap.toggled.connect(self.enable_scanned_hse_map)
        self.cbScannedHsePic.toggled.connect(self.enable_scanned_hse_pic)
        self.cbScannedIdDoc.toggled.connect(self.enable_scanned_id_doc)

        self.btnClose.clicked.connect(self.close_window)

        #Data Reader
        self.dataReader = None
        self.curr_profile = current_profile()

        self.twDocument.setCurrentIndex(0)
        self.twDocument.currentChanged.connect(self.page_changed)

        self.read_kobo_defaults()
        self.check_download_all()

        self.rbKoboMedia.setChecked(True)
        self.toggleSupportDoc(False)
        self.toggleScannedDoc(False)

        self.downloader_mode = DOWNLOAD_DOCS

    def hideWindow(self):
        self.hide()

    def kobo_media_clicked(self):
        if self.rbKoboMedia.isChecked():
            self.rbScannedDoc.setChecked(False)
            self.rbSupportDoc.setChecked(False)
            self.toggleKoboOptions(True)
            self.toggleSupportDoc(False)
            self.toggleScannedDoc(False)
            self.btnDownload.setEnabled(True)
            self.btnDownload.setStyleSheet("QPushButton{ background-color: rgb(85,255,127) }")
        else:
            self.toggleKoboOptions(False)
            self.disable_download_button()

    def support_doc_clicked(self):
        lelf.btnDownload.setText('Download')
        if self.rbSupportDoc.isChecked():
            self.rbScannedDoc.setChecked(False)
            self.rbKoboMedia.setChecked(False)
            self.toggleSupportDoc(True)
            self.toggleKoboSettings(True)
            self.toggleMediaFolders(False)
            self.toggleScannedDoc(False)
            self.btnDownload.setEnabled(True)
            self.btnDownload.setStyleSheet("QPushButton{ background-color: rgb(85,255,127) }")
        else:
            self.toggleSupportDoc(False)
            self.toggleKoboSettings(False)
            self.disable_download_button()

    def scanned_doc_clicked(self):
        if self.rbScannedDoc.isChecked():
            self.rbKoboMedia.setChecked(False)
            self.rbSupportDoc.setChecked(False)
            self.toggleSupportDoc(False)
            self.toggleKoboSettings(False)
            self.toggleMediaFolders(False)
            self.toggleScannedDoc(True)
            self.btnDownload.setEnabled(True)
            self.btnDownload.setStyleSheet("QPushButton{ background-color: rgb(255,85,0) }")
        else:
            self.disable_download_button()
            self.toggleScannedDoc(False)

    def toggleScannedDoc(self, mode):
        self._toggleScannedDoc(mode)
        self._toggleScannedHseMap(mode)
        self._toggleScannedHsePic(mode)
        self._toggleScannedIdDoc(mode)

    def _toggleScannedDoc(self, mode):
        self.edtScannedDoc.setEnabled(mode)
        self.cbScannedDoc.setEnabled(mode)
        self.tbScannedDoc.setEnabled(mode)
        self.btnScannedDoc.setEnabled(mode)

    def _toggleScannedHseMap(self, mode):
        self.edtScannedHseMap.setEnabled(mode)
        self.cbScannedHseMap.setEnabled(mode)
        self.tbScannedHseMap.setEnabled(mode)
        self.btnScannedHseMap.setEnabled(mode)

    def _toggleScannedHsePic(self, mode):
        self.edtScannedHsePic.setEnabled(mode)
        self.cbScannedHsePic.setEnabled(mode)
        self.tbScannedHsePic.setEnabled(mode)
        self.btnScannedHsePic.setEnabled(mode)
    
    def _toggleScannedIdDoc(self, mode):
        self.edtScannedIdDoc.setEnabled(mode)
        self.cbScannedIdDoc.setEnabled(mode)
        self.tbScannedIdDoc.setEnabled(mode)
        self.btnScannedIdDoc.setEnabled(mode)

    def toggleKoboOptions(self, mode):
        self.toggleKoboSettings(mode)
        self.toggleMediaFolders(mode)

    def toggleSupportDoc(self, mode):
        self.edtHousePic.setEnabled(mode);
        self.cbHousePic.setEnabled(mode);
        self.tbHousePic.setEnabled(mode);
        self.btnHousePic.setEnabled(mode);

        self.edtIdPic.setEnabled(mode);
        self.cbIdPic.setEnabled(mode);
        self.tbIdPic.setEnabled(mode);
        self.btnIdPic.setEnabled(mode);

    def toggleMediaFolders(self, mode):
        self.edtFamilyFolder.setEnabled(mode)
        self.edtSignFolder.setEnabled(mode)
        self.edtHouseFolder.setEnabled(mode)
        self.tbFamilyFolder.setEnabled(mode)
        self.tbSignFolder.setEnabled(mode)
        self.tbHouseFolder.setEnabled(mode)
        self.btnFamilyBrowse.setEnabled(mode)
        self.btnSignFolder.setEnabled(mode)
        self.btnHouseFolder.setEnabled(mode)

        self.cbFamilyPhoto.setEnabled(mode)
        self.cbSign.setEnabled(mode)
        self.cbHousePhoto.setEnabled(mode)

    def toggleKoboSettings(self, mode):
        self.edtMediaUrl.setEnabled(mode)
        self.edtKoboUsername.setEnabled(mode)
        self.edtKoboPassword.setEnabled(mode)

    def read_kobo_defaults(self):
        self.edtMediaUrl.setText(get_media_url())
        self.edtKoboUsername.setText(get_kobo_user())
        self.edtFamilyFolder.setText(get_family_photo())
        self.edtSignFolder.setText(get_sign_photo())
        self.edtHouseFolder.setText(get_house_photo())
        self.edtHousePic.setText(get_house_pic())
        self.edtIdPic.setText(get_id_pic())
        self.edtScannedDoc.setText(get_scanned_doc())
        self.edtScannedHseMap.setText(get_scanned_hse_map())
        self.edtScannedHsePic.setText(get_scanned_hse_pic())
        self.edtScannedIdDoc.setText(get_scanned_id_doc())

    def check_download_all(self):
        self.cbFamilyPhoto.setCheckState(Qt.Checked)
        self.cbSign.setCheckState(Qt.Checked)
        self.cbHousePhoto.setCheckState(Qt.Checked)
        self.cbHousePic.setCheckState(Qt.Checked)
        self.cbIdPic.setCheckState(Qt.Checked)
        self.cbScannedDoc.setCheckState(Qt.Checked)
        self.cbScannedHseMap.setCheckState(Qt.Checked)
        self.cbScannedHsePic.setCheckState(Qt.Checked)
        self.cbScannedIdDoc.setCheckState(Qt.Checked)

    def set_source_file(self):
        #Set the file path to the source file
        image_filters = "Comma Separated Value (*.csv);;ESRI Shapefile (*.shp);;AutoCAD DXF (*.dxf)" 
        source_file = QFileDialog.getOpenFileName(self,"Select Source File",vectorFileDir(),image_filters)
        if source_file != "":
            self.txtDataSource.setText(source_file) 
        
    def family_folder(self):
        dflt_folder = self.edtFamilyFolder.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtFamilyFolder.setText(folder)
            save_family_photo(folder)

    def sign_folder(self):
        dflt_folder = self.edtSignFolder.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtSignFolder.setText(folder)
            save_sign_photo(folder)

    def house_folder(self):
        dflt_folder = self.edtHouseFolder.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtHouseFolder.setText(folder)
            save_house_photo(folder)

    def house_pic_folder(self):
        dflt_folder = self.edtHousePic.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtHousePic.setText(folder)
            save_house_pic(folder)

    def id_pic_folder(self):
        dflt_folder = self.edtIdPic.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtIdPic.setText(folder)
            save_id_pic(folder)

    def scanned_doc_folder(self):
        dflt_folder = self.edtScannedDoc.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtScannedDoc.setText(folder)
            save_scanned_doc(folder)

    def scanned_hse_map_folder(self):
        dflt_folder = self.edtScannedHseMap.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtScannedHseMap.setText(folder)
            save_scanned_hse_map(folder)

    def scanned_hse_pic_folder(self):
        dflt_folder = self.edtScannedHsePic.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtScannedHsePic.setText(folder)
            save_scanned_hse_pic(folder)

    def scanned_id_doc_folder(self):
        dflt_folder = self.edtScannedIdDoc.text()
        folder = self.select_media_folder(dflt_folder)
        if folder <> '':
            self.edtScannedIdDoc.setText(folder)
            save_scanned_id_doc(folder)

    def select_media_folder(self, dflt_folder):
        title = self.tr("Folder to store media files")
        trans_path = QFileDialog.getExistingDirectory(self, title, dflt_folder)
        return trans_path

    def valid_credentials(self):
        if self.edtMediaUrl.text() == '':
            self.ErrorInfoMessage("Source of media files")
            return False

        if self.edtKoboUsername.text() == '':
            self.ErrorInfoMessage("Please enter username")
            return False

        if self.edtKoboPassword.text() == '':
            self.ErrorInfoMessage("Please enter password")
            return False

        return True

    def show_family_folder(self):
        self.browse_folder(self.edtFamilyFolder.text())

    def show_sign_folder(self):
        self.browse_folder(self.edtSignFolder.text()) 

    def show_house_folder(self):
        self.browse_folder(self.edtHouseFolder.text())

    def show_house_pic_folder(self):
        self.browse_folder(self.edtHousePic.text()) 

    def show_id_pic_folder(self):
        self.browse_folder(self.edtIdPic.text()) 

    def show_scanned_doc_folder(self):
        self.browse_folder(self.edtScannedDoc.text()) 

    def show_scanned_hse_map_folder(self):
        self.browse_folder(self.edtScannedHseMap.text()) 

    def show_scanned_hse_pic_folder(self):
        self.browse_folder(self.edtScannedHsePic.text()) 

    def show_scanned_id_doc_folder(self):
        self.browse_folder(self.edtScannedIdDoc.text()) 

    def browse_folder(self, folder):
        if folder == '':
            return
        # windows
        if sys.platform.startswith('win32'):
            os.startfile(folder)

        # *nix systems
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', folder])
        
        # macOS
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', folder])

    def enable_family_photo(self, checked):
        self.edtFamilyFolder.setEnabled(checked)

    def enable_signature(self, checked):
        self.edtSignFolder.setEnabled(checked)

    def enable_house_photo(self, checked):
        self.edtHouseFolder.setEnabled(checked)

    def enable_house_pic(self, checked):
        self.edtHousePic.setEnabled(checked)

    def enable_id_pic(self, checked):
        self.edtIdPic.setEnabled(checked)

    def enable_scanned_doc(self, checked):
        self.edtScannedDoc.setEnabled(checked)

    def enable_scanned_hse_map(self, checked):
        self.edtScannedHseMap.setEnabled(checked)

    def enable_scanned_hse_pic(self, checked):
        self.edtScannedHsePic.setEnabled(checked)

    def enable_scanned_id_doc(self, checked):
        self.edtScannedIdDoc.setEnabled(checked)

    def ErrorInfoMessage(self, message):
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()

    def fetch_selected_cols(self, doc_cols):
        """
        Extract text containing path from QLineEdit objects, only
        select from QLineEdits that are Enabled.
        Returns dict of {'csv_column_name':'path'}
        """
        sel_cols = {}
        for k, v in doc_cols.iteritems():
            line_edit = self.findChild(QLineEdit, v)
            if line_edit is None: continue
            if line_edit.isEnabled():
                sel_cols[k.lower()]=line_edit.text()
        return sel_cols

    def get_key_field(self, doc_cols):
        """
        Return the column name in the CSV that represents
        a key field.
        """
        for k, v in doc_cols.iteritems():
            if v == 'KEY':
                return k

    def fetch_doc_cols(self, media_columns):
        """
        Reads values from the mapfile to create a dict of
        {'csv_column_name':name_of_QLineEdit_with_dest_path}
        e.g. {'House Picture':'edtHousePic'}
        :rtype dict
        """
        cols = {}
        for k,v in media_columns.iteritems():
            a_col = unicode(k, 'utf-8').encode('ascii', 'ignore')
            cols[a_col] = v
        return cols

    def kobo_download_started(self, msg):
        self.btnDownload.setEnabled(False)
        self.edtProgress.append(msg+" started...")
        QApplication.processEvents()

    def kobo_download_completed(self, msg):
        self.btnDownload.setEnabled(True)
        self.edtProgress.setTextColor(QColor(51, 182, 45))
        self.edtProgress.setFontWeight(75)
        self.edtProgress.append(msg+" completed.")
        self.downloader_thread.quit()

    def kobo_download_progress(self, info_id, msg):
        if info_id == 0: # information
            self.edtProgress.setTextColor(QColor('black'))

        if info_id == 1: # Warning
            self.edtProgress.setTextColor(QColor(255, 170, 0))

        if info_id == 2: # Error
            self.edtProgress.setTextColor(QColor('red'))

        self.edtProgress.append(msg)
        QApplication.processEvents()

        
    def _downloader_thread_started(self):
        self.kobo_downloader.start_download()

    def _uploader_thread_started(self):
        self.kobo_downloader.start_upload()

    def fix_auto_sequence(self):
        pg_fix_auto_sequence('oc_household_supporting_document', 'oc_household_supporting_document_id_seq')

    def download_media(self):
        self.fix_auto_sequence()

        if self.twDocument.currentIndex() == 1:
            if self.rbScannedDoc.isChecked():
                self.process_scanned_docs()
            else:
                self.ErrorInfoMessage("Please select document type.")
            return

        if self.txtDataSource.text() == "":
            self.ErrorInfoMessage("Please select a source file.")
            return

        if not QFile.exists(unicode(self.txtDataSource.text())):
            self.ErrorInfoMessage("The specified source file does not exist.")
            return

        if self.rbKoboMedia.isChecked():
            save_location = 'media-column'
            upload_after = False

        if self.rbSupportDoc.isChecked():
            save_location = 'support-doc-column'
            upload_after = True

        src_cols = mapfile_section(save_location)
        doc_types = mapfile_section('doc-types')
        media_columns = mapfile_section(save_location)
        doc_cols =self.fetch_doc_cols(media_columns)
        sel_cols = self.fetch_selected_cols(doc_cols)
        key_field = self.get_key_field(doc_cols);

        if not self.valid_credentials():
            return

        credentials = (self.edtKoboUsername.text(),
                 self.edtKoboPassword.text())
        
        kobo_url = self.edtMediaUrl.text()
        save_media_url(kobo_url)
        save_kobo_user(credentials[0])

        support_doc_map = mapfile_section('support-doc-map')

        parent_ref_column = support_doc_map['parent_ref_column']

        self.kobo_downloader = KoboDownloader(
                self,
                OGRReader(unicode(self.txtDataSource.text())),
                sel_cols, key_field, doc_types, credentials, kobo_url, support_doc_map,
                self.curr_profile, upload_after, parent_ref_column)

        self.downloader_thread = QThread(self)
        self.kobo_downloader.moveToThread(self.downloader_thread)

        self.kobo_downloader.download_started.connect(self.kobo_download_started)
        self.kobo_downloader.download_progress.connect(self.kobo_download_progress)
        self.kobo_downloader.download_completed.connect(self.kobo_download_completed)

        self.downloader_thread.started.connect(self._downloader_thread_started)
        self.downloader_thread.finished.connect(self.downloader_thread.deleteLater)

        self.downloader_thread.start()

    def close_window(self):
        self.close()

    def process_scanned_docs(self):
        doc_types = mapfile_section('doc-types')
        src_cols = mapfile_section('scanned-doc-column')
        sel_cols = self.fetch_selected_cols(src_cols)
        key_field = self.get_key_field(src_cols);
        support_doc_map = mapfile_section('support-doc-map')
        parent_ref_column = support_doc_map['scanned_certificate']
        self.kobo_downloader = KoboDownloader(
                self,
                None,
                sel_cols, 
                key_field, 
                doc_types, 
                ('',''), 
                '', 
                support_doc_map,
                self.curr_profile, True,
                parent_ref_column,
                ref_type='str')

        self.downloader_thread = QThread(self)
        self.kobo_downloader.moveToThread(self.downloader_thread)

        self.kobo_downloader.download_started.connect(self.kobo_download_started)
        self.kobo_downloader.download_progress.connect(self.kobo_download_progress)
        self.kobo_downloader.download_completed.connect(self.kobo_download_completed)

        self.downloader_thread.started.connect(self._uploader_thread_started)
        self.downloader_thread.finished.connect(self.downloader_thread.deleteLater)

        self.downloader_thread.start()

    def disable_download_button(self):
        self.btnDownload.setEnabled(False)
        self.btnDownload.setStyleSheet("")

    def page_changed(self, page_index):
        self.disable_download_button()
        if page_index == 0:
            self.downloader_mode = DOWNLOAD_DOCS
            self.btnDownload.setText('Download')
            self.gbProgress.setTitle("Download Progress:")

            if self.rbKoboMedia.isChecked():
                self.kobo_media_clicked()

            if self.rbSupportDoc.isChecked():
                self.support_doc_clicked()

        if page_index == 1:
            self.downloader_mode = UPLOAD_DOCS
            self.btnDownload.setText('Upload')
            self.gbProgress.setTitle("Upload Progress:")
            self.scanned_doc_clicked()
        

class KoboDownloader(QObject):
    download_started = pyqtSignal(unicode)
    #Signal contains message type and message
    download_progress = pyqtSignal(int, unicode)
    #Signal indicates True if the update succeeded, else False.
    download_completed = pyqtSignal(unicode)

    INFORMATION, WARNING, ERROR = range(0, 3)
    
    def __init__(self, ui, data_reader, sel_cols, key_field, 
            doc_types, credentials, kobo_url, support_doc_map, 
            curr_profile, upload_after, parent_ref_column, ref_type='int', parent=None):

        QObject.__init__(self, parent)

        self.ui = ui  # get the UI environment
        self.downloaded_files = {}      # key: key_field_value, value: list of tuple of (doc_type_id, dest_url)
        self.data_reader = data_reader
        self.selected_cols = sel_cols   
        self.key_field = key_field
        self.doc_types = doc_types
        self.credentials = credentials
        self.kobo_url = kobo_url
        self.support_doc_map = support_doc_map
        self.curr_profile = curr_profile
        self.upload_after = upload_after
        self.parent_ref_column = parent_ref_column
        self.ref_type = ref_type

    def start_download(self):
        self.download_started.emit('Download')
        downloaded_files = self.run()
        print(downloaded_files)
        if self.upload_after:
            self.upload_downloaded_files(downloaded_files)
        self.download_completed.emit('Download')

    def start_upload(self):
        self.download_started.emit('Upload')

        if self.ui.cbScannedDoc.isChecked():
            dfiles = self.fetch_scanned_certificates()
            self.upload_downloaded_files(dfiles)

        if self.ui.cbScannedHseMap.isChecked():
            dfiles = self.fetch_scanned_docs('house map')
            self.upload_downloaded_files(dfiles)

        if self.ui.cbScannedHsePic.isChecked():
            dfiles = self.fetch_scanned_docs('house pictures')
            self.upload_downloaded_files(dfiles)

        if self.ui.cbScannedIdDoc.isChecked():
            dfiles = self.fetch_scanned_docs('id documents')
            self.upload_downloaded_files(dfiles)

        self.download_completed.emit('Upload')

    def run(self):
        file_names = []
        key_field_value = 0
        src_cols = self.data_reader.getFields()
        lyr = self.data_reader.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        numFeat = lyr.GetFeatureCount()

        feat_len = len(lyr)
        for index, feat in enumerate(lyr):

            msg = 'Record: {} of {}'.format(str(index+1), str(feat_len))
            self.download_progress.emit(KoboDownloader.INFORMATION, msg)

            # loop through the columns in the CSV file.
            for f in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(f)
                field_name = field_defn.GetNameRef()
                a_field_name = unicode(field_name, 'utf-8').encode('ascii', 'ignore').lower()

                # Get the Key Field value for later use
                if a_field_name == self.key_field:
                    key_field_value = feat.GetField(f)
                    continue

                # We are dealing with only columns that have been selected in the mapfile
                if a_field_name not in self.selected_cols.keys():
                    continue

                #dest_folder = ''
                dest_folder = self.selected_cols[a_field_name]
                field_value = feat.GetField(f)

                if field_value == '': continue

                dest_url = dest_folder + '\\'+field_value
                src_url = self.kobo_url+field_value

                msg = 'Downloading File: {} '.format(field_value)

                self.download_progress.emit(KoboDownloader.INFORMATION, msg)

                # download file
                self.download(src_url, dest_url, self.credentials[0], self.credentials[1])

                if a_field_name in self.doc_types:
                    doc_type_id = self.doc_types[a_field_name]
                else:
                    doc_type_id = -1

                file_names.append(
                        {'doc_type_id':doc_type_id, 
                         'key_field_value':key_field_value,
                         'filename':dest_url
                            })

            for fnames in file_names:
                fnames['key_field_value'] = key_field_value

            if key_field_value in self.downloaded_files:
                self.downloaded_files[key_field_value].extend(file_names)
            else:
                self.downloaded_files[key_field_value] = copy.deepcopy(file_names)

            file_names = []

        return self.downloaded_files

    def fetch_scanned_certificates(self):
        """
        Return a dict of {'filename':[{'doc_type_id', 'key_field_value', 'filename'}]}
        :filename: Physical name of the file on the disk
        :doc_type_id: Id picked from lookup "oc_check_household_document_type"
        :src_dir : Path where the file is found in the disk
        """
        dtype = 'scanned certificate'  
        dfiles = {}

        src_folder = self.selected_cols.get(dtype) # local folder with scanned certificates

        if src_folder is None or src_folder=='':
            return dfiles

        dtype_id = self.doc_types[dtype]  # ID for document of type "Scanned certificate" in table "check_document_type"

        for filename in os.listdir(src_folder):
            if fnmatch.fnmatch(filename, '*.pdf'):
                name, file_ext = os.path.splitext(filename)
                doc_src = []
                full_path = src_folder+'\\'+filename
                doc_src.append(
                        {'doc_type_id':dtype_id,
                         'key_field_value':unicode(name),
                         'filename':full_path})
                dfiles[unicode(name)]=doc_src
        return dfiles

    def fetch_scanned_docs(self, doc_type):
        """
        Return a dict of {'filename':[{'doc_type_id':, key_field_value':, 'filename':}]}
        :rtype dict:
        """
        dfiles = {}
        src_folder = self.selected_cols.get(doc_type)

        if src_folder is None or src_folder == '':
            return dfiles

        dtype_id = self.doc_types[doc_type]
        for filename in os.listdir(src_folder):
            if fnmatch.fnmatch(filename, '*.jpg'):
                name, file_ext = os.path.splitext(filename)
                orig_name = name
                # clean-up any postfix numbers in the filename
                split_name = name.split('_', 2)
                if len(split_name) > 1:
                    name = split_name[0]+'_'+split_name[1]
                else:
                    name = split_name[0]
                doc_src = []
                full_path = src_folder+'\\'+filename
                doc_src.append(
                        {'doc_type_id':dtype_id, 
                         'key_field_value':name, 
                         'filename':full_path})
                dfiles[orig_name]=doc_src
        return dfiles

    def upload_downloaded_files(self, downloaded_files):
        #1. Create and get ID from the supporting documents table
        #2. Get Household ID
        #3. Get ID of document type 
        #4. Create a record of entity_supporting_document
        if len(downloaded_files) == 0:
            return

        doc_type_cache = {}

        msg = "Uploading files to STDM started ..."
        self.download_progress.emit(KoboDownloader.INFORMATION, msg)

        for key, value in downloaded_files.iteritems():
            ref_code = value[0]['key_field_value']

            try:
                parent_id = self.get_parent_id(self.support_doc_map['parent_table'],
                                                     ref_code, self.parent_ref_column)
            except:
                parent_id = None

            if parent_id is None:
                msg = "ERROR. No record found for key: "+str(ref_code)
                self.download_progress.emit(KoboDownloader.ERROR, msg)
                continue

            for sfile in downloaded_files[key]:

                try:
                    src_doc_type = sfile['doc_type_id'] 
                    short_filename = sfile['key_field_value'] 
                    full_filename = sfile['filename']  # full path of the source file

                    msg = "Uploading file: "+short_filename
                    self.download_progress.emit(KoboDownloader.INFORMATION, msg)

                    support_doc = self.make_supporting_doc_dict(full_filename, self.support_doc_map)
                    if support_doc is None:
                        msg = "ERROR: Unable to create supporting document for file: {}".format(full_filename)
                        self.download_progress.emit(KoboDownloader.ERROR, msg)
                        continue

                    # Create a record in the supporting document table (oc_supporting_document)
                    #pg_create_supporting_document(support_doc)
                    #next_support_doc_id = get_last_id(self.support_doc_map['main_table'])

                    result_obj = pg_create_supporting_document(support_doc)
                    next_support_doc_id = result_obj.fetchone()[0]
                    support_doc_table = self.support_doc_map['parent_support_table']

                    # Create a record in the parent table supporting document table (oc_household_supporting_document)
                    # parent table is "oc_household"
                    self.create_supporting_doc(support_doc_table, next_support_doc_id, parent_id, int(src_doc_type))

                    # copy file to STDM supporting document path
                    if src_doc_type in doc_type_cache:
                        doc_type = doc_type_cache[src_doc_type]
                    else:
                        doc_type = get_value_by_column(
                                table_name=self.support_doc_map['doc_type_table'],
                                target_col='value', 
                                where_col='id', 
                                value=src_doc_type)
                        doc_type_cache[src_doc_type] = doc_type

                    new_filename = support_doc['doc_identifier']
                    self.create_new_support_doc_file(sfile, new_filename, doc_type, self.support_doc_map)
                except:
                    msg = "ERROR Uploading. File not found!: "+full_filename
                    self.download_progress.emit(KoboDownloader.ERROR, msg)

        
    def get_parent_id(self, parent_table, value, parent_ref_column):
        """
        Retrieve the parent record ID based on a unique reference.

        :param parent_table: Name of the parent table
        :param value: Search value for the reference column
        :param parent_ref_column: Name of the reference column
        :return: Parent record ID or None if not found
        :rtype: int or None
        """
        if self.ref_type != 'int':
            value = "'{}'".format(value)
        
        parent_id = get_value_by_column(
            table_name=parent_table,
            target_col='id',
            where_col=parent_ref_column,
            value=value
        )
        
        return parent_id


    def make_supporting_doc_dict(self, doc_name, doc_map):
        try:
            doc_size = os.path.getsize(doc_name)
            path, filename = os.path.split(doc_name)
            ht = hashlib.sha1(filename.encode('utf-8'))
            document = {
                'support_doc_table': doc_map['main_table'],
                'creation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'doc_identifier': ht.hexdigest(),
                'source_entity': doc_map['parent_table'],
                'doc_filename': filename,
                'document_size': doc_size
            }
            return document
        except FileNotFoundError:
            self.download_progress.emit(KoboDownloader.ERROR, "File not found: {}".format(doc_name))
            return None
        except Exception as e:
            self.download_progress.emit(KoboDownloader.ERROR, "Error processing file {}: {}".format(doc_name, str(e)))
            return None

        # write to db
        #pg_create_supporting_document(document)

    def create_supporting_doc(self, table_name, next_doc_id, household_id, doc_type_id):
        pg_create_parent_supporting_document(table_name, next_doc_id, household_id, doc_type_id)

    def create_new_support_doc_file(self, old_file, new_filename, dtype, support_doc_map):
        self.reg_config = RegistryConfig()
        support_doc_path = self.reg_config.read([NETWORK_DOC_RESOURCE])
        old_file_type = old_file['doc_type_id']  #old_file[0]
        old_filename = old_file['filename']  #old_file[2]
        name, file_ext = os.path.splitext(old_filename)

        doc_path = support_doc_path.values()[0]
        profile_name = self.curr_profile.name
        entity_name = support_doc_map['parent_table']
        doc_type = dtype.replace(' ','_').lower()

        dest_path = doc_path+'/'+profile_name.lower()+'/'+entity_name+'/'+doc_type+'/'
        dest_filename = dest_path+new_filename+file_ext

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        shutil.copy(old_filename, dest_filename)

    def download(self, src_url, dest_url, username, password):

        req = requests.get(src_url, auth=(username,password))

        with open(dest_url, 'wb') as f:
            f.write(req.content)

        return req.status_code

    def fake_download(self, src_url, dest_url, username, password):
        return 200
        
