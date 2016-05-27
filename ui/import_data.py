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
import sys
import copy

from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    QFile,
    SIGNAL,
    QSignalMapper
)

from stdm.utils import *
from stdm.utils.util import getIndex
from stdm.data.database import alchemy_table_relationships
from stdm.data.pg_utils import (
    table_column_names,
    pg_tables,
    spatial_tables
)
from stdm.data.importexport import (
    vectorFileDir,
    setVectorFileDir
)
from stdm.data.importexport.value_translators import ValueTranslatorManager
from stdm.data.importexport.reader import OGRReader
from .importexport import (
    ValueTranslatorConfig,
    TranslatorWidgetManager
)
from stdm.settings import current_profile
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
        self.chk_virtual.toggled.connect(self._on_load_virtual_fields)
         
        #Data Reader
        self.dataReader = None
         
        #Init
        self.registerFields()
        
        #Geometry columns
        self.geomcols = []

        #Initialize value translators from definitions
        self._init_translators()

        #self._set_target_fields_stylesheet()

        #Disable virtual fields
        self.chk_virtual.setVisible(False)

    def _init_translators(self):
        translator_menu = QMenu(self)

        self._trans_widget_mgr = TranslatorWidgetManager(self)
        self._trans_signal_mapper = QSignalMapper(self)

        for trans_name, config in ValueTranslatorConfig.translators.iteritems():
            trans_action = QAction(trans_name + "...", translator_menu)

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

                #Safety precaution
                if trans_config is None: return

                trans_dlg = trans_config.create(self, self._source_columns(),
                                                self.targetTab, dest_column, src_column)

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
                
            elif self.field("typeSpatial"):
                self.loadTables("spatial")
                self.geomClm.setEnabled(True)
                
        if pageid == 2:
            self.lstSrcFields.clear()
            self.lstTargetFields.clear()
            self.assignCols()
            self._enable_disable_trans_tools()

    def _source_columns(self):
        return self.dataReader.getFields()

    def assignCols(self):
        #Load source and target columns respectively
        srcCols = self._source_columns()
        
        for c in srcCols:
            srcItem = QListWidgetItem(c,self.lstSrcFields)
            srcItem.setCheckState(Qt.Unchecked)
            srcItem.setIcon(QIcon(":/plugins/stdm/images/icons/column.png"))
            self.lstSrcFields.addItem(srcItem)
            
        #Destination Columns
        tabIndex = int(self.field("tabIndex"))
        self.targetTab = self.destCheckedItem.text()
        targetCols = table_column_names(self.targetTab)   
            
        #Remove geometry columns in the target columns list
        for gc in self.geomcols:            
            colIndex = getIndex(targetCols,gc)
            if colIndex != -1:
                targetCols.remove(gc)
                
        self._add_target_table_columns(targetCols)

    def _add_target_table_columns(self, items, style=False):
        for item in items:
            list_item = QListWidgetItem(item)

            if style:
                color = QColor(0, 128, 255)
                list_item.setTextColor(color)

            self.lstTargetFields.addItem(list_item)
                
    def _on_load_virtual_fields(self, state):
        """
        Load/unload relationships in the list of destination table columns."
        """
        relationship_names = alchemy_table_relationships(self.targetTab)

        if state:
            if len(relationship_names) == 0:
                msg = QApplication.translate("ImportData",
                    "There are no virtual fields in the specified table.")
                QMessageBox.warning(self, QApplication.translate("ImportData","Import Data"),
                                    msg)
                self.chk_virtual.setChecked(False)

            self._add_target_table_columns(relationship_names, True)

        else:
            self._remove_destination_table_fields(relationship_names)

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

    def loadGeomCols(self,table):
        #Load geometry columns based on the selected table 
        self.geomcols = table_column_names(table, True)
        self.geomClm.clear()
        self.geomClm.addItems(self.geomcols)
                
    def loadTables(self,type):
        #Load textual or spatial tables
        self.lstDestTables.clear()
        tables = None
        if type == "textual":
            tables = profile_user_tables(self.curr_profile)
            
        elif type == "spatial":
            tables = profile_spatial_tables(self.curr_profile)
        if tables is not None:
            for t in tables:
                tabItem = QListWidgetItem(t,self.lstDestTables)
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
                                      "it \nPlease check for the supported file types.")
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
        
    def execImport(self):
        #Initiate the import process
        success = False
        matchCols = self.getSrcDestPairs()
        
        #Specify geometry column
        geom_column=None
        
        if self.field("typeSpatial"):
            geom_column = self.field("geomCol")
            
        #Ensure that user has selected at least one column if it is a non-spatial table
        if len(matchCols) == 0:
            self.ErrorInfoMessage("Please select at least one source column.")
            return success

        value_translator_manager = self._trans_widget_mgr.translator_manager()
               
        #try:
        if self.field("optOverwrite"):
            self.dataReader.featToDb(self.targetTab, matchCols, False, self, geom_column,
                                     translator_manager=value_translator_manager)
        else:
            self.dataReader.featToDb(self.targetTab, matchCols, True, self, geom_column,
                                     translator_manager=value_translator_manager)

        self.InfoMessage("All features have been imported successfully!")

        #Update directory info in the registry
        setVectorFileDir(self.field("srcFile"))

        success = True
        # except:
        #     self.ErrorInfoMessage(unicode(sys.exc_info()[1]))

        return success
        
    def destSelectChanged(self, item):
        """
        Handler when a list widget item is clicked,
        clears previous selections
        """
        if self.destCheckedItem != None:
            if item.checkState() == Qt.Checked:
                self.destCheckedItem.setCheckState(Qt.Unchecked) 
            else:
                self.destCheckedItem = None 
              
        if item.checkState() == Qt.Checked:
            self.destCheckedItem = item
            
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

   

