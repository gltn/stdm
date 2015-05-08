"""
/***************************************************************************
Name                 : Template Document Selector
Description          : Dialog for selecting a document template from the 
                       saved list.
Date                 : 14/May/2014 
copyright            : (C) 2014 by John Gitau
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
from PyQt4.QtGui import (
                         QDialog,
                         QDialogButtonBox,
                         QStandardItemModel,
                         QStandardItem,
                         QIcon,
                         QPixmap,
                         QApplication,
                         QIcon,
                         QInputDialog,
                         QMessageBox
                         )

from PyQt4.QtCore import (
                          QFile,
                          QIODevice
                          )

from PyQt4.QtXml import QDomDocument

from stdm.utils import documentTemplates
from stdm.settings import RegistryConfig
from stdm import resources_rc
from notification import (
                             NotificationBar,
                             ERROR
                             )

from .ui_composer_doc_selector import Ui_frmDocumentSelector

class TemplateDocumentSelector(QDialog,Ui_frmDocumentSelector):
    """
    Dialog for selecting a document template from the saved list.
    """
    def __init__(self,parent = None,selectMode=True):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        self.notifBar = NotificationBar(self.vlNotification)
        
        if selectMode:
            self.buttonBox.setVisible(True)
            self.manageButtonBox.setVisible(False)
            currHeight = self.size().height()
            self.resize(200,currHeight)
            
        else:
            self.buttonBox.setVisible(False)
            self.manageButtonBox.setVisible(True)
            self.setWindowTitle(QApplication.translate("TemplateDocumentSelector","Template Manager"))
            
        #Configure manage buttons
        btnEdit = self.manageButtonBox.button(QDialogButtonBox.Ok)
        btnEdit.setText(QApplication.translate("TemplateDocumentSelector","Edit..."))
        btnEdit.setIcon(QIcon(":/plugins/stdm/images/icons/edit.png"))
        
        btnDelete = self.manageButtonBox.button(QDialogButtonBox.Save)
        btnDelete.setText(QApplication.translate("TemplateDocumentSelector","Delete"))
        btnDelete.setIcon(QIcon(":/plugins/stdm/images/icons/delete.png"))
        
        #Connect signals
        self.buttonBox.accepted.connect(self.onAccept)
        btnEdit.clicked.connect(self.onEditTemplate)
        btnDelete.clicked.connect(self.onDeleteTemplate)
        
        #Get saved document templates then add to the model
        templates = documentTemplates()

        self._docItemModel = QStandardItemModel(parent)
        self._docItemModel.setColumnCount(2)
        
        for name,path in templates.iteritems():
            docNameItem =  self._createDocNameItem(name)
            filePathItem = QStandardItem(path)
            self._docItemModel.appendRow([docNameItem,filePathItem])
            
        self.lstDocs.setModel(self._docItemModel)
        
    def _createDocNameItem(self,docName):
        """
        Create a template document standard item.
        """
        #Set icon
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plugins/stdm/images/icons/document.png"), QIcon.Normal, QIcon.Off)
        
        dnItem = QStandardItem(icon,docName)
        
        return dnItem
    
    def onEditTemplate(self):
        """
        Slot raised to edit document template.
        """
        self.notifBar.clear()
        
        if self.documentMapping() == None:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Please select a document template to edit"))
            return
        
        templateName,filePath = self.documentMapping()
        
        docName,ok = QInputDialog.getText(self, \
                                              QApplication.translate("TemplateDocumentSelector","Edit Template"), \
                                              QApplication.translate("TemplateDocumentSelector","Please enter the new template name below"), \
                                              text = templateName)
        if ok and docName == "":
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Template name cannot be empty"))
            return
        
        elif docName == templateName:
            return
        
        elif ok and docName != "":
            result,newTemplatePath = self._editTemplate(filePath, docName)
            
            if result:
                #Update view
                mIndices = self._selectedMappings()
        
                docNameItem = self._docItemModel.itemFromIndex(mIndices[0])
                filePathItem = self._docItemModel.itemFromIndex(mIndices[1])
                
                docNameItem.setText(docName)
                filePathItem.setText(newTemplatePath)
                
                self.notifBar.insertInfoNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "'%s' template has been successfully updated")%docName)
                
            else:
                self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Error: '%s' template could not be updated")%templateName)
            
    def onDeleteTemplate(self):
        """
        Slot raised to delete document template.
        """
        self.notifBar.clear()
        
        if self.documentMapping() == None:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Please select a document template to delete"))
            return
        
        templateName,filePath = self.documentMapping()
        
        result = QMessageBox.warning(self, QApplication.translate("TemplateDocumentSelector", \
                                                                         "Confirm delete"), 
                                     QApplication.translate("TemplateDocumentSelector", \
                                                                         "Are you sure you want to delete '%s' template?" \
                                                                         "This action cannot be undone.\nClick Yes to proceed " \
                                                                         "or No to cancel.")%(templateName),
                                     QMessageBox.Yes|QMessageBox.No)
        
        if result == QMessageBox.No:
            return
        
        status = self._deleteDocument(filePath)
        
        if status:
            #Remove item from list using model index row number
            selectedDocNameIndices = self.lstDocs.selectionModel().selectedRows(0)
            row = selectedDocNameIndices[0].row()
            self._docItemModel.removeRow(row)
            self.notifBar.insertInfoNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "'%s' template has been successfully removed")%templateName)
        
        else:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Error: '%s' template could not be removed")%templateName)
    
    def onAccept(self):
        """
        Slot raised to close the dialog only when a selection has been made by the user.
        """
        self.notifBar.clear()
        
        if self.documentMapping() == None:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Please select a document"))
            return
        
        self.accept()
        
    def _selectedMappings(self):
        """
        Returns the model indices for the selected row.
        """
        selectedDocNameIndices = self.lstDocs.selectionModel().selectedRows(0)
        selectedFilePathIndices = self.lstDocs.selectionModel().selectedRows(1)
        
        if len(selectedDocNameIndices) == 0:
            return None
        
        docNameIndex = selectedDocNameIndices[0]
        filePathIndex = selectedFilePathIndices[0]
        
        return (docNameIndex,filePathIndex)
    
    def documentMapping(self):
        """
        Returns a tuple containing the selected document name and the corresponding file name.
        """
        mIndices = self._selectedMappings()
        
        if mIndices == None:
            return None
        
        docNameItem = self._docItemModel.itemFromIndex(mIndices[0])
        filePathItem = self._docItemModel.itemFromIndex(mIndices[1])
        
        return (docNameItem.text(),filePathItem.text())
    
    def _editTemplate(self,templatePath,newName):
        """
        Updates the template document to use the new name.
        """
        templateFile = QFile(templatePath)
        
        if not templateFile.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector","Open Operation Error"), \
                                            "{0}\n{1}".format(QApplication.translate("TemplateDocumentSelector","Cannot read template file."), \
                                                      templateFile.errorString()
                                                      ))
            return (False,"")
         
        templateDoc = QDomDocument()
        
        if templateDoc.setContent(templateFile):
            composerElement = templateDoc.documentElement()
            titleAttr = composerElement.attributeNode("title")
            if not titleAttr.isNull():
                titleAttr.setValue(newName)
                
            #Try remove file
            status = templateFile.remove()
            
            if not status:
                return (False,"")
            
            #Create new file
            newTemplatePath = self._composerTemplatesPath() + "/" + newName + ".sdt"  
            newTemplateFile = QFile(newTemplatePath)
            
            if not newTemplateFile.open(QIODevice.WriteOnly):
                QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector","Save Operation Error"), \
                                                "{0}\n{1}".format(QApplication.translate("TemplateDocumentSelector","Could not save template file."), \
                                                          newTemplateFile.errorString()
                                                          ))
                return (False,"")
            
            if newTemplateFile.write(templateDoc.toByteArray()) == -1:
                QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector","Save Error"), \
                                                QApplication.translate("TemplateDocumentSelector","Could not save template file."))
                return (False,"")
            
            newTemplateFile.close()  
            
            return (True,newTemplatePath)
    
    def _deleteDocument(self,templatePath):
        """
        Delete the document template from the file system.
        """
        docFile = QFile(templatePath)
        
        return docFile.remove()
    
    def _composerTemplatesPath(self):
        """
        Reads the path of composer templates in the registry.
        """
        regConfig = RegistryConfig()
        keyName = "ComposerTemplates"
        
        valueCollection = regConfig.read([keyName])
        
        if len(valueCollection) == 0:
            return None
        
        else:
            return valueCollection[keyName]
        