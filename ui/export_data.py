"""
/***************************************************************************
Name                 : Export Data from STDM
Description          : LEGACY CODE, NEEDS TO BE UPDATED.
                       Export data to selected OGR formats
Date                 : 24/March/12
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
from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    SIGNAL
)

import sqlalchemy

from stdm.utils import *
from stdm.utils.util import getIndex
from stdm.ui.reports import SqlHighlighter
from stdm.data.pg_utils import (
    process_report_filter,
    table_column_names,
    unique_column_values,
    pg_tables
)
from stdm.data.importexport.writer import OGRWriter

from stdm.data.importexport import (
    vectorFileDir,
    setVectorFileDir
)
from stdm.settings import current_profile
from stdm.utils.util import (
    profile_user_tables
)
from .ui_export_data import Ui_frmExportWizard 

class ExportData(QWizard,Ui_frmExportWizard):
    def __init__(self,parent=None):
        QWizard.__init__(self,parent) 
        self.setupUi(self)  
        self.curr_profile = current_profile()
        #Event Handlers    
        self.btnDestFile.clicked.connect(self.setDestFile)
        self.lstSrcTab.itemSelectionChanged.connect(self.srcSelectChanged)
        self.btnUniqueVals.clicked.connect(self.colUniqueValues)
        
        #Query Builder signals
        self.lstQueryCols.itemDoubleClicked.connect(self.filter_insertField)
        self.lstUniqueVals.itemDoubleClicked.connect(self.filter_insertField)
        self.btnOpEq.clicked.connect(self.filter_insertEq)
        self.btnOpNotEq.clicked.connect(self.filter_insertNotEq)
        self.btnOpLike.clicked.connect(self.filter_insertLike)
        self.btnOpGreater.clicked.connect(self.filter_greaterThan)
        self.btnOpGreaterEq.clicked.connect(self.filter_greaterEq)
        self.btnOpAnd.clicked.connect(self.filter_insertAnd)
        self.btnOpLess.clicked.connect(self.filter_insertLess)
        self.btnOpLessEq.clicked.connect(self.filter_insertLessEq)
        self.btnOpOr.clicked.connect(self.filter_insertOR)
        self.btnClearQuery.clicked.connect(self.filter_clearQuery)
        self.btnQueryVerify.clicked.connect(self.filter_verifyQuery)
        
        #Init controls
        self.initControls()
        
        #Register fields
        self.registerFields() 
        
    def initControls(self):
        #Initialize controls
        self.cboSpatialCols_2.setEnabled(False)
        self.gpQBuilder.setChecked(False)
        
        #Query Builder section
        self.txtWhereQuery.setWordWrapMode(QTextOption.WordWrap)
        
        #Custom SQL highlighter
        sqlHighlighter = SqlHighlighter(self.txtWhereQuery)
        
    def registerFields(self):
        #Destination file name and format
        pgDestination = self.page(0)
        pgDestination.registerField("destFile*",self.txtExportPath)
        
        #Export table options page
        pgExportTab = self.page(1)
        pgExportTab.registerField("srcTabIndex*",self.lstSrcTab)
        pgExportTab.registerField("geomCol",self.cboSpatialCols_2,"currentText",SIGNAL("currentIndexChanged(int)"))
        
    def initializePage(self,int):
        #Re-implementation of wizard page initialization
        if int==1:            
            #Load tables            
            self.loadSourceTables() 
            
        if int==2:
            #Load columns for query builder
            selTableIndex = self.field("srcTabIndex")
            self.srcTab = str(self.lstSrcTab.item(selTableIndex).text())
            self.lstQueryCols.clear()
            self.lstQueryCols.addItems(self.allCols) 
            
    def validateCurrentPage(self):
        #Validate the current page before proceeding to the next one
        validPage = True
        
        if self.currentId() == 1:
            if len(self.lstSrcTab.selectedItems()) == 0:
                self.ErrorInfoMessage("Please select a table whose contents are to be exported.")
                validPage=False
                
            else:                
                if len(self.selectedColumns())==0:                                                                
                    self.ErrorInfoMessage("Please select at least one textual column whose values are to be exported.")
                    validPage=False
                    
            #Set Geometry column
            geomCol = str(self.field("geomCol"))
            self.geomColumn = "" if geomCol == "NULL" else geomCol 
                  
        if self.currentId()==2:
            validPage = self.execExport() 
                   
        return validPage     
    
    def selectedColumns(self):
        #Get the selected columns to be imported
        tabCols=[]
        
        for c in range(self.lstSrcCols_2.count()):                 
            srcCol=self.lstSrcCols_2.item(c)
            
            if srcCol.checkState() == Qt.Checked:                              
                tabCols.append(srcCol.text())    
                          
        return tabCols
            
    def loadSourceTables(self):
        #Load all STDM tables
        self.lstSrcTab.clear()
        # tables = pg_tables()
        tables = profile_user_tables(
            self.curr_profile, True, True
        )
        for t in tables.keys():
            tabItem = QListWidgetItem(t,self.lstSrcTab)
            tabItem.setIcon(QIcon(":/plugins/stdm/images/icons/table.png"))
            self.lstSrcTab.addItem(tabItem)
        
    def setDestFile(self):
        #Set the file path to the destination file
        if self.rbShp.isChecked():
            ogrFilter = "ESRI Shapefile (*.shp)"
        elif self.rbCSV.isChecked():
            ogrFilter = "Comma Separated Values (*.csv)"
        elif self.rbMapInfo.isChecked():
            ogrFilter = "MapInfo File (*.tab)"
        elif self.rbGPX.isChecked():
            ogrFilter = "GPX (*.gpx)"
        elif self.rbDXF.isChecked():
            ogrFilter = "DXF (*.dxf)"     
                 
        destFile = QFileDialog.getSaveFileName(
            self,"Select Output File",vectorFileDir(),ogrFilter
        )
        
        if destFile != "":
            self.txtExportPath.setText(destFile) 
        
    def srcSelectChanged(self):
        '''
        Handler when a source table item is clicked,
        clears previous selections
        '''    
        selTabs=self.lstSrcTab.selectedItems()
        
        if len(selTabs) > 0:
            selTab=selTabs[0]
            
            #Load columns for the selected table
            self.loadColumns(selTab.text())
                
    def loadColumns(self,table):
        #Load textual and spatial (if available) columns
        #Get spatial columns first        
        spColumns = table_column_names(table,True)
        self.cboSpatialCols_2.clear()
        self.cboSpatialCols_2.addItems(spColumns)
        
        #Textual Columns
        self.lstSrcCols_2.clear()
        self.allCols = table_column_names(table)
        
        for sc in spColumns:            
            colIndex = getIndex(self.allCols,sc)
            if colIndex != -1:
                self.allCols.remove(sc)    
                                        
        for col in self.allCols:            
            tabItem = QListWidgetItem(col,self.lstSrcCols_2)
            tabItem.setCheckState(Qt.Unchecked)
            tabItem.setIcon(QIcon(":/plugins/stdm/images/icons/column.png"))
            self.lstSrcCols_2.addItem(tabItem)   
               
        if len(spColumns) > 0:
            self.cboSpatialCols_2.setEnabled(True)
        
    def colUniqueValues(self):
        #Slot for getting unique values for the selected column
        self.lstUniqueVals.clear()
        selCols = self.lstQueryCols.selectedItems()
        
        if len(selCols) > 0:
            selCol = selCols[0]
            colName = selCol.text()
            uniqVals = unique_column_values(self.srcTab,colName) 
            self.lstUniqueVals.addItems(uniqVals)
            self.lstUniqueVals.sortItems() 
            
    def execExport(self):
        #Initiate the export process
        succeed = False
        
        targetFile = str(self.field("destFile"))
        writer = OGRWriter(targetFile)
        resultSet = self.filter_buildQuery()
        
        if resultSet is None:
            return succeed
        
        if resultSet.rowcount == 0:
            self.ErrorInfoMessage("There are no records to export")
            return succeed
        
        try:                                  
            writer.db2Feat(self,self.srcTab,resultSet,self.selectedColumns(),self.geomColumn)
            self.InfoMessage("Features in '%s' have been successfully exported!"%(self.srcTab))  
            
            #Update directory info in the registry
            setVectorFileDir(targetFile)
            
            succeed=True    
                  
        except:
            self.ErrorInfoMessage(str(sys.exc_info()[1]))  
        
        return succeed
            
    def filter_clearQuery(self):        
        #Deletes all the text in the SQL text editor
        self.txtWhereQuery.clear()
        
    def filter_verifyQuery(self):
        #Verify the query expression    
        if len(self.txtWhereQuery.toPlainText()) == 0:
            self.ErrorInfoMessage("No filter has been defined.")
            
        else:
            results = self.filter_buildQuery()
            
            if results != None:            
                rLen = results.rowcount
                msg = "The SQL statement was successfully verified.\n" + str(rLen) + " record(s) returned."
                self.InfoMessage(msg)
        
    def filter_buildQuery(self):
        #Build query set and return results 
        queryCols = self.selectedColumns() 
        
        if self.geomColumn != "":
            queryCols.append("ST_AsText(%s)"%(self.geomColumn)) 
            
                 
        columnList = ",".join(queryCols)
        whereStmnt = self.txtWhereQuery.toPlainText()         
        sortStmnt=''        
        results=None 
            
        try:        
            results = process_report_filter(self.srcTab,columnList,whereStmnt,sortStmnt)      
              
        except sqlalchemy.exc.DataError,e:
            if e is None:
                errMessage = "Database Error Message - NOT AVAILABLE"
            else:
                errMessage = e.message
                
            self.ErrorInfoMessage("The SQL statement is invalid!\n" + errMessage)  
            
        return results    
        
    def filter_insertField(self,lstItem):
        '''
        Inserts the text of the clicked field item into the
        SQL parser text editor.
        '''
        self.txtWhereQuery.insertPlainText(lstItem.text())    
    
    def filter_insertEq(self):
        #Insert Equal operator
        self.txtWhereQuery.insertPlainText(" = ")
     
    def filter_insertNotEq(self):
        #Insert Not Equal to
        self.txtWhereQuery.insertPlainText(" <> ")
    
    def filter_insertLike(self):
        #Insert LIKE operator
        self.txtWhereQuery.insertPlainText(" LIKE ")
    
    def filter_greaterThan(self):
        #Insert greater than
        self.txtWhereQuery.insertPlainText(" > ")
    
    def filter_greaterEq(self):
        #Insert Greater than or equal to
        self.txtWhereQuery.insertPlainText(" >= ")
    
    def filter_insertAnd(self):
        #Insert AND        
        self.txtWhereQuery.insertPlainText(" AND ")
    
    def filter_insertLess(self):
        self.txtWhereQuery.insertPlainText(" < ")
    
    def filter_insertLessEq(self):
        self.txtWhereQuery.insertPlainText(" <= ")
    
    def filter_insertOR(self):
        self.txtWhereQuery.insertPlainText(" OR ")            
            
    def keyPressEvent(self,e):
        '''
        Override method for preventing the dialog from
        closing itself when the escape key is hit
        '''
        if e.key() == Qt.Key_Escape:
            pass 
        
    def InfoMessage(self,message):
        #Information message box        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()
                  
    def ErrorInfoMessage(self,Message): 
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Data Export Error')
        msg.setText(Message)
        msg.exec_()  

   

