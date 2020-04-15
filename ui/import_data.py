"""
/***************************************************************************
Name                 : Data Import Wizard
Description          : LEGACY CODE, NEEDS TO BE UPDATED.
                       Import spatial and textual data into STDM database
Date                 : 24/February/12
copyright            : (C) 2012 by John Gitau
email                : gkahiu@gmail.com 
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
import sys
import copy
from collections import OrderedDict
from datetime import datetime
import hashlib

from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    QFile,
    QFileInfo,
    SIGNAL,
    QSignalMapper
)

from stdm.utils import *
from stdm.utils.util import getIndex, enable_drag_sort_widgets, mapfile_section
from stdm.data.database import alchemy_table_relationships
from stdm.data.pg_utils import (
    table_column_names,
    pg_tables,
    spatial_tables,
    get_last_id,
    get_value_by_column,
    pg_create_supporting_document,
    pg_create_parent_supporting_document
)

from stdm.data.importexport import (
    vectorFileDir,
    setVectorFileDir
)

from stdm.data.importexport.value_translators import (
        ValueTranslatorManager,
        LookupValueTranslator,
        RelatedTableTranslator,
        SourceDocumentTranslator
        )

from stdm.data.importexport.reader import OGRReader

from .importexport import (
    ValueTranslatorConfig,
    TranslatorWidgetManager,
    LookupTranslatorConfig,
    RelatedTableTranslatorConfig
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

from stdm.utils.util import (
    profile_user_tables,
    profile_spatial_tables
)
from .ui_import_data import Ui_frmImport

class ImportData(QWizard, Ui_frmImport):
    def __init__(self,parent=None):
        QWizard.__init__(self,parent)
        self.setupUi(self) 
        self.curr_profile = current_profile()

        #Connect signals   
        self.btnBrowseSource.clicked.connect(self.setSourceFile)
        self.lstDestTables.itemClicked.connect(self.destSelectChanged)
        self.btnSrcUp.clicked.connect(self.srcItemUp)
        self.btnSrcDown.clicked.connect(self.srcItemDown)
        self.btnSrcAll.clicked.connect(self.checkSrcItems)
        self.btnSrcNone.clicked.connect(self.uncheckSrcItems)
        self.btnDestUp.clicked.connect(self.targetItemUp)
        self.btnDestDown.clicked.connect(self.targetItemDown)
        self.lstSrcFields.currentRowChanged[int].connect(self.sourceRowChanged)
        self.lstTargetFields.currentRowChanged[int].connect(self.destRowChanged)
        self.lstTargetFields.currentRowChanged[int].connect(self._enable_disable_trans_tools)
        self.chk_virtual.toggled.connect(self._on_load_virtual_columns)

        self.rbTextType.clicked.connect(self.text_type_clicked)
        self.rbSpType.clicked.connect(self.sptype_clicked)
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
         
        #Init
        self.registerFields()
        
        #Geometry columns
        self.geomcols = []

        self._trans_widget_mgr = TranslatorWidgetManager(self)

        #self.auto_load_translators()

        #Initialize value translators from definitions
        self._init_translators()

        self.read_kobo_defaults()

        self.check_download_all()

        self.toggleKoboOptions(False)
        self.toggleSupportDoc(False)

        #self._set_target_fields_stylesheet()

    def text_type_clicked(self):
        if self.rbTextType.isChecked():
            self.toggleKoboOptions(False)
            self.toggleSupportDoc(False)
            if self.txtDataSource.text() <> '':
                self.button(QWizard.NextButton).setEnabled(True)

    def sptype_clicked(self):
        if self.rbSpType.isChecked():
            self.toggleKoboOptions(False)
            self.toggleSupportDoc(False)
            if self.txtDataSource.text() <> '':
                self.button(QWizard.NextButton).setEnabled(True)


    def kobo_media_clicked(self):
        if self.rbKoboMedia.isChecked():
            self.toggleKoboOptions(True)
            self.toggleSupportDoc(False)
            self.button(QWizard.NextButton).setEnabled(False)

    def support_doc_clicked(self):
        if self.rbSupportDoc.isChecked():
            self.toggleSupportDoc(True)
            self.toggleKoboSettings(True)
            self.toggleMediaFolders(False)
            self.button(QWizard.NextButton).setEnabled(False)

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

    def read_kobo_defaults(self):
        self.edtMediaUrl.setText(get_media_url())
        self.edtKoboUsername.setText(get_kobo_user())
        self.edtFamilyFolder.setText(get_family_photo())
        self.edtSignFolder.setText(get_sign_photo())
        self.edtHouseFolder.setText(get_house_photo())
        self.edtHousePic.setText(get_house_pic())
        self.edtIdPic.setText(get_id_pic())

    def download_media(self):
        if not QFile.exists(unicode(self.txtDataSource.text())):
            self.ErrorInfoMessage("The specified source file does not exist.")
            return

        if self.rbKoboMedia.isChecked():
            save_location = 'media-column'
            downloaded_files = self.download_kobo_media('media-column')

        if self.rbSupportDoc.isChecked():
            save_location = 'support-doc-column'
            downloaded_files = self.download_kobo_media('support-doc-column')
            self.upload_downloaded_files(downloaded_files)

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

                for f in range(feat_defn.GetFieldCount()):
                    field_defn = feat_defn.GetFieldDefn(f)
                    field_name = field_defn.GetNameRef()
                    a_field_name = unicode(field_name, 'utf-8').encode('ascii', 'ignore').lower()

                    dest_folder = ''
                    if a_field_name in ucols:
                        if ucols[a_field_name] == 'KEY':
                            key_field_value = feat.GetField(f)
                            continue

                        line_edit = self.findChild(QLineEdit, ucols[a_field_name])
                        if line_edit.isEnabled():
                            dest_folder = line_edit.text()
                            field_value = feat.GetField(f)

                            if field_value == '': continue

                            self.lblCurrFile.setText(field_value)

                            dest_url = dest_folder + '\\'+field_value
                            src_url = self.edtMediaUrl.text()+field_value

                            QApplication.processEvents()

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
            print "***BEFORE***"
            for sfile in downloaded_files[submission_id]:
                new_filename = self.create_supporting_doc(sfile[1], support_doc_map)
                last_support_doc_id += 1
                print last_support_doc_id
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

    def _init_translators(self):
        translator_menu = QMenu(self)

        #self._trans_widget_mgr = TranslatorWidgetManager(self)
        self._trans_signal_mapper = QSignalMapper(self)

        for trans_name, config in ValueTranslatorConfig.translators.iteritems():
            trans_action = QAction( u'{}...'.format(trans_name),
                translator_menu
            )

            self._trans_signal_mapper.setMapping(trans_action, trans_name)
            trans_action.triggered.connect(self._trans_signal_mapper.map)

            translator_menu.addAction(trans_action)

        if len(translator_menu.actions()) == 0:
            self.btn_add_translator.setEnabled(False)

        else:
            self.btn_add_translator.setMenu(translator_menu)

            self._trans_signal_mapper.mapped[str].connect(self._load_translator_dialog)

        self.btn_edit_translator.setEnabled(False)
        self.btn_delete_translator.setEnabled(False)

        self.btn_edit_translator.clicked.connect(self._on_edit_translator)
        self.btn_delete_translator.clicked.connect(self._on_delete_translator)

    def auto_load_translators(self):
        srclookups = mapfile_section('lookups')
        dstlookups = mapfile_section('lookup-defaults')
        trans_sec = self.target_table_shortname(self.targetTab)+'-translators'
        translators = mapfile_section(trans_sec)

        for dest_column, lookup_table in dstlookups.iteritems():

            lookup_type = translators.get(dest_column)
            if lookup_type is None: continue
            # Single Select Lookups
            if lookup_type == 'lookup':

                config_key ="Lookup values"
                trans_config = ValueTranslatorConfig.translators.get(config_key, None)
                src_column = self._get_src_column(lookup_table, srclookups)
                if src_column is None:
                    continue

                trans_dlg = trans_config.create(
                    self,
                    [],
                    self.targetTab,
                    dest_column,
                    src_column,
                    dflt_lookups=dstlookups.values()
                )

                trans_dlg.auto_lookup_translator = LookupValueTranslator()
                trans_dlg.auto_lookup_translator.set_referenced_table(lookup_table)
                trans_dlg.auto_lookup_translator.set_referencing_table(self.targetTab)
                trans_dlg.auto_lookup_translator.set_referencing_column(dest_column)
                trans_dlg.auto_lookup_translator.set_referenced_table(lookup_table)
                trans_dlg.auto_lookup_translator.add_source_reference_column(src_column, dest_column)
                trans_dlg.auto_lookup_translator.default_value = ''

                self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

            # Related Entities
            if lookup_type == 'relatedentity':

                config_key ="Related table"
                trans_config = ValueTranslatorConfig.translators.get(config_key, None)

                map_sec = self.targetTab[3:]+'-'+dest_column+'-relatedentity'
                rel_values = mapfile_section(map_sec)
                config_key ="Related table"
                dest_table = rel_values['dest_table']
                dest_column = rel_values['dest_column']

                ref_table = rel_values['reftable']
                ref_output_column = rel_values['ref_output_col']

                col_pairs = {}
                col_pairs[rel_values['src_table_field']] = rel_values['ref_table_field']

                #trans_config = ValueTranslatorConfig.translators.get(config_key, None)
                trans_dlg = trans_config.create(
                    self,
                    [],
                    self.targetTab,
                    dest_column,
                    src_column,
                    dflt_lookups=rel_values
                )

                trans_dlg.auto_rel_translator = RelatedTableTranslator()
                trans_dlg.auto_rel_translator.set_referencing_table(self.targetTab)
                trans_dlg.auto_rel_translator.set_referencing_column(dest_column)
                trans_dlg.auto_rel_translator.set_referenced_table(ref_table)
                trans_dlg.auto_rel_translator.set_output_reference_column(ref_output_column)
                trans_dlg.auto_rel_translator.set_input_referenced_columns(col_pairs)

                self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

            if lookup_type == 'supporting_document':

                config_key ="Supporting documents"
                trans_config = ValueTranslatorConfig.translators.get(config_key, None)

                src_column = self._get_sd_src_column(self.targetTab, dest_column)

                trans_dlg = trans_config.create(
                    self,
                    [],
                    self.targetTab,
                    dest_column.replace('_',' ').title(),
                    src_column
                )


                trans_dlg.auto_src_translator = SourceDocumentTranslator()
                trans_dlg.auto_src_translator.set_referencing_table(self.targetTab)
                trans_dlg.auto_src_translator.set_referencing_column(dest_column)

                #Just use the source column for getting the relative image path
                # and name
                trans_dlg.auto_src_translator.add_source_reference_column(
                    src_column,
                    dest_column
                )
                trans_dlg.auto_src_translator.entity = trans_dlg.entity()
                trans_dlg.auto_src_translator.document_type_id = trans_dlg._document_type_id
                trans_dlg.auto_src_translator.document_type = dest_column

                support_docs = mapfile_section('support_docs-defaults')
                trans_dlg.auto_src_translator.source_directory = support_docs[dest_column]

                self._trans_widget_mgr.add_widget(dest_column, trans_dlg)


    def _get_src_column(self, value, srclookups):
        column = None
        for col, table in srclookups.iteritems():
            if table == value:
                column = col
                break
        return column

    def _get_sd_src_column(self, target_table, dest_col):
        column = None
        columns = mapfile_section(target_table[3:])
        for s_col, d_col in columns.iteritems():
            if d_col == dest_col:
                column = s_col
                break
        return column


    def _register_lookups(self, config_key, lookups):
        src_column = self._selected_source_column()
        for dest_column, val in lookups.iteritems():
            trans_config = ValueTranslatorConfig.translators.get(config_key, None)
            trans_dlg = trans_config.create(
                self,
                [],
                self.targetTab,
                dest_column,
                src_column,
                dflt_lookups=dlookups.values()
            )
            self._trans_widget_mgr.add_widget(dest_column, trans_dlg)


    def _load_translator_dialog(self, config_key):
        """
        Load translator dialog.
        """
        dest_column = self._selected_destination_column()
        src_column = self._selected_source_column()

        if dest_column:
            #Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            if trans_dlg is None:
                trans_config = ValueTranslatorConfig.translators.get(config_key, None)

                if trans_config is None: return

                try:
                    if trans_config.__name__ =='LookupTranslatorConfig':
                        dlookups = mapfile_section('lookups')
                        trans_dlg = trans_config.create(
                            self,
                            self._source_columns(),
                            self.targetTab,
                            dest_column,
                            src_column,
                            dflt_lookups=dlookups.values()
                        )
                    elif trans_config.__name__=='RelatedTableTranslatorConfig':
                        dlookups = mapfile_section('household_members-relatedentity')
                        trans_dlg = trans_config.create(
                            self,
                            self._source_columns(),
                            self.targetTab,
                            dest_column,
                            src_column,
                            dflt_lookups=dlookups
                        )
                    else:
                        trans_dlg = trans_config.create(
                            self,
                            self._source_columns(),
                            self.targetTab,
                            dest_column,
                            src_column
                        )

                except RuntimeError as re:
                    QMessageBox.critical(
                        self,
                        QApplication.translate(
                            'ImportData',
                            'Value Translator'
                        ),
                        unicode(re)
                    )

                    return

            #self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

            self._handle_translator_dlg(dest_column, trans_dlg)

    def _handle_translator_dlg(self, key, dlg):
        if dlg.exec_() == QDialog.Accepted:
            self._trans_widget_mgr.add_widget(key, dlg)

        self._enable_disable_trans_tools()

    def _on_edit_translator(self):
        """
        Slot to load the translator widget specific for the selected column for editing.
        """
        dest_column = self._selected_destination_column()

        if dest_column:
            #Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            self._handle_translator_dlg(dest_column, trans_dlg)

    def _on_delete_translator(self):
        """
        Slot for deleting the translator widget for the selected column.
        """
        dest_column = self._selected_destination_column()

        self._delete_translator(dest_column)

    def _delete_translator(self, destination_column):
        if not destination_column:
            return

        res = self._trans_widget_mgr.remove_translator_widget(destination_column)

        self._enable_disable_trans_tools()

    def _enable_disable_trans_tools(self, index=-1):
        """
        Enable/disable appropriate value translator tools based on the selected
        column.
        """
        dest_column = self._selected_destination_column()

        if dest_column:
            #Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            if trans_dlg is None:
                self.btn_add_translator.setEnabled(True)
                self.btn_edit_translator.setEnabled(False)
                self.btn_delete_translator.setEnabled(False)

            else:
                self.btn_add_translator.setEnabled(False)
                self.btn_edit_translator.setEnabled(True)
                self.btn_delete_translator.setEnabled(True)

        else:
            self.btn_add_translator.setEnabled(False)
            self.btn_edit_translator.setEnabled(False)
            self.btn_delete_translator.setEnabled(False)

    def _selected_destination_column(self):
        dest_field_item = self.lstTargetFields.currentItem()

        if dest_field_item is None:
            return ""

        else:
            return dest_field_item.text()

    def _selected_source_column(self):
        src_field_item = self.lstSrcFields.currentItem()

        if src_field_item is None:
            return ""

        else:
            return src_field_item.text()

    def _set_target_fields_stylesheet(self):
        self.lstTargetFields.setStyleSheet("QListWidget#lstTargetFields::item:selected"
                                           " { selection-background-color: darkblue }")

    def registerFields(self):
        #Register wizard fields
        pgSource = self.page(0)
        pgSource.registerField("srcFile*",self.txtDataSource)
        pgSource.registerField("typeText",self.rbTextType)
        pgSource.registerField("typeSpatial",self.rbSpType)
        pgSource.registerField("koboMedia",self.rbKoboMedia)
        pgSource.registerField("supportdoc",self.rbSupportDoc)
        
        #Destination table configuration
        destConf = self.page(1)
        destConf.registerField("optAppend",self.rbAppend)
        destConf.registerField("optOverwrite",self.rbOverwrite)
        destConf.registerField("tabIndex*",self.lstDestTables)
        destConf.registerField("geomCol",self.geomClm,"currentText",SIGNAL("currentIndexChanged(int)"))
        
    def initializePage(self,pageid):
        #Re-implementation of wizard page initialization
        if pageid == 1:
            #Reference to checked listwidget item representing table name
            self.destCheckedItem=None
            self.geomClm.clear()
            
            if self.field("typeText"):
                self.loadTables("textual")
                self.geomClm.setEnabled(False)
                self.toggleKoboOptions(False)
                self.toggleSupportDoc(False)
                
            elif self.field("typeSpatial"):
                self.loadTables("spatial")
                self.geomClm.setEnabled(True)
                self.toggleKoboOptions(False)
                self.toggleSupportDoc(False)

            elif self.field("koboMedia"):
                self.toggleKoboOptions(True)
                self.toggleSupportDoc(False)
                
            elif self.field("supportdoc"):
                self.toggleKoboSettings(True)
                self.toggleSupportDoc(True)
                self.toggleMediaFolders(False)

        if pageid == 2:
            self.lstSrcFields.clear()
            self.lstTargetFields.clear()
            self.assignCols()
            self.auto_load_translators()
            self._enable_disable_trans_tools()
    
    def toggleKoboOptions(self, mode):
        self.toggleKoboSettings(mode)
        self.toggleMediaFolders(mode)

    def check_download_all(self):
        self.cbFamilyPhoto.setCheckState(Qt.Checked)
        self.cbSign.setCheckState(Qt.Checked)
        self.cbHousePhoto.setCheckState(Qt.Checked)
        self.cbHousePic.setCheckState(Qt.Checked)
        self.cbIdPic.setCheckState(Qt.Checked)

    def toggleKoboSettings(self, mode):
        self.edtMediaUrl.setEnabled(mode)
        self.edtKoboUsername.setEnabled(mode)
        self.edtKoboPassword.setEnabled(mode)

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

    def toggleSupportDoc(self, mode):
        self.edtHousePic.setEnabled(mode);
        self.cbHousePic.setEnabled(mode);
        self.tbHousePic.setEnabled(mode);
        self.btnHousePic.setEnabled(mode);

        self.edtIdPic.setEnabled(mode);
        self.cbIdPic.setEnabled(mode);
        self.tbIdPic.setEnabled(mode);
        self.btnIdPic.setEnabled(mode);

    def _source_columns(self):
        """
        :rtype: list
        """
        return self.dataReader.getFields()

    def assignCols(self):
        #Load source and target columns respectively
        srcCols = self._source_columns()

        target_table = self.target_table_shortname(self.destCheckedItem.text())
        cols = mapfile_section(target_table).keys()
        ucols = {}
        for i,c in enumerate(cols):
            ucols[i] = unicode(c, 'utf-8').encode('ascii', 'ignore')

        temp = {}
        for i,f in enumerate(srcCols):
            col = f.encode('ascii', 'ignore').lstrip().lower()
            for k,v in ucols.iteritems():
                if v==col:
                    temp[k] = srcCols[srcCols.index(f)]

        order_temp = OrderedDict(sorted(temp.items()))
        for col in order_temp.values():
            srcCols.pop(srcCols.index(col))

        for k,v in order_temp.iteritems():
            srcCols.insert(k, v)
        
        for i, c in enumerate(srcCols):
            srcItem = QListWidgetItem(c,self.lstSrcFields)
            srcItem.setCheckState(Qt.Unchecked)
            if i<=len(cols)-1:
                srcItem.setCheckState(Qt.Checked)
            srcItem.setIcon(QIcon(":/plugins/stdm/images/icons/column.png"))
            self.lstSrcFields.addItem(srcItem)
            
        #Destination Columns
        tabIndex = int(self.field("tabIndex"))
        self.targetTab = self.destCheckedItem.text()
        targetCols = table_column_names(self.targetTab, False, True)

        #Remove geometry columns in the target columns list
        for gc in self.geomcols:            
            colIndex = getIndex(targetCols,gc)
            if colIndex != -1:
                targetCols.remove(gc)

        #Remove 'id' column if there
        id_idx = getIndex(targetCols, 'id')
        if id_idx != -1:
            targetCols.remove('id')

        remove_list = mapfile_section(target_table+'-remove')
        targetCols = [item for item in targetCols if str(item) not in remove_list.values()]

        # sort list according to the mapfile
        dest_cols = targetCols
        if self.sortable(target_table):
            dest_cols = self.sort_dest_cols_by_mapfile(targetCols)

        self._add_target_table_columns(dest_cols)

        virtual_cols = mapfile_section(target_table+'-virtual')
        if len(virtual_cols) > 0:
            self.chk_virtual.setChecked(True)

    def sortable(self, target_table):
        """
        :rtype: bool
        """
        sortables = mapfile_section('sortables').values()
        return True if target_table in sortables else False

    def sort_dest_cols_by_mapfile(self, dest_cols):
        target_table = self.target_table_shortname(self.destCheckedItem.text())
        map_cols = mapfile_section(target_table).values()
        sorted_cols = []
        for col in map_cols:
            if col in dest_cols:
                sorted_cols.append(col)
        return sorted_cols

    def _add_target_table_columns(self, items, style=False):
        for item in items:
            list_item = QListWidgetItem(item)

            if style:
                color = QColor(0, 128, 255)
                list_item.setTextColor(color)

            self.lstTargetFields.addItem(list_item)
                
    def _on_load_virtual_columns(self, state):
        """
        Load/unload relationships in the list of destination table columns.
        """
        virtual_columns = self.dataReader.entity_virtual_columns(self.targetTab)

        virtual_columns = [vc.lower().replace(' ','_') for vc in virtual_columns]
        remove_list = mapfile_section(self.targetTab[3:]+'-remove').values()
        virtual_columns = [item for item in virtual_columns if str(item) not in remove_list]

        if len(virtual_columns) == 0:
            return

        if state:
            if len(virtual_columns) == 0:
                msg = QApplication.translate("ImportData",
                    "There are no virtual columns for the specified table.")
                QMessageBox.warning(
                    self,
                    QApplication.translate(
                        'ImportData',
                        'Import Data'
                    ),
                    msg
                )
                self.chk_virtual.setChecked(False)

                return

            self._add_target_table_columns(virtual_columns, True)

        else:
            self._remove_destination_table_fields(virtual_columns)

    def _remove_destination_table_fields(self, fields):
        """Remove the specified columns from the destination view."""
        for f in fields:
            list_items = self.lstTargetFields.findItems(f, Qt.MatchFixedString)
            if len(list_items) > 0:
                list_item = list_items[0]

                row = self.lstTargetFields.row(list_item)

                rem_item = self.lstTargetFields.takeItem(row)
                del rem_item

                #Delete translator if already defined for the given column
                self._delete_translator(f)

    def loadGeomCols(self, table):
        #Load geometry columns based on the selected table 
        self.geomcols = table_column_names(table, True, True)
        self.geomClm.clear()
        self.geomClm.addItems(self.geomcols)
                
    def loadTables(self, type):
        #Load textual or spatial tables
        self.lstDestTables.clear()
        tables = None

        if type == "textual":
            tables = profile_user_tables(self.curr_profile, False, True)
            
        elif type == "spatial":
            tables = profile_spatial_tables(self.curr_profile)

        dest_tables = mapfile_section('imports')
        if tables is not None:
            for t in tables:
                if len(dest_tables) > 0:
                    if t not in dest_tables.values(): continue
                tabItem = QListWidgetItem(t, self.lstDestTables)
                tabItem.setCheckState(Qt.Unchecked)
                tabItem.setIcon(QIcon(":/plugins/stdm/images/icons/table.png"))
                self.lstDestTables.addItem(tabItem)
                
    def validateCurrentPage(self):
        #Validate the current page before proceeding to the next one
        validPage=True
        
        if not QFile.exists(unicode(self.field("srcFile"))):
            self.ErrorInfoMessage("The specified source file does not exist.")
            validPage = False
            
        else:
            if self.dataReader:
                self.dataReader.reset()
            self.dataReader = OGRReader(unicode(self.field("srcFile")))
            
            if not self.dataReader.isValid():
                self.ErrorInfoMessage("The source file could not be opened."
                                      "\nPlease check is the given file type "
                                      "is supported")
                validPage = False
                
        if self.currentId()==1:
            if self.destCheckedItem == None:                                                        
                self.ErrorInfoMessage("Please select the destination table.")
                validPage = False
                
        if self.currentId()==2:
            validPage = self.execImport()

        return validPage

    def setSourceFile(self):
        #Set the file path to the source file
        imageFilters = "Comma Separated Value (*.csv);;ESRI Shapefile (*.shp);;AutoCAD DXF (*.dxf)" 
        sourceFile = QFileDialog.getOpenFileName(self,"Select Source File",vectorFileDir(),imageFilters)
        if sourceFile != "":
            self.txtDataSource.setText(sourceFile) 
        
    def getSrcDestPairs(self):
        #Return the matched source and destination columns
        srcDest = {}
        for l in range(self.lstTargetFields.count()):
            if l < self.lstSrcFields.count():                
                srcItem = self.lstSrcFields.item(l)
                if srcItem.checkState() == Qt.Checked:
                    destItem = self.lstTargetFields.item(l)
                    srcDest[srcItem.text()] = destItem.text()
                    
        return srcDest

    def target_table_shortname(self, targetTab):
        return targetTab[targetTab.find('_')+1:]

    def validate_translator(self, vtmanager, targetTab):
        success = True
        translator_section = self.target_table_shortname(targetTab)+'-translators'
        translators = mapfile_section(translator_section)
        vtmtrans = [trans.lower().replace(' ','_') for trans in vtmanager._translators]
        for translator in translators.keys():
            if translator not in vtmtrans:
                self.ErrorInfoMessage("Please do translation for field `{}`".format(translator))
                success = False
                break
        return success

        
    def execImport(self):
        #Initiate the import process
        success = False
        matchCols = self.getSrcDestPairs()
        
        #Specify geometry column
        geom_column=None
        
        if self.field("typeSpatial"):
            geom_column = self.field("geomCol")
            
        # Ensure that user has selected at least one column if it is a
        # non-spatial table
        if len(matchCols) == 0:
            self.ErrorInfoMessage("Please select at least one source column.")
            return success

        value_translator_manager = self._trans_widget_mgr.translator_manager()

        success = self.validate_translator(value_translator_manager, self.targetTab)
        if not success:
            return success
               
        # try:
        if self.field("optOverwrite"):
            entity = self.curr_profile.entity_by_name(self.targetTab)
            dependencies = entity.dependencies()
            view_dep = dependencies['views']
            entity_dep = [e.name for e in entity.children()]
            entities_dep_str = ', '.join(entity_dep)
            views_dep_str = ', '.join(view_dep)

            if len(entity_dep) > 0 or len(view_dep) > 0:
                del_msg = QApplication.translate(
                    'ImportData',
                    "Overwriting existing records will permanently \n"
                    "remove records from other tables linked to the \n"
                    "records. The following tables will be affected."
                    "\n{}\n{}"
                    "\nClick Yes to proceed importing or No to cancel.".
                        format(entities_dep_str, views_dep_str)
                )
                del_result = QMessageBox.critical(
                    self,
                    QApplication.translate(
                        "ImportData",
                        "Overwrite Import Data Warning"
                    ),
                    del_msg,
                    QMessageBox.Yes | QMessageBox.No
                )

                if del_result == QMessageBox.Yes:
                    self.dataReader.featToDb(
                        self.targetTab, matchCols, False, self, geom_column,
                        translator_manager=value_translator_manager
                    )
                    # Update directory info in the registry
                    setVectorFileDir(self.field("srcFile"))

                    self.InfoMessage(
                        "All features have been imported successfully!"
                    )
                    success = True

                else:
                    success = False
        else:
            self.dataReader.featToDb(
                self.targetTab, matchCols, True, self, geom_column,
                translator_manager=value_translator_manager
            )
            self.InfoMessage(
                "All features have been imported successfully!"
            )
            #Update directory info in the registry
            setVectorFileDir(self.field("srcFile"))
            success = True
        # except:
        #     self.ErrorInfoMessage(unicode(sys.exc_info()[1]))

        return success

    def _clear_dest_table_selections(self, exclude=None):
        #Clears checked items in destination table list view
        if exclude is None:
            exclude = []

        for i in range(self.lstDestTables.count()):
            item = self.lstDestTables.item(i)
            if item.checkState() == Qt.Checked and not item.text() in exclude:
                item.setCheckState(Qt.Unchecked)
        
    def destSelectChanged(self, item):
        """
        Handler when a list widget item is clicked,
        clears previous selections
        """
        if not self.destCheckedItem is None:
            if item.checkState() == Qt.Checked:
                self.destCheckedItem.setCheckState(Qt.Unchecked) 
            else:
                self.destCheckedItem = None 
              
        if item.checkState() == Qt.Checked:
            self.destCheckedItem = item

            #Ensure other selected items have been cleared
            self._clear_dest_table_selections(exclude=[item.text()])

            #Load geometry columns if selection is a spatial table
            if self.field("typeSpatial"):
                self.loadGeomCols(item.text())
                
    def syncRowSelection(self, srcList, destList):
        """
        Sync the selection of an srcList item to the corresponding one in
        the destination column list.
        """
        if (srcList.currentRow() + 1) <= destList.count():
            destList.setCurrentRow(srcList.currentRow())
            
    def sourceRowChanged(self):
        #Slot when the source list's current row changes
        self.syncRowSelection(self.lstSrcFields,self.lstTargetFields)
        
    def destRowChanged(self):
        #Slot when the destination list's current row changes
        self.syncRowSelection(self.lstTargetFields, self.lstSrcFields)
                
    def itemUp(self, listWidget):
        #Moves the selected item in the list widget one level up
        curIndex = listWidget.currentRow()
        curItem = listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex - 1, curItem)
        listWidget.setCurrentRow(curIndex - 1)
        
    def itemDown(self, listWidget):
        #Moves the selected item in the list widget one level down
        curIndex=listWidget.currentRow()
        curItem=listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex + 1,curItem)
        listWidget.setCurrentRow(curIndex + 1)
        
    def checkAllItems(self, listWidget, state):
        #Checks all items in the list widget
        for l in range(listWidget.count()):
            item=listWidget.item(l)
            if state:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
                
    def checkSrcItems(self):
        #Slot for checking all source table columns
        self.checkAllItems(self.lstSrcFields, True)
        
    def uncheckSrcItems(self):
        #Slot for unchecking all source table columns
        self.checkAllItems(self.lstSrcFields, False)
        
    def srcItemUp(self):
        #Slot for moving source list item up
        self.itemUp(self.lstSrcFields)
        
    def srcItemDown(self):
        #Slot for moving source list item down
        self.itemDown(self.lstSrcFields)
    
    def targetItemUp(self):
        #Slot for moving target item up
        self.itemUp(self.lstTargetFields)
        
    def targetItemDown(self):
        #Slot for moving target item down
        self.itemDown(self.lstTargetFields)
         
    def keyPressEvent(self,e):
        """
        Override method for preventing the dialog from
        closing itself when the escape key is hit
        """
        if e.key() == Qt.Key_Escape:
            pass
        
    def InfoMessage(self, message):
        #Information message box        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()
                  
    def ErrorInfoMessage(self, message):
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()
