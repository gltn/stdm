import os
import shutil
import sys
import copy
from collections import OrderedDict
from datetime import datetime
import hashlib

from PyQt4.QtGui import (
        QApplication,
        QDialog,
        QFileDialog,
        QMessageBox,
        QLineEdit
  )

from PyQt4.QtCore import (
    Qt,
    QFile,
    QFileInfo,
    SIGNAL,
    QSignalMapper
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
        save_media_url,
        save_kobo_user,
        save_kobo_pass,
        save_family_photo,
        save_sign_photo,
        save_house_photo,
        save_house_pic,
        save_id_pic
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
    pg_create_parent_supporting_document
)

from stdm.data.importexport.reader import OGRReader

from ui_document_downloader import Ui_DocumentDownloader

class DocumentDownloader(QDialog, Ui_DocumentDownloader):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self) 
        self.btnBrowseSource.clicked.connect(self.set_source_file)
        self.btnHide.clicked.connect(self.hideWindow)
        self.rbKoboMedia.clicked.connect(self.kobo_media_clicked)
        self.rbSupportDoc.clicked.connect(self.support_doc_clicked)

        self.tbFamilyFolder.clicked.connect(self.family_folder)
        self.tbSignFolder.clicked.connect(self.sign_folder)
        self.tbHouseFolder.clicked.connect(self.house_folder)
        self.tbHousePic.clicked.connect(self.house_pic_folder)
        self.tbIdPic.clicked.connect(self.id_pic_folder)

        self.btnDownload.clicked.connect(self.download_media)

        self.btnFamilyBrowse.clicked.connect(self.show_family_folder)
        self.btnSignFolder.clicked.connect(self.show_sign_folder)
        self.btnHouseFolder.clicked.connect(self.show_house_folder)
        self.btnHousePic.clicked.connect(self.show_house_pic_folder)
        self.btnIdPic.clicked.connect(self.show_id_pic_folder)

        self.cbFamilyPhoto.toggled.connect(self.enable_family_photo)
        self.cbSign.toggled.connect(self.enable_signature)
        self.cbHousePhoto.toggled.connect(self.enable_house_photo)
        self.cbHousePic.toggled.connect(self.enable_house_pic)
        self.cbIdPic.toggled.connect(self.enable_id_pic)

        #Data Reader
        self.dataReader = None
        self.curr_profile = current_profile()

        self.read_kobo_defaults()
        self.check_download_all()

        self.rbKoboMedia.setChecked(True)
        self.toggleSupportDoc(False)

    def hideWindow(self):
        self.hide()

    def kobo_media_clicked(self):
        if self.rbKoboMedia.isChecked():
            self.toggleKoboOptions(True)
            self.toggleSupportDoc(False)

    def support_doc_clicked(self):
        if self.rbSupportDoc.isChecked():
            self.toggleSupportDoc(True)
            self.toggleKoboSettings(True)
            self.toggleMediaFolders(False)

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

    def check_download_all(self):
        self.cbFamilyPhoto.setCheckState(Qt.Checked)
        self.cbSign.setCheckState(Qt.Checked)
        self.cbHousePhoto.setCheckState(Qt.Checked)
        self.cbHousePic.setCheckState(Qt.Checked)
        self.cbIdPic.setCheckState(Qt.Checked)

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

    def select_media_folder(self, dflt_folder):
        title = self.tr("Folder to store media files")
        trans_path = QFileDialog.getExistingDirectory(self, title, dflt_folder)
        return trans_path

    def download_media(self):
        if self.txtDataSource.text() == "":
            self.ErrorInfoMessage("Please select a source file.")
            return

        if not QFile.exists(unicode(self.txtDataSource.text())):
            self.ErrorInfoMessage("The specified source file does not exist.")
            return

        if self.rbKoboMedia.isChecked():
            downloaded_files = self.download_kobo_media('media-column')

        if self.rbSupportDoc.isChecked():
            downloaded_files = self.download_kobo_media('support-doc-column')
            print downloaded_files
            self.upload_downloaded_files(downloaded_files)

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

    def download_kobo_media(self, save_location):
        #1. check if url is blank
        #2. check if username is blank
        #3. check if password is blank
        #4. check that the source document is selected

        downloaded_files = {}
        file_names = []
        key_field_value = 0

        #Read the mapfile to get the edit controls with the 
        # path where to save the different media files
        media_columns = mapfile_section(save_location)
        ucols = {}
        for k,v in media_columns.iteritems():
            a_col = unicode(k, 'utf-8').encode('ascii', 'ignore')
            ucols[a_col] = v

        # Get document type ids
        doc_types = mapfile_section('doc-types')

        data_reader = OGRReader(unicode(self.txtDataSource.text()))
        src_cols = data_reader.getFields()

        lyr = data_reader.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        numFeat = lyr.GetFeatureCount()

        if not self.valid_credentials:
            return

        username = self.edtKoboUsername.text()
        password = self.edtKoboPassword.text()

        save_media_url(self.edtMediaUrl.text())
        save_kobo_user(username)

        feat_len = len(lyr)
        try:
            self.btnDownload.setEnabled(False)
            for index, feat in enumerate(lyr):
                self.lblCurrRecord.setText(str(index+1)+' of '+ str(feat_len))

                print "** A **"

                for f in range(feat_defn.GetFieldCount()):
                    field_defn = feat_defn.GetFieldDefn(f)
                    field_name = field_defn.GetNameRef()
                    a_field_name = unicode(field_name, 'utf-8').encode('ascii', 'ignore').lower()

                    dest_folder = ''
                    if a_field_name in ucols:
                        if ucols[a_field_name] == 'KEY':
                            key_field_value = feat.GetField(f)
                            continue

                        print "** C **"
                        line_edit = self.findChild(QLineEdit, ucols[a_field_name])
                        if line_edit.isEnabled():
                            dest_folder = line_edit.text()
                            field_value = feat.GetField(f)

                            if field_value == '': continue

                            self.lblCurrFile.setText(field_value)

                            dest_url = dest_folder + '\\'+field_value
                            src_url = self.edtMediaUrl.text()+field_value

                            QApplication.processEvents()

                            print "** D **"
                            #self.download(src_url, dest_url, username, password)


                            if a_field_name in doc_types:
                                doc_type_id = doc_types[a_field_name]
                            else:
                                doc_type_id = -1

                            file_names.append((doc_type_id, dest_url))

                if key_field_value in downloaded_files:
                    downloaded_files[key_field_value].extend(file_names)
                else:
                    downloaded_files[key_field_value] = copy.deepcopy(file_names)

                print "** F **"
                print downloaded_files

                file_names = []

            self.btnDownload.setEnabled(True)
        except:
            self.btnDownload.setEnabled(True)

        return downloaded_files

    def valid_credentials(self):
        if self.edtMediaUrl.text() == '':
            self.ErrorInfoMessage("Source of media files")
            return false

        if self.edtKoboUsername.text() == '':
            self.ErrorInfoMessage("Please enter username")
            return false

        if self.edtKoboPassword.text() == '':
            self.ErrorInfoMessage("Please enter password")
            return false

    def download(self, src_url, dest_url, username, password):
        import requests

        self.lblMsg.setText('Downloading ...')
        QApplication.processEvents()
        req = requests.get(src_url, auth=(username,password))

        with open(dest_url, 'wb') as f:
            f.write(req.content)

        self.lblMsg.setText('Done.')
        return req.status_code

    def upload_downloaded_files(self, downloaded_files):
        #1. Create and get ID from the supporting documents table
        #2. Get Household ID
        #3. Get ID of document type 
        #4. Create a record of entity_supporting_document
        doc_type_cache = {}

        support_doc_map = mapfile_section('support-doc-map')
        for submission_id in downloaded_files.keys():
            household_id = self.get_household_id(support_doc_map, submission_id)
            if household_id is None:
                continue
            last_support_doc_id = get_last_id(support_doc_map['main_table'])
            for sfile in downloaded_files[submission_id]:
                new_filename = self.create_supporting_doc(sfile[1], support_doc_map)
                last_support_doc_id += 1
                parent_support_table = support_doc_map['parent_support_table']

                self.create_parent_supporting_doc(parent_support_table, last_support_doc_id, household_id, int(sfile[0]))

                # copy file to STDM supporting document path
                if sfile[0] in doc_type_cache:
                    doc_type = doc_type_cache[sfile[0]]
                else:
                    doc_type = get_value_by_column(
                            support_doc_map['doc_type_table'], 'value', 'id', sfile[0])
                    doc_type_cache[sfile[0]] = doc_type

                self.create_new_support_doc_file(sfile, new_filename, doc_type, support_doc_map)

    def get_household_id(self, doc_map, value):
        table_name = doc_map['parent_table']
        target_col = 'id'
        where_col = doc_map['parent_ref_column']
        id = get_value_by_column(table_name, target_col, where_col, value)
        return id

    def create_supporting_doc(self, doc_name, doc_map):
        doc_size = 0  #os.path.getsize(doc_name)
        path, filename = os.path.split(doc_name)
        ht = hashlib.sha1(filename.encode('utf-8'))
        document = {}
        document['support_doc_table'] = doc_map['main_table']
        document['creation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        document['doc_identifier'] = ht.hexdigest()
        document['source_entity'] = doc_map['parent_table']
        document['doc_filename'] = filename
        document['document_size'] = doc_size

        # write to db
        pg_create_supporting_document(document)

        return document['doc_identifier']

    def create_parent_supporting_doc(self, table_name, doc_id, household_id, doc_type_id):
        pg_create_parent_supporting_document(table_name, doc_id, household_id, doc_type_id)

    def create_new_support_doc_file(self, old_file, new_filename, dtype, support_doc_map):
        self.reg_config = RegistryConfig()
        support_doc_path = self.reg_config.read([NETWORK_DOC_RESOURCE])
        old_file_type = old_file[0]
        old_filename = old_file[1]
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

    def ErrorInfoMessage(self, message):
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()


