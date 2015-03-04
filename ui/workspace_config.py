# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
# Import the PyQt and QGIS libraries

import platform
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui_workspace_config import Ui_STDMWizard
from stdm.data import ConfigTableReader,deleteProfile,profileFullDescription,tableFullDescription,deleteColumn,\
deleteTable,lookupData2List,deleteLookupChoice,SQLInsert,LicenseDocument,_execute

from attribute_editor import AttributeEditor
from table_propertyDlg import TableProperty
from addtable import TableEditor
from stdm.security import RoleProvider
from profileDlg import ProfileEditor
from lookup_values_dlg import ADDLookupValue
from sqlalchemy.sql.expression import text
from sqlalchemy.exc import SQLAlchemyError

class WorkspaceLoader(QWizard,Ui_STDMWizard):
    def __init__(self, parent):
        #Initialize the Qwizard parent
        QWizard.__init__(self,parent)
        #inherit the GUI from Designer.
        self.setupUi(self)
        self.registerFields()
        #Initialize the xml filehandler
        self.tableHandler = ConfigTableReader()
        self.tableName=None
        self.tableList=[]
        self.profile=''
        self.geomEntity=None

        #if platform.system() =="Windows":
        #    self.setWizardStyle(QWizard.AeroStyle)
        self.setWindowFlags(Qt.Dialog| Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        
        QObject.connect(self.lstEntity,SIGNAL('clicked(QModelIndex)'),self.seletedTableAttrib)
        QObject.connect(self.pftableView,SIGNAL('clicked(QModelIndex)'),self.selectedTableName)
        QObject.connect(self.lstEntity_2,SIGNAL('clicked(QModelIndex)'),self.relationForTable)       
        QObject.connect(self.tblEdit, SIGNAL('clicked(QModelIndex)'), self.selectedColumnIndex)
        QObject.connect(self.tblEdit_2, SIGNAL('clicked(QModelIndex)'), self.selectedColumnIndex)
        QObject.connect(self.tblLookupList, SIGNAL('clicked(QModelIndex)'), self.lookupColumns)
        
        self.btnAdd.clicked.connect(self.addTableColumn)
        self.btnEdit.clicked.connect(self.columnEditor)
        self.btnProperty.clicked.connect(self.tableRelationEditor)
        self.btnDelete.clicked.connect(self.deletedSelectedTable)
        self.btnSQL.clicked.connect(self.schemaPreview)
        #self.btnHTML.clicked.connect(self.HTMLFileView)
        self.btnBrowse.clicked.connect(self.defWorkDir)
        self.btnBrowse2.clicked.connect(self.setCertificatePath)
        self.btnTemplates.clicked.connect(self.setTemplatesPath)
        self.btnBrowse2_2.clicked.connect(self.settingsPath)
        #self.btnRunSchema.clicked.connect(self.setDatabaseSchema)
        self.cboProfile.currentIndexChanged.connect(self.selectionChanged)
        self.btnNew.clicked.connect(self.setTableName)
        self.btnNew_2.clicked.connect(self.editTableName)
        self.btnNewP.clicked.connect(self.addProfile)
        self.btnPDelete.clicked.connect(self.deleteProfile)
        self.txtHtml.textChanged.connect(self.updateSQLFile)
        self.btnDel.clicked.connect(self.deleteTableColumn)
        self.btnPropDel.clicked.connect(self.deleteTableRelation)
        self.btnLkDel.clicked.connect(self.deleteLookupChoice)
        #self.toolbtn.clicked.connect(self.popup)
        self.btnAddLk.clicked.connect(self.addLookupValue)
        self.helpRequested.connect(self.HelpContents)
        self.rbSchema.clicked.connect(self.setSqlIsertDefinition)
        self.rbSchemaNew.clicked.connect(self.setSqlIsertDefinition)
        #self.chkPdefault.clicked.connect(self.setDefualtProfile)

        try:
            settings = self.tableHandler.pathSettings()
            if settings[1].get('Config') == None:
               self.startId() == 1
            elif settings[1].get('Config') != None:
                self.setStartId(2)
        except:
            pass
        
    def registerFields(self):
        self.setOption(self.HaveHelpButton, True)  
        pgCount=self.page(1)
        pgCount.registerField("Accept",self.rbAccpt)
        pgCount.registerField("Reject",self.rbReject)
        pgCount2=self.page(4)
        #pgCount2.registerField("SelectionMenu",self.toolbtn)


    def validateCurrentPage (self):
        validPage = True
        if self.currentId()==1:
            if not self.rbAccpt.isChecked():
                self.InfoMessage(" You must agree to the disclaimer to continue")
                validPage=False
            if self.rbReject.isChecked():
                self.InfoMessage("Rejecting to comply with disclaimer policy will cause the wizard to exit.\
                 STDM will no to be accessible")
                validPage=False
        if self.currentId()==2:
            if self.txtDefaultFolder.text()=='' or self.txtCertFolder.text()=='' or self.txtSetting.text()=='':
                self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","Data directory paths are not given"))
                validPage=False
        if self.currentId()==3:
            if self.profile=='':
                if self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader",\
                                        "You have not selected any default profile for your configuration. \n "\
                                "The current profile will be used as default instead"))==QMessageBox.No:
                    validPage=False
        if self.currentId() == 5:
            if self.setDatabaseSchema() == 'success' or self.rbSkip.isChecked():
                validPage = True

            else:
                validPage = False

        return validPage
                    
    
    def initializePage(self, int):
        if self.currentId()==1:
            self.licenseFile()
            
        if self.currentId()==2:
            self.configPath()

        if self.currentId()==3:
            self.pathSettings()
            self.profileContent()
        if self.currentId()==4:
            #self.toolbtn.setPopupMode(QToolButton.InstantPopup)
            self.registerProfileSettings()
            self.readUserTable()
            try:
                if self.tableName:
                    self.loadTableColumns(self.tableName)
            except Exception as ex:
                self.ErrorInfoMessage(ex.message)
            self.tblLookup.setAlternatingRowColors(True)


        #if self.currentId() == 6:
         #   self.set_social_tenure_entities()

        if self.currentId()==5:
            self.txtHtml.hide()
            self.rbSchema.setChecked(True)
            self.setSqlIsertDefinition()

        if self.currentId()==6:
            try:
                 self.setDatabaseSchema()
            except:
                return
    
    def checkTablesExist(self,activeProfile):
        '''Method to check if the right config exist in the directory and then return the table names'''
        tableExist=self.tableHandler.tableListModel(activeProfile)
        return tableExist
                                 
    def readUserTable(self):
        '''Start the profile table list for editing attributes'''
        profile=self.cboProfile.currentText()
        model=self.tableHandler.tableListModel(self.profile) 
        self.lstEntity.setModel(model)
        self.lstEntity_2.setModel(model)
        self.lstEntity.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstEntity.customContextMenuRequested.connect(self.popup)
        self.lstEntity.setWrapping(True)
        self.populateLookup()
    
    def lookupTables(self):
        '''get the lookup tables'''
        return self.tableHandler.lookupTable()
    
    def populateLookup(self):   
        lookupModel=self.tableHandler.lookupTableModel()
        self.tblLookupList.setModel(lookupModel)
        
    def loadTableData(self,profile,widget):
        '''method returns the model to the passed listview widget'''
        model=self.tableHandler.profile_tables(profile)
        #QMessageBox.information(self,"Test",str(type))
        widget.setModel(model)
        widget.resizeColumnToContents(0)
        #return widget    
    
    def profileContent(self):
        '''Loads all available content/table from the config for the selected profile'''
        profiles=self.tableHandler.STDMProfiles()
        #for pf in profiles:
        self.cboProfile.clear()
        self.cboProfile.insertItems(0,profiles)
        self.cboProfile.setCurrentIndex(0)
        self.loadTableData(self.profile, self.pftableView)
        
    def setDefualtProfile(self):
        '''
        Check to see if user want to save a specific profile to settings
        '''
        if self.cboProfile.currentText()!='':
            self.profile=self.cboProfile.currentText()
        else:
            self.profile=self.cboProfile.itemText(0)
                
    def selectionChanged(self):
        '''Listen to user selection for the profile to load the corresponding table'''
        self.tableName=None
        self.profile=str(self.cboProfile.currentText())
        self.loadTableData(self.profile, self.pftableView)
        self.registerProfileSettings()
        self.lblDescprition.setText(profileFullDescription(self.profile))
        
    def registerProfileSettings(self):
        profile=QApplication.translate("WorkspaceLoader","currentProfile")
        self.tableHandler.setProfileSettings({profile:self.profile})      
        
    def loadTableColumns(self, tableName):
        '''Get a list of all Columns defined for the given table name'''
        columnModel=None
        if tableName==None:
            self.ErrorInfoMessage("Table Not defined")
            return
        columnModel=self.tableHandler.columns(self.profile,tableName)
        self.tblEdit.clearSpans()
        self.tblEdit.setModel(columnModel)
        self.loadTableRelations(tableName)
        self.tblEdit.resizeColumnsToContents()
        self.tblEdit.setColumnWidth(4,100)
        self.showGeometryColumns(tableName)
    
    def loadTableRelations(self, tableName):
        '''Method to load defined relations for the given table from the config'''
        self.tblEdit_2.clearSpans()
        if tableName==None:
            self.ErrorInfoMessage("No Table selected")
            return
        relationModel=self.tableHandler.tableRelation(tableName)
        self.tblEdit_2.setModel(relationModel)
        

    def showGeometryColumns(self,tableName):
        '''method to show defined geometry columns '''
        self.tblLookup_2.clearSpans()
        if tableName == None:
            return
        geometryModel = self.tableHandler.geometryData(tableName)
        self.tblLookup_2.setModel(geometryModel)
               
    def relationForTable(self):
        '''Load defined relations for the selected table'''
        self.tblEdit_2.clearSpans()
        selectIndex = self.lstEntity_2.selectedIndexes()
        if len(selectIndex)>0:
            tabName = selectIndex[0]
            self.loadTableRelations(tabName.data())
            self.tableName = tabName.data()
        
    def EditTableNode(self):
        '''Select table for editing and adding new attributes'''
        selectIndex=self.lstEntity.selectionModel().selectedIndexes()
        if len(selectIndex)>0:
            tabName=selectIndex[0]
            self.tableName=tabName.data()
            self.loadTableColumns(self.tableName)
        
    def seletedTableAttrib(self):
        '''Modify table data including table name'''
        selectIndex=self.lstEntity.selectionModel().selectedIndexes()
        if len(selectIndex)>0:
            tabName=selectIndex[0]
            self.tableName=tabName.data()
            self.loadTableColumns(self.tableName)
           
    def selectedTableName(self):
        '''Modify table data including table name'''
        selectIndex=self.pftableView.selectionModel().selectedIndexes()
        if len(selectIndex)>0:
            tabName=selectIndex[0]
            self.loadTableColumns(tabName.data())
            self.tableName=tabName.data()
        else:
            return None

    def addTableColumn(self):
        '''add new attribute for the table'''
        if self.tableName!=None:
            colDlg=AttributeEditor(str(self.cboProfile.currentText()),self.tableName,self)
            colDlg.exec_()
            self.loadTableColumns(self.tableName)
        else:
            self.ErrorInfoMessage("Please select table to add attributes")
            return
        self.populateLookup()
    
    def columnEditor(self):
        '''Edit selected table column'''
        try:
            selCols=self.tblEdit.selectionModel().selectedIndexes() 
            EditorSession=[]
            if len(selCols)>0 and self.tableName!=None:
                EditorSession.append(selCols[0].data())
                EditorSession.append(selCols[1].data())
                EditorSession.append(selCols[2].data())
                EditorSession.append(selCols[3].data())
                colDlg = AttributeEditor(str(self.cboProfile.currentText()),self.tableName,self,args=EditorSession)
                colDlg.exec_()
            else:
                self.InfoMessage(QApplication.translate("WorkSpaceLoader","No table column is selected for editing"))
                return
        except:
            pass 
        self.loadTableColumns(self.tableName)
        self.loadTableRelations(self.tableName)
        self.populateLookup()
        
    def tableRelationEditor(self):
        if self.tableName!=None:
            colDlg=TableProperty(str(self.cboProfile.currentText()),self.tableName,self)
            colDlg.exec_()
            self.loadTableRelations(self.tableName)
        else:
            self.ErrorInfoMessage("Please select table to add attributes")
            return
    
    def selectedColumnIndex(self):
        '''Method to return selected table item in the list'''
        selCols=self.tblEdit.selectionModel().selectedIndexes() 
        if len(selCols)>0:
            item=selCols[0].data()     
        else:
            return
    def lookupColumns(self):

        selCols=self.tblLookupList.selectionModel().selectedIndexes() 
        if len(selCols)>0:
            tableName=selCols[0].data()    
            self.lookupColumnsTowidget(tableName) 
            self.tableName=tableName
            self.lookupDefinedValues()
        else:
            self.ErrorInfoMessage("No selections")
            return
        
    def lookupColumnsTowidget(self, tableName):
        '''Get a list of all Columns defined for the given table name'''
        columnModel=None
        if tableName==None:
            self.ErrorInfoMessage("lookup Not defined")
            return
        columnModel=self.tableHandler.lookupColumns(tableName)
        self.tblEdit.clearSpans()
        self.tblEdit.setModel(columnModel)
        self.loadTableRelations(tableName)
        self.tblEdit.resizeColumnsToContents()
  
    def setTableName(self):
        actionState=[self.profile,QApplication.translate("WorkspaceLoader","Add Table")]
        self.addTable(actionState)
        self.loadTableData(self.profile, self.pftableView)
        
    def editTableName(self):
        if self.tableName==None:
            self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","No table is selected"))
            return
        actionState=[self.profile,QApplication.translate("WorkspaceLoader","Edit Table")]
        self.addTable(actionState) 
        self.loadTableData(self.profile, self.pftableView)
        
    def addTable(self,actionState):
        '''add new table'''
        if len(actionState)>1:
            dlg=TableEditor(actionState,self.tableName,self)
            dlg.exec_()
        
    def addProfile(self):
        '''add new profile'''
        profileDlg=ProfileEditor(self)
        profileDlg.exec_()
        self.profileContent()
        
    def deletedSelectedTable(self):
        #use the delete buttont to remove the selected table
        if self.tableName==None:
            self.ErrorInfoMessage(QApplication.translate('WorkspaceLoader',"No table is selected for this operation"))
            return
        else:
            if self.warningInfo(QApplication.translate("WorkspaceLoader","You are about to delete %s table" %self.tableName))==QMessageBox.Yes:
                deleteTable(self.profile,self.tableName)
                self.loadTableData(self.profile, self.pftableView)
                self.tableName=None
            else:
                return
    
    def deleteProfile(self):
        if self.cboProfile.currentIndex==-1:
            self.InfoMessage(QApplication.translate("WorkspaceLoader","No profile found"))
            return
        else:
            if self.warningInfo(QApplication.translate("WorkspaceLoader","You are about to delete current profile"))==QMessageBox.Yes:
                deleteProfile(self.profile)
            else: return
            self.profileContent()
            
    def deleteTableColumn(self):
        '''ensure we deleted the selected table column only by matching name entry in the config'''
        try:
            if self.warningInfo(QApplication.translate('WorkspaceLoader',\
                                                       "You are about to delete selected column from table "+\
                                                       self.tableName))==QMessageBox.Yes:
                selCols=self.tblEdit.selectionModel().selectedIndexes() 
                if len(selCols)>0:
                    item=selCols[0].data()
                    element="columns"
                    if str(self.tableName).startswith('check'):
                        deleteColumn(self.profile,'lookup',self.tableName,element,'name',str(item))
                        self.lookupColumnsTowidget(self.tableName)
                    else:
                        deleteColumn(self.profile,'table',self.tableName,element,'name',str(item))
                        try:
                            deleteColumn(self.profile,'table',self.tableName,'constraints','column',str(item))
                        except Exception as ex:
                            self.ErrorInfoMessage(str(ex.message))
                        self.loadTableColumns(self.tableName)
            else:
                return
        except:
            self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","Unable to delete table"))
            return
    
    def deleteTableRelation(self):
        '''delete defined table relation from the config '''
        if self.warningInfo(QApplication.translate('WorkspaceLoader',\
                                                       "Are you sure you want to deleted selected relation for table "+\
                                                       self.tableName))==QMessageBox.Yes:
            selCols=self.tblEdit_2.selectionModel().selectedIndexes() 
            if len(selCols)>0:
                item=selCols[0].data()
                element="relations"
                deleteColumn(self.profile,'table',self.tableName,element,'name',str(item))
                self.loadTableRelations(self.tableName)
        
    def deleteLookupChoice(self): 
        '''remove a text from the lookup choices'''
        selIndx =self.tblLookup.selectionModel().selectedIndexes()
        if selIndx:
            selItem = selIndx[0]
        else:
            self.ErrorInfoMessage(QApplication.translate('WorkspaceLoader',\
                                                       "No text is selected from the lookup choices"))
            return
        if selItem!=None and not self.tableName.startswith('check'):
            self.ErrorInfoMessage(QApplication.translate('WorkspaceLoader',\
                                                       "selected table is not a lookup table"))
            return
        if self.warningInfo(QApplication.translate('WorkspaceLoader',\
                                                       "Are you sure you want to delete "+str(selItem.data())+ " choice from "+\
                                                       self.tableName))==QMessageBox.Yes:
            if str(self.tableName).startswith('check'):
                deleteLookupChoice(self.profile,'lookup',self.tableName,'data','value',str(selItem.data()))
                self.lookupDefinedValues()
        
           
    def addLookupValue(self):
        if self.tableName==None:
            self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","No table is selected"))
            return
        if self.tableName!=None and self.tableName.startswith("check"):
            lkDlg=ADDLookupValue(self)
            if lkDlg.exec_()==QDialog.Accepted:
                lkName=lkDlg.value
                self.addLookupToWidget(lkName)
        else:
            self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","Selected table is not a lookup"))
    
    def addLookupToWidget(self,lkText):
        '''Add lookup to config list and add it to view widget'''
        self.tableHandler.addLookupValue(self.tableName,str(lkText).capitalize())
        self.lookupDefinedValues()
                
    def lookupDefinedValues(self):
        '''load all defined lookup choices for the selected table'''
        lookUpModel = self.tableHandler.readLookupList(self.tableName)
        self.tblLookup.clearFocus()
        self.tblLookup.setModel(lookUpModel)

    def schemaPreview(self):
        #Method to allow the user preview customized xml in SQL format
        if self.txtHtml.isVisible():
            self.txtHtml.hide()
            self.txtHtml.clear()
            self.btnSQL.setText(QApplication.translate("WorkspaceLoader","Show Generated SQL"))
            
        else:
            self.rawSQLDefinition()
            self.txtHtml.setVisible(True)
            self.btnSQL.setText(QApplication.translate("WorskpaceLoader","Close SQL View"))
    
    def rawSQLDefinition(self):
        '''read sql definition on the UI'''
        self.txtHtml.clear()
        fileN=self.SQLFileView()
        color=QColor(192, 192, 192)
        self.txtHtml.setTextBackgroundColor(color)
        with open(fileN,'r')as f:
            self.txtHtml.insertPlainText(f.read())
        f. close()
            
    def setSqlIsertDefinition(self):
        '''Add insert sql statement for the lookup defined values'''
        fileN=self.SQLFileView()
        if self.rbSchemaNew.isChecked():
            self.tableHandler.saveXMLchanges()
            lookups=self.lookupTables()
            for lookup in lookups:
                lookupTextList=lookupData2List(self.profile,lookup)
                sqlInsert=SQLInsert(lookup,lookupTextList)
                SQLSt=sqlInsert.setInsertStatement()
                with open(fileN,'a')as f:
                    for row in SQLSt:
                        f.write(row)
                        f.write("\n")
                f. close()
            self.setRelation(fileN,sqlInsert)
        if self.rbSchema.isChecked():
            self.tableHandler.upDateSQLSchema()
        self.rawSQLDefinition()
                
    def SQLFileView(self):
        '''read the SQL in directory'''
        file=self.tableHandler.sqlTableDefinition()
        return file
    
    def setRelation(self,fileN,sql):
        with open(fileN,'a')as f:
            f.write(sql.spatialRelation())
        f.close()
            
    def setDatabaseSchema(self):    
        '''run generated SQL to the database'''
        valid = 'success'
        if self.rbSkip.isChecked():
            pass
        else:
            self.DropSchemaTables()
            fileName = self.SQLFileView()
            try:
                with open(fileName,'r')as f:
                    sqlSt=text(f.read())
                    roleP=RoleProvider()
                    roleP._execute(sqlSt)
                    self.assignRoles()
                    self.InfoMessage("Changes successfully saved in the STDM database")
                    self.tableHandler.trackXMLChanges()
                    return valid
            except SQLAlchemyError as ex:
                return self.ErrorInfoMessage(str(ex.message))
            except IOError as ex:
                return self.ErrorInfoMessage(str(ex.message))
    
    def assignRoles(self):
        if self.rbSchemaNew.isChecked():
            roleP=RoleProvider()
            roles=roleP.GetSysRoles()
            for role in roles:
                roleSql=text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO %s;"%(role))
                _execute(roleSql)
        
    def DropSchemaTables(self):
        '''Check if table is already defined in pgtables and drop it'''
        if self.rbSchemaNew.isChecked():
            self.tableList = self.tableHandler.fulltableList()
            try:
                for table in self.tableList:
                    sqlSt = text("drop table if exists " +table+ " cascade;")
                    _execute(sqlSt)
            except SQLAlchemyError as ex:
                return self.ErrorInfoMessage(str(ex.message))
        else:
            pass
    
    def updateSQLFile(self):
        '''Method to record and save changes whenever the document's content changes'''
        fileName = self.SQLFileView()
        if str(fileName).endswith(".sql"):
            doc = self.txtHtml.document()
            docText = str(doc.toPlainText())
            if docText != "":
                try:
                    with open(fileName,'w')as f:
                        f.write(docText)
                    f.close()
                except IOError as io:
                    self.ErrorInfoMessage(io.message)
            else: return
         
    def popup(self, QAction):
        #A shortcut menu to allow the user to customize table details on the forms page
        menu=QMenu()
        #self.toolbtn.setMenu(menu)
        self.addAction = menu.addAction(QApplication.translate("WorkspaceLoader","Add Table"))
        menu.addSeparator()
        self.editAction = menu.addAction(QApplication.translate("WorkspaceLoader","Rename Table"))
        self.closeAction=menu.addAction(QApplication.translate("WorkspaceLoader","Delete Table"))
        cursor=QCursor()
        pos=cursor.pos()
        action = menu.exec_(self.mapToGlobal(pos))
        if action==self.addAction:
            self.setTableName()
        if action==self.editAction:
            if self.tableName==None:
                self.ErrorInfoMessage(QApplication.translate("WorkspaceLoader","No selected table found"))
                return
            else:
                self.editTableName()
                del menu
        if action==self.closeAction:
            if self.tableName!=None:
                if self.warningInfo(QApplication.translate("WorkspaceLoader","Delete (%s) table?")%self.tableName)==QMessageBox.Yes:
                    self.deletedSelectedTable()
        self.readUserTable()
    
    def licenseFile(self):
        self.txtLicense.clear()
        licenseDoc = LicenseDocument()
        self.txtLicense.setCurrentFont(licenseDoc.text_font())
        self.txtLicense.setText(licenseDoc.read_license_info())
        
    def configPath(self):
        try:
            pathKeys,configPath=self.tableHandler.pathSettings()
            if configPath:
                self.txtSetting.setText(configPath[pathKeys[0]])
                self.txtDefaultFolder.setText(configPath[pathKeys[1]])
                self.txtCertFolder.setText(configPath[pathKeys[2]])
                self.txtTemplates.setText(configPath[pathKeys[3]])
            else:
                userpath = self.tableHandler.userProfileDir()
                self.txtSetting.setText(userpath)
                self.setWorkingDataPath(userpath)
                self.certificatePath(userpath)
                self.templatePath()
        except: 
            pass
    
    def pathSettings(self):
        '''add the datapath to the setting'''
        dataPath={}
        settings=self.tableHandler.settingsKeys()
        userPath=[self.txtSetting.text(),self.txtDefaultFolder.text(),self.txtCertFolder.text(),self.txtTemplates.text()]
        for i in range(len(settings)):
            dataPath[settings[i]]=userPath[i]
        self.tableHandler.setProfileSettings(dataPath)
        self.tableHandler.createDir(dataPath.values())
        self.tableHandler.updateDir(self.txtSetting.text())
        
    def settingsPath(self):
        try:
            dir_name=self.openDirectoryChooser(QApplication.translate("WorkspaceLoader",\
                                                                      "Select a directory for configuration Settings",\
                                                                      str(self.txtSetting.text())))
            dirPath=dir_name[0]
            self.txtSetting.setText(dirPath)
            self.setWorkingDataPath(dirPath)
            self.certificatePath(dirPath)
            self.templatePath()
        except:
            pass
        
    def defWorkDir(self):
        dir_name=None
        try:
            dir_name=self.openDirectoryChooser(QApplication.translate("WorkspaceLoader",
                                                                      "Select a directory for STDM data",\
                                                                      str(self.txtDefaultFolder.text())))
            dirPath=dir_name[0]
            self.setWorkingDataPath(dirPath)
            self.certificatePath(dirPath)
            self.templatePath()

        except:
            pass
    
    def setWorkingDataPath(self, dir_name):
        self.txtDefaultFolder.setText(str(dir_name)+"/Data")
        
        
    def certificatePath(self,dirP):
        path = str(dirP)+"/Reports"
        self.txtCertFolder.setText(path)
        self.templatePath()
        
    def templatePath(self):
        path = self.txtCertFolder.text()
        path =path+"/Templates"
        self.txtTemplates.setText(path)
        
    def setCertificatePath(self):
        try:
            dir_name=self.openDirectoryChooser(QApplication.translate("WorkspaceLoader",
                                                                      "Select a directory for saving Reports",\
                                                                      str(self.txtCertFolder.text())))
            self.txtCertFolder.setText(str(dir_name[0]))
        except:
            pass
    
    def setTemplatesPath(self):
        try:
            dir_name=self.openDirectoryChooser(QApplication.translate("WorkspaceLoader",
                                                                      "Select a directory for saving templates",\
                                                                      str(self.txtCertFolder.text())))
            self.txtTemplates.setText(str(dir_name[0]))
        except:
            pass
        
    def openDirectoryChooser(self, message, dir=None):
        #Method to get the user selected directory
        dirDlg=QFileDialog(self,message,dir)
        dirDlg.setFileMode(QFileDialog.Directory)
        dirDlg.setOption(QFileDialog.ShowDirsOnly,True)
        if dirDlg.exec_()==QDialog.Accepted:
            selDir=dirDlg.selectedFiles()
            if len(selDir)>0:            
                return selDir  
        
    def HelpContents(self):
        normPath = self.tableHandler.setDocumentationPath() 
        os.startfile(normPath,'open')
                                        
    def ErrorInfoMessage(self, message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(QApplication.translate("WorkspaceLoader","STDM"))
        msg.setText(message)
        msg.exec_()  
                
    def InfoMessage(self, message):
        #Information message box        
        msg=QMessageBox()
        msg.setWindowTitle(unicode(self.windowTitle()))
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()  
        
    def warningInfo(self, message):
        #Information message box        
        msg=QMessageBox()
        msg.setWindowTitle(unicode(self.windowTitle()))
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setText(message)
        return msg.exec_()
        