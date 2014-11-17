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

from PyQt4.QtGui import *
from PyQt4.QtCore import (
                          Qt,
                          QFile,
                          SIGNAL
                          )

from stdm.utils import *
import resources_rc
from stdm.data import (
                       table_column_names,
                       pg_tables,
                       spatial_tables
                       )
from stdm.data.importexport import (
                                    OGRReader,
                                    vectorFileDir,
                                    setVectorFileDir
                                    )

from .ui_import_data import Ui_frmImport

class ImportData(QWizard,Ui_frmImport):
    def __init__(self,parent=None):
        QWizard.__init__(self,parent)
        self.setupUi(self) 
                
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
         
        #Data Reader
        self.dataReader=None    
         
        #Init
        self.registerFields()
        
        #Geometry columns
        self.geomcols=[]
        
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
            
    def assignCols(self):
        #Load source and target columns respectively
        srcCols=self.dataReader.getFields()
        
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
            if colIndex!=-1:
                targetCols.remove(gc)
                
        self.lstTargetFields.addItems(targetCols)
                
    def loadGeomCols(self,table):
        #Load geometry columns based on the selected table 
        self.geomcols = table_column_names(table,True)
        self.geomClm.clear()
        self.geomClm.addItems(self.geomcols)
                
    def loadTables(self,type):
        #Load textual or spatial tables
        self.lstDestTables.clear()
        
        if type=="textual":
            tables = pg_tables(excludeLookups=False)
            
        elif type=="spatial":
            tables = spatial_tables(excludeViews=True)
                                
        for t in tables:            
            tabItem = QListWidgetItem(t,self.lstDestTables)
            tabItem.setCheckState(Qt.Unchecked)
            tabItem.setIcon(QIcon(":/plugins/stdm/images/icons/table.png"))
            self.lstDestTables.addItem(tabItem)            
                
    def validateCurrentPage(self):
        #Validate the current page before proceeding to the next one
        validPage=True
        
        if not QFile.exists(str(self.field("srcFile"))):
            self.ErrorInfoMessage("The specified source file does not exist.")
            validPage = False
            
        else:
            if self.dataReader:
                self.dataReader.reset()
            self.dataReader = OGRReader(str(self.field("srcFile")))
            
            if not self.dataReader.isValid():
                self.ErrorInfoMessage("The source file could not be opened.\nPlease check for the supported file types.")
                validPage=False
                
        if self.currentId()==1:
            if self.destCheckedItem == None:                                                        
                self.ErrorInfoMessage("Please select the destination table.")
                validPage=False
                
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
        srcDest={}
        for l in range(self.lstTargetFields.count()):
            if l < self.lstSrcFields.count():                
                srcItem=self.lstSrcFields.item(l)
                if srcItem.checkState()== Qt.Checked:                
                    destItem=self.lstTargetFields.item(l)
                    srcDest[srcItem.text()] = destItem.text()
                    
        return srcDest
        
    def execImport(self):
        #Initiate the import process
        success = False
        matchCols = self.getSrcDestPairs()
        
        #Specify geometry column
        geomColumn=None
        
        if self.field("typeSpatial"):
            geomColumn = str(self.field("geomCol"))  
            
        #Ensure that user has selected at least one column if it is a non-spatial table
        if len(matchCols) == 0:
            self.ErrorInfoMessage("Please select at least one source column.")
            return success 
               
        try:
            if self.field("optOverwrite"):
                self.dataReader.featToDb(self.targetTab,matchCols,False,self,geomColumn)
            else:                
                self.dataReader.featToDb(self.targetTab,matchCols,True,self,geomColumn)  
            
            self.InfoMessage("All features have been imported successfully!")
            
            #Update directory info in the registry
            setVectorFileDir(str(self.field("srcFile")))
            
            success = True 
                     
        except:
            self.ErrorInfoMessage(str(sys.exc_info()[1]))
            
        return success
        
    def destSelectChanged(self,item):
        '''
        Handler when a list widget item is clicked,
        clears previous selections
        '''  
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
                
    def syncRowSelection(self,srcList,destList):
        #Sync the selection of an srcList item to the corresponding one in destList
        if (srcList.currentRow() + 1) <=destList.count():
            destList.setCurrentRow(srcList.currentRow())
            
    def sourceRowChanged(self):
        #Slot when the source list's current row changes
        self.syncRowSelection(self.lstSrcFields,self.lstTargetFields)
        
    def destRowChanged(self):
        #Slot when the destination list's current row changes
        self.syncRowSelection(self.lstTargetFields, self.lstSrcFields)
                
    def itemUp(self,listWidget):
        #Moves the selected item in the list widget one level up
        curIndex=listWidget.currentRow()
        curItem=listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex-1,curItem)
        listWidget.setCurrentRow(curIndex-1)
        
    def itemDown(self,listWidget):
        #Moves the selected item in the list widget one level down
        curIndex=listWidget.currentRow()
        curItem=listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex+1,curItem)
        listWidget.setCurrentRow(curIndex+1)
        
    def checkAllItems(self,listWidget,state):
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
        msg.setText(Message)
        msg.exec_()  

   

