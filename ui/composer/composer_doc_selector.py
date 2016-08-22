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

from stdm.utils.util import documentTemplates
from stdm.composer.composer_data_source import composer_data_source
from stdm.settings.registryconfig import RegistryConfig
from ..notification import (
                             NotificationBar,
                             ERROR
                             )

from .ui_composer_doc_selector import Ui_frmDocumentSelector

class TemplateDocumentSelector(QDialog,Ui_frmDocumentSelector):
    """
    Dialog for selecting a document template from the saved list.
    """
    def __init__(self,parent = None,selectMode=True, filter_data_source=''):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        self.notifBar = NotificationBar(self.vlNotification)

        self._mode = selectMode

        #Filter templates by the specified table name
        self._filter_data_source = filter_data_source
        
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
            if self._template_contains_filter_table(path):
                docNameItem =  self._createDocNameItem(name)
                filePathItem = QStandardItem(path)
                self._docItemModel.appendRow([docNameItem,filePathItem])
            
        self.lstDocs.setModel(self._docItemModel)

    def _template_contains_filter_table(self, path):
        #Returns true if the template refers to the filter data source
        if not self._filter_data_source:
            return True

        data_source = composer_data_source(path)
        if data_source is None:
            return False

        referenced_table = data_source.referenced_table_name
        if referenced_table == self._filter_data_source:
            return True

        return False

    @property
    def mode(self):
        return self._mode

    @property
    def filter_data_source(self):
        return self._filter_data_source
        
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
                
                self.notifBar.insertSuccessNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "'{0}' template has been successfully updated".format(docName)))
                
            else:
                self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Error: '{0}' template could not be updated".format(templateName)))
            
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
                                                                         "Are you sure you want to delete '{0}' template?" \
                                                                         "This action cannot be undone.\nClick Yes to proceed " \
                                                                         "or No to cancel.".format(templateName)), 
                                     QMessageBox.Yes|QMessageBox.No)
        
        if result == QMessageBox.No:
            return
        
        status = self._deleteDocument(filePath)
        
        if status:
            #Remove item from list using model index row number
            selectedDocNameIndices = self.lstDocs.selectionModel().selectedRows(0)
            row = selectedDocNameIndices[0].row()
            self._docItemModel.removeRow(row)
            self.notifBar.insertSuccessNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "'{0}' template has been successfully removed".format(templateName)))
        
        else:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Error: '{0}' template could not be removed".format(templateName)))
    
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
            titleAttr = composerElement.attributeNode("_title")
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
