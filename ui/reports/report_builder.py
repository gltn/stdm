"""
/***************************************************************************
Name                 : STDM Report Builder - LEGACY CODE, NEEDS UPDATE
Description          : Report Builder Dialog
Date                 : 07/September/11 
copyright            : (C) 2011 by John Gitau
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sqlalchemy

from stdm.utils import *
from stdm.data.reports import (
                               STDMReport,
                               STDMGenerator,
                               ReportElements, 
                                STDMReportConfig, 
                                ReportSerializer,
                                DbField, 
                                FieldConfig, 
                                GroupSettings, 
                                SortDir, 
                                FieldSort
                                )
from stdm.data import (
                       table_column_names,
                       unique_column_values,
                       pg_tables,
                       pg_views,
                       process_report_filter
                       )
from stdm.ui.customcontrols import TableComboBox
'''
from stdm.workspace.defaultSetting.config import dbTableConfig
from stdm.workspace.defaultSetting.map_query import CertificateMap
'''
 
from .report_title_base import TitleBase
from .field_base import FieldBase
from .report_title import Title
from .field_names import FieldNames
from .groups import Groups
from .report_layout import ReportLayout
from .highlighter import SqlHighlighter

from qgis.core import *
from qgis.gui import *

from .ui_rpt_builder import Ui_ReportBuilder

class ReportBuilder(QDialog,Ui_ReportBuilder):   
    def __init__(self,config,parent = None): 
        QDialog.__init__(self,parent)
        
        self.setupUi(self)
        
        #Disable supporting tabs
        self.enableSupportingTabs(False)
        
        #Dynamic class for placing report elements
        self.rptElements = ReportElements()
        
        #Get instance of config object    
        self.config = config
        self.progressDlgDlg = QProgressDialog(self)
        
        #Event handlers
        #Fields Section
        self.btnRptCancel.clicked.connect(self.close)
        self.btnSave.clicked.connect(self.saveReport)
        self.btnLoad.clicked.connect(self.loadReport)
        self.comboBox.currentIndexChanged[int].connect(self.tabChanged)
        self.btnAddField.clicked.connect(self.addReportFields)
        self.btnAddAllFields.clicked.connect(self.addAllFields)
        self.btnRemField.clicked.connect(self.remReportFields)
        self.btnRemAllFields.clicked.connect(self.remAllFields)
        self.btnUniqVals.clicked.connect(self.fields_getUniqueVals)
        
        #Filter Section
        self.lstFields.itemDoubleClicked.connect(self.filter_insertRptFields)
        self.lstUniqVal.itemDoubleClicked.connect(self.filter_insertRptFields)
        self.btnOpEqual.clicked.connect(self.filter_insertEq)
        self.btnOpNotEqual.clicked.connect(self.filter_insertNotEq)
        self.btnOpLike.clicked.connect(self.filter_insertLike)
        self.btnOpGreater.clicked.connect(self.filter_greaterThan)
        self.btnOpGreaterEq.clicked.connect(self.filter_greaterEq)
        self.btnOpAnd.clicked.connect(self.filter_insertAnd)
        self.btnOpLess.clicked.connect(self.filter_insertLess)
        self.btnOpLess_2.clicked.connect(self.filter_insertLessEq)
        self.btnOpOr.clicked.connect(self.filter_insertOR)
        self.btnSQLClr.clicked.connect(self.filter_ClearText)
        self.btnSQLVer.clicked.connect(self.filter_verifyQuery)    
        self.btnGenRpt.clicked.connect(self.generateReport)  
        
        #Display Section
        #self.lblTitleClr.clicked.connect(self.display_titleColor)
        self.trRptSettings.itemSelectionChanged.connect(self.display_treeViewSelection)
        
        #Grouping section
        self.btnAddGpField.clicked.connect(self.grouping_addField)
        self.btnRemGpField.clicked.connect(self.grouping_removeField)
        
        #Show on Map
        self.btnMap.clicked.connect(self.map_query_fromFilter)
        #Initialize dialog with table names
        self.initRptDialog()   
        
        #self.btnSQLApply.setVisible(False) 
    
    def initRptDialog(self):
        #Initialize the dialog with table names
        self.tabNames={}    
        tabList=self.config.items("ReportFields")
        
        for names in tabList:
            tableName = names[0]
            displayName = names[1]
            self.tabNames[tableName] = displayName
            self.comboBox.addItem(displayName,tableName)
        
        self.initStackWidgets()
        
        #Sorting
        self.tbSortFields.verticalHeader().setVisible(False) 
        self.tbSortFields.setAlternatingRowColors(True)
        self.tbSortFields.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        #Fields
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listWidget_2.setSelectionMode(QAbstractItemView.MultiSelection)
        
        #General
        self.btnGenRpt.setEnabled(False)
        self.btnSave.setEnabled(False)
        
        #Display
        self.trRptSettings.expandAll()
        
        #Filter
        self.txtSqlParser.setWordWrapMode(QTextOption.WordWrap)
        sqlHL = SqlHighlighter(self.txtSqlParser)
        
        #Grouping
        #Hide inapplicable columns
        self.tbGroupFields.verticalHeader().setVisible(False) 
        self.tbGroupFields.setAlternatingRowColors(True)
        self.tbGroupFields.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.initVars()
    
    def initVars(self):
        #Initialize data variables   
        self._sortOrder=0    
    
    def initStackWidgets(self):
        #Instantiate new report display widgets
        titleWidgets=["Title"]
        for t in titleWidgets:
            stWidg = Title(t)   
            self.stackedWidget.addWidget(stWidg)  
            
        #Add Field Names Widget
        fnWidg = FieldNames("Field Names")
        self.stackedWidget.addWidget(fnWidg)
        
        #Add Layout Tree Node (Under Elements parent node)
        elNode=self.trRptSettings.findItems("Elements",Qt.MatchExactly,0)[0]
        layoutNode = QTreeWidgetItem(["Layout"])
        elNode.addChild(layoutNode)
        
        #Add Layout Widget
        layoutWidg = ReportLayout("Layout")
        self.stackedWidget.addWidget(layoutWidg)
        
        #Select the first item in the tree view    
        titleNode=elNode.child(0)
        titleNode.setSelected(True)

    def resetControls(self):
        #Reset widgets
        self.listWidget_2.clear()
        self.listWidget.clear()
        self.enableSupportingTabs(False)
        self.txtSqlParser.clear()
        self.lstUniqVal.clear()
        self.lstFields.clear()
        self.grouping_cleanUpFields()
        self.lstRptFields.clear()  
        self.display_updateReportFields() 
        self.sorting_updateReportFields()  
        self.initVars()  
    
    def tabChanged(self,itemIndex):
        #Handler when the table names' combo box items changes    
        self.tabFields=[]
        self.rptFields=[]
        self.resetControls()
        self.loadTabFields(itemIndex)
        self.selectAvailFieldItem()
    
    def enableSupportingTabs(self,status):
        '''
        Enable/Disable other tabs only when the report fields
        have been defined by the user
        '''
        self.tab_2.setEnabled(status)
        self.tab_3.setEnabled(status)
        self.tab_4.setEnabled(status)
        self.tab_5.setEnabled(status)
        self.btnGenRpt.setEnabled(status)
        self.btnSave.setEnabled(status)
    
    def loadTabFields(self,comboItemIndex):
        #Load the associated fields from  specified table name 
        self.tabName = str(self.comboBox.itemData(comboItemIndex))
        self.tabFields = table_column_names(self.tabName)
        self.listWidget.addItems(self.tabFields) 
        
        #Set table name in the Fields Query Builder
        self.lblSqlEntity.setText("Select * FROM " + self.tabName + " WHERE:")   
    
    def addReportFields(self,selectAll=False):
        # get selected fields and add to the report collection
        selFields=[]
        if selectAll:
            for i in range(self.listWidget.count()):
                lstItem=self.listWidget.item(i)   
                selFields.append(lstItem.text())   
        else:        
            selItems=self.listWidget.selectedItems()
            for selItem in selItems:
                selFields.append(selItem.text())
        self.updateSelectedReportFields(selFields)

    def updateSelectedReportFields(self,rptFields):
        #Updates the user defined report fields
        for r in rptFields:
            self.rptFields.append(r)
            self.tabFields.remove(r)            
        self.updateFieldViews()
    
    def remReportFields(self,selectAll=False):
        #Remove items from the report collection
        selFields=[]
        if selectAll:
            for i in range(self.listWidget_2.count()):
                lstItem=self.listWidget_2.item(i)   
                selFields.append(lstItem.text())   
        else:    
            selItems=self.listWidget_2.selectedItems()
            for selItem in selItems:
                selFields.append(selItem.text())
                
        for s in selFields:           
            self.rptFields.remove(s)
            self.tabFields.append(s)            
        
        self.updateFieldViews()
    
    def selectAvailFieldItem(self,index=0):
        #Select an item in available fields view
        if index==0:
            selItem=self.listWidget.item(0)
            self.listWidget.setCurrentItem(selItem)
        
    def loadRptFieldsWidgets(self):
        '''
        Populate report fields widgets defined in the supporting
        tabs
        '''
        self.reloadRptListWidgets(self.lstFields)
        self.reloadRptListWidgets(self.lstRptFields)
        self.grouping_cleanUpFields()  
        self.display_updateReportFields() 
        self.sorting_updateReportFields()
    
    def reloadRptListWidgets(self,lstwidgetobj):
        #clear and reload report fields widgets
        lstwidgetobj.clear()
        lstwidgetobj.addItems(self.rptFields)
  
    def addAllFields(self):
        #Handler when the add all fields button is clicked
        self.addReportFields(True)
    
    def remAllFields(self):
        #Handler when the remove all report fields button is clicked
        self.remReportFields(True)
  
    def updateFieldViews(self):
        #Update the available and report fields' widgets
        self.listWidget.clear()
        self.listWidget.addItems(self.tabFields)
        self.listWidget_2.clear()
        self.listWidget_2.addItems(self.rptFields)
        '''
        Check if the report fields have been defined
        and enable the supporting tabs
        '''
        if len(self.rptFields)>0:
            self.enableSupportingTabs(True)
            self.loadRptFieldsWidgets()
        else:
            self.enableSupportingTabs(False)        
        
    def fields_getUniqueVals(self):
        #Raised when the get unique values button is clicked
        selItems=self.lstFields.selectedItems()
        if len(selItems)>0:
            columnName = selItems[0].text()
            self.fields_loadUniqueVals(self.tabName, str(columnName))
        
    def fields_loadUniqueVals(self,tableName,columnName):
        #Get unique column values and load the list
        uniqueVals = unique_column_values(tableName,columnName)
        self.lstUniqVal.clear()
        self.lstUniqVal.addItems(uniqueVals)
        self.lstUniqVal.sortItems()    
    
    def filter_ClearText(self):
        #Deletes all the text in the text edit
        self.txtSqlParser.clear()
    
    def filter_insertRptFields(self,lstItem):
        '''
        Inserts the clicked report field item into the
        SQL parser text edit.
        '''
        self.txtSqlParser.insertPlainText(lstItem.text())    
    
    def filter_insertEq(self):
        #Insert Equal operator
        self.txtSqlParser.insertPlainText(" = ")
     
    def filter_insertNotEq(self):
        #Insert Not Equal to
        self.txtSqlParser.insertPlainText(" <> ")
    
    def filter_insertLike(self):
        #Insert LIKE operator
        self.txtSqlParser.insertPlainText(" LIKE ")
    
    def filter_greaterThan(self):
        #Insert greater than
        self.txtSqlParser.insertPlainText(" > ")
    
    def filter_greaterEq(self):
        #Insert Greater than or equal to
        self.txtSqlParser.insertPlainText(" >= ")
    
    def filter_insertAnd(self):
        #Insert AND
        #self.filter_AppendOpHTML("AND")    
        self.txtSqlParser.insertPlainText(" AND ")
    
    def filter_insertLess(self):
        self.txtSqlParser.insertPlainText(" < ")
    
    def filter_insertLessEq(self):
        self.txtSqlParser.insertPlainText(" <= ")
    
    def filter_insertOR(self):
        self.txtSqlParser.insertPlainText(" OR ")    
    
    def filter_buildQuery(self):
        #Build query set and return results
        columnList = ",".join(self.rptFields)
        filterStmnt = self.txtSqlParser.toPlainText()
        
        #Check if sorting has been defined
        stLen,stSQL = self.sorting_compileSort()
        
        #Check if grouping has been defined
        gpLen,gpQuery = self.grouping_orderQuery()
        sortStmnt=''
        if gpLen > 0:          
            sortStmnt = gpQuery
            if stLen>0:
                stSQL = stSQL.replace(" ORDER BY","")
                sortStmnt = sortStmnt+"," + stSQL
        else:        
            if stLen>0:
                sortStmnt = stSQL
                
        results=None  
        
        try:        
            results = process_report_filter(self.tabName,columnList,filterStmnt,sortStmnt)           
           
        except sqlalchemy.exc.ProgrammingError,sqlalchemy.exc.DataError:
            self.ErrorInfoMessage("The SQL statement is invalid!") 
        
        return results       
   
    def map_query_fromFilter(self):
        strQuery=self.txtSqlParser.toPlainText()
        unitArray=[]
        
        try:
            mpPartQry=self.tabName+"."+ dbTableConfig.getItem(self.tabName)+"=spatial_unit.identity"
            if strQuery!="":
                mpPartQry+=" AND "+self.tabName+"."+strQuery
            else:
                mpPartQry=mpPartQry
            mapUnits=self.stdmPgProv.procReportViewFilter(self.tabName,str(mpPartQry))            
            refLayer=CertificateMap(mapUnits)
        except:
            self.ErrorInfoMessage(str(sys.exc_info()[1]))
            return
                
    def filter_verifyQuery(self):
        #Verify the query expression    
        if len(self.txtSqlParser.toPlainText())==0:
            self.ErrorInfoMessage("No filter has been defined")
            
        else:
            results=self.filter_buildQuery()
            
            if results!=None:            
                resLen = results.rowcount
                msg = "The SQL statement was successfully verified.\n" + str(resLen) + " record(s) returned."
                self.InfoMessage(msg)
            
    def sorting_updateReportFields(self):
        #Update the fields available in the sorting section    
        sortItems=["Ascending","Descending","None"]
        
        #Important! Ensure only new values are added without overriding the existing rows
        row=self.tbSortFields.rowCount()
        
        for l in range(len(self.rptFields)):
            f=self.rptFields[l]
            item=self.sorting_getFieldItem(f)
            if item==None:            
                #Instantiate row widgets
                fieldItem = QTableWidgetItem()
                fieldItem.setText(f)
                
                sortWidg = TableComboBox(row)            
                sortWidg.addItems(sortItems)            
                sortWidg.setCurrentIndex(2)
                sortWidg.currentIndexChanged.connect(lambda:self.sorting_sortOrderChanged())
                
                orderItem = QTableWidgetItem()
                orderItem.setText("") 
                
                #Add widgets to the row 
                self.tbSortFields.insertRow(row)           
                self.tbSortFields.setItem(row,0,fieldItem)
                self.tbSortFields.setCellWidget(row,1,sortWidg)
                self.tbSortFields.setItem(row,2,orderItem)
                row+=1  
                
        self.sorting_cleanUpFieldsList()  
    
    def sorting_sortOrderChanged(self):
        #Slot method when the user defines a sort order 
        cboSender=self.sender()  
        sortOrder=str(cboSender.currentText())
        row=cboSender.row
        orderWidg=self.tbSortFields.item(row,2)
        
        if sortOrder=="None":
            if self._sortOrder>0:
                self._sortOrder-=1
                #Get the removed sort order value
                remVal=int(orderWidg.text())
                self.sorting_setSortOrderWidget(row, "") 
                self.sorting_updateSortOrder(remVal)           
        else:        
            if str(orderWidg.text())is "":            
                self._sortOrder+=1 
                self.sorting_setSortOrderWidget(row, str(self._sortOrder))   
        
    def sorting_updateSortOrder(self,startVal):
        '''
        Update the values of the sorting order when a field
        becomes ineligible 
        ''' 
        numRows = self.tbSortFields.rowCount()
        for r in range(numRows):
            orderWidg = self.tbSortFields.item(r,2)
            widgTxt = orderWidg.text()
            if str(widgTxt)is not "" and int(widgTxt)>startVal:                            
                oldval = int(widgTxt)
                newval = oldval-1
                orderWidg.setText(str(newval)) 
  
    def sorting_setSortOrderWidget(self,row,text):
        '''
        Set the sort order value for the specified table widget item
        extracted from the row number in the widget's collection
        ''' 
        orderWidg=self.tbSortFields.item(row,2)
        orderWidg.setText(text)
        
    def sorting_getFieldItem(self,text):
        #Get the table widget item based on its text attribute
        tabItem=None
        items=self.tbSortFields.findItems(text,Qt.MatchExactly)
        for it in items:
            if str(it.text())==text:
                tabItem=it
                break
        return tabItem

    def sorting_cleanUpFieldsList(self):
        #Remove inapplicable rows from the sort collection
        remFields=[]
        for i in range(self.tbSortFields.rowCount()):
            fieldItem=self.tbSortFields.item(i,0)
            remFields.append(str(fieldItem.text()))
        for f in self.rptFields:
            fIndex = getIndex(remFields,str(f))
            if fIndex!=-1:
                remFields.remove(str(f))
        for r in remFields:
            remItem=self.sorting_getFieldItem(r)
            if remItem is not None:
                row=remItem.row()
                self.tbSortFields.removeRow(row)

    def sorting_getFieldConfig(self,field):    
        #Get field SortInfo
        fs = None
        for r in range(self.tbSortFields.rowCount()):
            fieldWidg = self.tbSortFields.item(r,0)          
            if field == str(fieldWidg.text()):              
                fs = FieldSort()                        
                dir = str(self.tbSortFields.cellWidget(r,1).currentText())
                if not dir == "None":  
                    fs.order = int(str(self.tbSortFields.item(r,2).text()))                
                    if dir == "Ascending":
                        fs.direction = SortDir.Ascending 
                    elif dir == "Descending":
                        fs.direction = SortDir.Descending
        return fs  
         
    def sorting_compileSort(self):
        #Compile the user-defined sorting fields to a standard SQL command
        sortSQL=' ORDER BY '
        rowNumOrder=[]
        rows=self.tbSortFields.rowCount()
        #Loop through to put row numbers based on the sort order defined by the user    
        for r in range(rows):
            orderWidg=self.tbSortFields.item(r,2)
            orderTxt=str(orderWidg.text())
            if orderTxt is not "":
                rowIndex=int(orderTxt)-1  
                rowNumOrder.insert(rowIndex, r) 
                
        for rn in rowNumOrder:
            fieldWidg=self.tbSortFields.item(rn,0)
            sortField=str(fieldWidg.text())   
            cboOrder=self.tbSortFields.cellWidget(rn,1)
            sortOrder=str(cboOrder.currentText())
            sqlSortOrder=''
            if sortOrder=="Ascending":
                sqlSortOrder=' ASC,'
            else:
                sqlSortOrder=' DESC,'
            sortSQL+=sortField + sqlSortOrder
        sortSQL=sortSQL.rstrip(',')
        
        return (len(rowNumOrder),sortSQL)

    def grouping_addField(self):
        #Add a report field for grouping
        numrows=self.tbGroupFields.rowCount()
        
        #Get selected item in the report fields list box
        selItems=self.lstRptFields.selectedItems()
        for selItem in selItems:
            selText=selItem.text()
            self.grouping_addFieldByName(str(selText))
        
    def grouping_addFieldByName(self,field):
        
        #Method does the heavy lifting of adding the field in the grouping list box and corresponding widget
        tabFields=[] 
          
        #updatedFields=self.rptFields
        numrows=self.tbGroupFields.rowCount()      
        tabFields.append(field)
            
        fieldItem = QTableWidgetItem()
        fieldItem.setText(field)
        
        #Add row
        self.tbGroupFields.insertRow(numrows)
        self.tbGroupFields.setItem(numrows,0,fieldItem)
        numrows+=1
        
        #Add Widget
        gpWidg = Groups("gp_" + field)
        self.stackedWidget.addWidget(gpWidg) 
        self.grouping_addFieldNode(field)
          
        #Clean up
        for t in tabFields:                
            #updatedFields.remove(t)
            listItems=self.lstRptFields.findItems(t,Qt.MatchExactly)
            for listItem in listItems:              
                self.lstRptFields.takeItem(self.lstRptFields.row(listItem))
                
        return gpWidg          

    def grouping_removeField(self):
        #Remove the selected group field
        selRows=self.tbGroupFields.selectedItems()
        for selRow in selRows:
            selText=str(selRow.text())
            self.grouping_removeFieldReferences(selText)

    def grouping_cleanUpFields(self):
        #Remove all grouping fields and their references
        gpRows = self.tbGroupFields.rowCount()
        for g in range(gpRows):
            gpItem = self.tbGroupFields.item(g,0)
            fieldName = str(gpItem.text())
            self.grouping_removeFieldReferences(fieldName)
            self.tbGroupFields.removeRow(g)
                
    def grouping_removeFieldReferences(self,field):
        #Remove grouping widget, tree view item and row
        
        #Remove Item
        gpItems = self.tbGroupFields.findItems(field,Qt.MatchExactly)
        if len(gpItems) > 0:
            remItem = gpItems[0]
            self.tbGroupFields.removeRow(remItem.row())        
        #Insert list item
        self.lstRptFields.addItem(field)        
        #Remove settings widget
        gpWidg=self.__displayGetStWidget("gp_" + field)
        self.stackedWidget.removeWidget(gpWidg)        
        #Remove tree node
        self.grouping_removeFieldNode(field)
        
    def grouping_addFieldNode(self,groupfield):
        #Add group field node to the tree view
        trGroups=self.trRptSettings.findItems("Groups",Qt.MatchExactly,0)[0]
        trn = QTreeWidgetItem([groupfield])
        trGroups.addChild(trn)
    
    def grouping_removeFieldNode(self,groupfield):
        #Remove group field node in the tree view 
        trGroups=self.trRptSettings.findItems("Groups",Qt.MatchExactly,0)[0]
        trn=self.display_getChildNode("Groups", groupfield)
        trGroups.removeChild(trn)
    
    def grouping_orderQuery(self):
        #Order results by the specified grouping fields
        sortSQL=" ORDER BY "
        rowCount=self.tbGroupFields.rowCount()
        for r in range(rowCount):
            cellItem=self.tbGroupFields.item(r,0)
            cellTxt=str(cellItem.text())
            sortSQL+=cellTxt + " ASC,"
        sortSQL=sortSQL.rstrip(',')
        return (rowCount,sortSQL)

    def grouping_getFieldConfig(self,field):
        #Get the group settings for the specified field 
        gs = None      
        for r in range(self.tbGroupFields.rowCount()):
            groupItem = self.tbGroupFields.item(r,0)
            groupText = str(groupItem.text())
            if groupText == field:              
                gs = GroupSettings()
                gs.isInGroup = True
                gs.order = r              
        return gs
                                        
    def display_updateReportFields(self):
        #Update tree fields list in the display section
        trFields=self.trRptSettings.findItems("Fields",Qt.MatchExactly,0)[0]
        #Check if a report item has been added into the list or not    
        for f in self.rptFields:      
            rWidg=self.display_getChildNode("Fields", f)
            if rWidg==None:                
                tr=QTreeWidgetItem([f])
                trFields.addChild(tr)
                #Add settings widget as well
                self.display_addFieldWidget(f)
        #Clean up the field tree items and associated widgets
        self.display_cleanUpFieldsList()
            
    def display_cleanUpFieldsList(self):
        #Remove items from the fields tree node that are no longer applicable
        trFields=self.trRptSettings.findItems("Fields",Qt.MatchExactly,0)[0]
        lstFields=[]
        for f in range(trFields.childCount()):
            tw=trFields.child(f)
            lstFields.append(tw.text(0))
        #Remove (from the list) those items that exist for both report and tree instances
        for r in self.rptFields: 
            fIndex = getIndex(lstFields,str(r))
            if fIndex!=-1:
                lstFields.remove(str(r))
        #Now clean up the tree node items     
        for obsItem in lstFields:
            obsNode=self.display_getChildNode("Fields", obsItem)
            obsWidg=self.__displayGetStWidget(obsItem)
            if obsNode!=None:
                trFields.removeChild(obsNode)
            if obsWidg!=None:
                self.stackedWidget.removeWidget(obsWidg)    
        
    def display_getChildNode(self,parentStr,childStr):
        #Get the tree item based on the parent and child texts respectively
        trParent=self.trRptSettings.findItems(parentStr,Qt.MatchExactly,0)[0]
        cNode=None
        for t in range(trParent.childCount()):
            trChild=trParent.child(t)
            if trChild.text(0)==childStr:
                cNode=trChild
                break
        return cNode

    def display_getChildList(self,parentStr):
        #Get the names list of the child nodes for the specified parent node
        trParent=self.trRptSettings.findItems(parentStr,Qt.MatchExactly,0)[0]
        childNodes=[]
        for t in range(trParent.childCount()):
            trChild=trParent.child(t)
            childNodes.append(str(trChild.text(0)))
        return childNodes
        
    def display_titleColor(self):
        #Shows the color dialog and set the title color
        tColor=QColorDialog.getColor(Qt.darkBlue, self,"Select title color") 
        if tColor.isValid():
            tPalette=QPalette(tColor)            
            self.lblTitleClr.setPalette(tPalette)
        
    def display_treeViewSelection(self):
        #Load appropriate widget when the report display's tree view selection changes
        trSel=self.trRptSettings.selectedItems()[0]
        searchTxt=trSel.text(0)
        #Since the groups and field have the same name,return the correct widget
        trParent=trSel.parent()
        if not trParent is None:
            if trParent.text(0)=="Groups":
                searchTxt="gp_" + searchTxt
        #Retrieve widget from the stack widget based on the selected item
        for w in range(self.stackedWidget.count()):
            widg=self.stackedWidget.widget(w)                
            if widg.ID==searchTxt:                     
                self.stackedWidget.setCurrentWidget(widg)
                break    
        
    def display_addFieldWidget(self,reportItem):
        '''
        Create a widget for each report field added by the user and add it to the stack
        only if it does not exist.
        '''
        elWidg=self.__displayGetStWidget(reportItem)
        if elWidg==None:        
            fieldWidg = FieldBase(reportItem)    
            self.stackedWidget.addWidget(fieldWidg)
    
    def __displayGetStWidget(self,widgetID):
        #Get a widget in the stack widget control based on the form identifier
        stWidg=None
        for s in range(self.stackedWidget.count()):
            widg=self.stackedWidget.widget(s)
            if widg.ID==widgetID:
                stWidg=widg
                break
        return stWidg

    def display_autoWidth(self):
        #automatically compute the field width
        #Get the paper size defined by the user
        layoutWidg=self.__displayGetStWidget("Layout")
        w,h=layoutWidg.PageSize()
        cmWidth=w/(72/2.54)
        return (cmWidth/len(self.rptFields))

    def display_CompileSettings(self):
        #Compile the user defined settings
        self.rptElements.headerElements=[]
        self.rptElements.detailElements=[]
        self.rptElements.groups=[]
        
        #Config File Settings
        self.rptElements.footer=self.config.get("ReportMessages","Footer")
        self.rptElements.author=self.config.get("ReportMessages","Author")
        self.rptElements.subject=self.config.get("ReportMessages","Subject")
        
        #List of image fields
        self.imageFields=[]
        
        #Get column style settings
        left=0
        width=self.display_autoWidth()
        colStyle=self.__displayGetStWidget("Field Names").columnStyle()    
        columnList=self.display_getChildList("Fields")
        
        for field in columnList:
            fWidg=self.__displayGetStWidget(field)
            fWidg.elLeft=left
            fWidg.elWidth=width
            fWidg.columnStyle=colStyle
            left+=width
            
        for i in range(self.stackedWidget.count()):
            w=self.stackedWidget.widget(i)
            if isinstance(w,Title):
                self.rptElements.headerElements.append(w.systemExpression())
                self.rptElements.title=w.elText
                self.rptElements.headerBorders=w.elBorder
                
            elif isinstance(w,FieldBase):            
                self.rptElements.detailElements.append(w.getObjectValue()) 
                self.rptElements.headerElements.append(w.getLabel())                       
                self.rptElements.detailBorders=w.elBorder
                
                #Check if it is an image field
                if w.isImageField():
                    self.imageFields.append(str(w.ID))
                    
            elif isinstance(w,Groups):            
                self.rptElements.groups.append(w.getReportGroup())
                
            elif isinstance(w,ReportLayout):
                self.rptElements.page_size=w.PageSize()
                self.rptElements.margin_top=w.TopMargin()
                self.rptElements.margin_bottom=w.BottomMargin()
                self.rptElements.margin_left=w.LeftMargin()
                self.rptElements.margin_right=w.RightMargin()
            '''
            elif isinstance(w,frmFieldNames):
                self.rptElements.headerElements.append(w.getLabel())
        '''

    def saveReportSettings(self,file):
        #Helper for saving user report settings to file
        self.showhideProgressDialog("Saving Report Settings...")
        
        #Create report config object
        rptConfig = STDMReportConfig(self.tabName)
        
        #Loop through all report elements' settings
        for i in range(self.stackedWidget.count()):
            w = self.stackedWidget.widget(i)
            
            #Get report element 
            rptEl = w.getSettings()
            
            #Group dialog settings are not added directly to the collection but through the DBField proxy
            if not rptEl.parent == "Groups":               
                #Check if it is a definition for database fields
                if rptEl.parent == "Fields":
                    df = DbField()   
                                   
                    #copy attributes from ReportElement base to DbField object
                    copyattrs(rptEl,df,["dialogSettings","parent","name"])   
                                                                 
                    #Set field configuration
                    fc = FieldConfig()
                    fc.sortInfo = self.sorting_getFieldConfig(rptEl.name)
                    
                    #Set grouping information
                    gi = self.grouping_getFieldConfig(rptEl.name)
                    if not gi == None:
                        gpDialog = self.__displayGetStWidget("gp_" + rptEl.name)
                        if gpDialog != None:                          
                            gi.dialogSettings = gpDialog.getSettings().dialogSettings
                            fc.groupingInfo = gi
                            
                    #Get field index
                    fc.reportOrder = self.rptFields.index(rptEl.name)
                    df.uiConfiguration = fc              
                    rptEl = df
                rptConfig.addElement(rptEl)   
                       
        rptConfig.setFilter(str(self.txtSqlParser.toPlainText()))
        rptConfig.setVersion(1.1)
        
        #Serialize to file 
        rptSerializer = ReportSerializer(file) 
        rptSerializer.serialize(rptConfig)
        self.showhideProgressDialog("",False)

    def loadSettings_activateControls(self,reportFields):
        #Enable supporting controls in the report builder widget          
                
        #Load report fields
        self.updateSelectedReportFields(reportFields)
        #Select the first item in the list    
        self.selectAvailFieldItem()

    def loadReportSettings(self,file):
        #Helper for restoring previously saved report settings
        
        #Deserialize report settings 
        rptSerializer = ReportSerializer(file) 
        rptValid, rptConf = rptSerializer.deserialize()
        #Validate if the object is an STDM Report Settings file      
        if rptValid:          
            #Check if the table exists
            tabExists = self._tableExists(rptConf.table)          
            if tabExists:
                self.showhideProgressDialog("Restoring Report Settings...")              
                friendlyTabName = self.tabNames[rptConf.table]  
                
                #Force builder reset even if the loaded report refers to the previously loaded table            
                if rptConf.table == self.tabName:                                
                    self.tabChanged(friendlyTabName)                  
                else:                  
                    self.tabName = rptConf.table
                    #Set focus to report table in the drop down menu
                    setComboCurrentIndexWithText(self.comboBox,friendlyTabName)
                
                #Validate the fields
                validTabFields = table_column_names(rptConf.table)                      
                validRptFields, invalidRptFields = compareLists(validTabFields,rptConf.fields)  
                            
                #Configure supporting controls
                self.loadSettings_activateControls(validRptFields)
                
                #Set filter statement
                self.txtSqlParser.setText(rptConf.filter)
                
                #Group order container
                gpInfoCollection =[]
                
                #Sort info container
                sortInfoCollection =[]
                
                #Iterate report elements
                for r in rptConf.reportElementCollection:
                    if r.parent != "Groups":
                        #Get corresponding widget and load the settings
                        rptWidg = self.__displayGetStWidget(r.name)
                        if not rptWidg == None:
                            rptWidg.loadSettings(r.dialogSettings)
                            
                        #Set grouping and sorting configuration
                        if r.parent == "Fields":
                            gpInfo = r.uiConfiguration.groupingInfo
                            if gpInfo != None:
                                gpInfo.field = r.name
                                gpInfoCollection.append(gpInfo)
                            fieldSort = r.uiConfiguration.sortInfo
                            
                            if fieldSort.direction != SortDir.Null:
                                fieldSort.field = r.name
                                sortInfoCollection.append(fieldSort) 
                                                           
                #Sort GROUPINFO items using the order attribute then add fields to the report builder controls
                gpInfoCollection.sort(key=lambda g: g.order)
                for g in gpInfoCollection:
                    groupDlg = self.grouping_addFieldByName(g.field)
                    groupDlg.loadSettings(g.dialogSettings) 
                    
                #Order SORTINFO items using the order attribute then add fields to the report builder controls
                sortInfoCollection.sort(key=lambda s: s.order)
                for s in sortInfoCollection:
                    sortItem = self.sorting_getFieldItem(s.field)
                    if sortItem is not None:
                        rowIndex = sortItem.row()
                        dirCombo = self.tbSortFields.cellWidget(rowIndex,1)
                        if s.direction == SortDir.Ascending:
                            setComboCurrentIndexWithText(dirCombo, "Ascending")
                        elif s.direction == SortDir.Descending:
                            setComboCurrentIndexWithText(dirCombo, "Descending")    
                                                                 
                #Show message of invalid fields
                if len(invalidRptFields) > 0:
                    fieldsStr = ",".join(invalidRptFields)
                    self.ErrorInfoMessage(fieldsStr + " columns do not exist in the current table definition.\nThey will not be included in the report") 
            else:
                self.showhideProgressDialog("", False)
                self.ErrorInfoMessage(rptConf.table + " table or view does not exist in the database")
        else:
            self.showhideProgressDialog("", False)
            fileName = str(file.section("/",-1))
            self.ErrorInfoMessage(fileName + " is not a valid STDM Report Settings file.\n Please validate the" + \
                                  " source of the file")
        
        self.showhideProgressDialog("", False)
      
    def showhideProgressDialog(self,message,show = True):
        #Generic progress dialog for the report builder window    
        if show == True:                    
            self.progressDlg.setWindowModality(Qt.WindowModal)
            self.progressDlg.setLabelText(message) 
            self.progressDlg.setCancelButtonText("")
            self.progressDlg.setMaximum(0)
            self.progressDlg.setMinimum(0)
            self.progressDlg.show()
        else:
            self.progressDlg.close()
            self.progressDlg.reset()
  
    def saveReport(self):
        #Serialize user report settings to file
        rptConfFile = QFileDialog.getSaveFileName(self,"STDM Report","","STDM Report(*.trs)")
        if rptConfFile != "":
            self.saveReportSettings(rptConfFile)     
          
    def loadReport(self):
        #Load previously saved report settings
        rptConfFile = QFileDialog.getOpenFileName(self, "STDM Report","","STDM Report(*.trs)")
        if rptConfFile != "":
            self.loadReportSettings(rptConfFile)
              
    def generateReport(self):
        #Generate report
        dbResults = self.filter_buildQuery()   
        if dbResults != None:
            #Get user settings
            self.display_CompileSettings()
            #Create query set
            tmpDir,qSet = createQuerySet(self.rptFields,dbResults,self.imageFields)        
            stdmRpt = STDMReport(qSet,self.rptElements)        
            rptFile = QFileDialog.getSaveFileName(self,"STDM Report","","Report Document(*.pdf)")  
                  
            if rptFile != "":            
                rptGenerator=STDMGenerator(stdmRpt,rptFile)
                rptGenerator.generateReport()            
                self.InfoMessage("The report has been successfully created and written to {0}".format(rptFile))
                self.close()
                
    def _tableExists(self,tableName):
        """
        Assert whether the a table or view with the given name exists in the 'public' schema.
        """
        tables = pg_tables()
        views = pg_views()
        tables.extend(views)
        
        tableIndex = getIndex(tables, tableName)
        
        return False if tableIndex == -1 else True
        
    def ErrorInfoMessage(self,Message):      
        #Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(Message)
        msg.exec_() 
    
    def InfoMessage(self,Message):      
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(Message)
        msg.exec_() 
