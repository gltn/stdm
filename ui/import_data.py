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

        bg_color = "QListWidget::item:selected{background-color: rgba(0, 170, 255, 255)};"    
        self.lstTargetFields.setStyleSheet(bg_color)
        self.lstSrcFields.setStyleSheet(bg_color)

        #Data Reader
        self.dataReader = None
         
        #Init
        self.registerFields()
        
        #Geometry columns
        self.geomcols = []

        self._trans_widget_mgr = TranslatorWidgetManager(self)

        #Initialize value translators from definitions
        self._init_translators()

    def text_type_clicked(self):
        if self.rbTextType.isChecked():
            if self.txtDataSource.text() != '':
                self.button(QWizard.NextButton).setEnabled(True)

    def sptype_clicked(self):
        if self.rbSpType.isChecked():
            if self.txtDataSource.text() != '':
                self.button(QWizard.NextButton).setEnabled(True)

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
                source_names = [src_field for src_field, table in srclookups.items() if src_field == dest_column]
                if len(source_names) == 0: continue

                src_column = source_names[0]
                #src_column = self._get_src_column(lookup_table, srclookups)
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

        
        if self.lstSrcFields.count() > 0:
            item = self.lstSrcFields.item(0)
            self.lstSrcFields.setCurrentItem(item)
        self._enable_disable_trans_tools()


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
                #self.toggleKoboOptions(False)
                #self.toggleSupportDoc(False)
                
            elif self.field("typeSpatial"):
                self.loadTables("spatial")
                self.geomClm.setEnabled(True)
                #self.toggleKoboOptions(False)
                #self.toggleSupportDoc(False)

            #elif self.field("koboMedia"):
                #self.toggleKoboOptions(True)
                #self.toggleSupportDoc(False)
                
            #elif self.field("supportdoc"):
                #self.toggleKoboSettings(True)
                ##self.toggleSupportDoc(True)
                #self.toggleMediaFolders(False)

        if pageid == 2:
            self.lstSrcFields.clear()
            self.lstTargetFields.clear()
            self.assignCols()
            self.auto_load_translators()
            self._enable_disable_trans_tools()

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
        
        update_geom_column = False
        if self.field("typeSpatial"):
            geom_column = self.field("geomCol")
            update_geom_column = True
            
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
                update_geom_column_only=update_geom_column, translator_manager=value_translator_manager
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
