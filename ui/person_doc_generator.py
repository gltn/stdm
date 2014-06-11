"""
/***************************************************************************
Name                 : Document Generator By Person
Description          : Dialog that enables a user to generate documents by 
                       using person information.
Date                 : 21/May/2014 
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
                         QApplication,
                         QProgressDialog,
                         QMessageBox,
                         QImageWriter,
                         QFileDialog
                         )
from PyQt4.QtCore import (
                          Qt,
                          QDir,
                          QFileInfo
                          )

from stdm.data import (
                       Farmer,
                       genderFormatter,
                       maritalStatusFormatter
                       )
from stdm.composer import DocumentGenerator

from .notification import NotificationBar
from .entity_browser import FarmerEntitySelector
from .ui_person_doc_generator import Ui_frmPersonDocGenerator
from .composer_doc_selector import TemplateDocumentSelector
from .stdmdialog import  declareMapping

__all__ = ["PersonDocumentGenerator"]

class PersonDocumentGenerator(QDialog,Ui_frmPersonDocGenerator):
    """
    Dialog that enables a user to generate documents by using person information.
    """
    def __init__(self,iface,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        #Class vars
        self._iface = iface
        self._docTemplatePath = ""
        self._outputFilePath = ""
        
        self._notifBar = NotificationBar(self.vlNotification)
        
        mapping=declareMapping.instance()
        self._dbModel=mapping.tableMapping('party')
        
        #Initialize person foreign key mapper
        self.personFKMapper = self.tabWidget.widget(0)
        self.personFKMapper.setDatabaseModel(self._dbModel)
        self.personFKMapper.setEntitySelector(FarmerEntitySelector)
        self.personFKMapper.setSupportsList(True)
        self.personFKMapper.setDeleteonRemove(False)
        '''
        self.personFKMapper.addCellFormatter("GenderID",genderFormatter)
        self.personFKMapper.addCellFormatter("MaritalStatusID",maritalStatusFormatter)
        '''
        self.personFKMapper.setNotificationBar(self._notifBar)
        self.personFKMapper.initialize()
        
        #Configure person model attribute view
        
        # QMessageBox.information(None,"test",str(self._dbModel.displayMapping()))
        #tableMapping=self.mapping.displayMapping('party')
        
        
        self.lstDocNaming.setDataModel(self._dbModel)
        #self.lstDocNaming.setModelDisplayMapping(tableMapping)
        self.lstDocNaming.load()
        
        #Configure generate button
        generateBtn = self.buttonBox.button(QDialogButtonBox.Ok)
        if generateBtn != None:
            generateBtn.setText(QApplication.translate("PersonDocumentGenerator","Generate"))
        
        #Load supported image types
        supportedImageTypes = QImageWriter.supportedImageFormats()
        for imageType in supportedImageTypes:
            imageTypeStr = imageType.data()
            self.cboImageType.addItem(imageTypeStr)
        
        #Connect signals
        self.btnSelectTemplate.clicked.connect(self.onSelectTemplate)
        self.buttonBox.accepted.connect(self.onGenerate)
        self.chkUseOutputFolder.stateChanged.connect(self.onToggledOutputFolder)
        self.rbExpImage.toggled.connect(self.onToggleExportImage)
            
    def onSelectTemplate(self):
        """
        Slot raised to load the template selector dialog.
        """
        templateSelector = TemplateDocumentSelector(self)
        if templateSelector.exec_() == QDialog.Accepted:
            docName,docPath = templateSelector.documentMapping()
            
            self.lblTemplateName.setText(docName)
            self._docTemplatePath = docPath
            
    def onToggledOutputFolder(self,state):
        """
        Slot raised to enable/disable the generated output documents to be 
        written to the plugin composer output folder using the specified
        naming convention.
        """
        if state == Qt.Checked:
            self.gbDocNaming.setEnabled(True)
            
        elif state == Qt.Unchecked:
            self.gbDocNaming.setEnabled(False)
            
    def reset(self):
        """
        Clears/resets the dialog from user-defined options.
        """
        self._docTemplatePath = ""
        self.lblTemplateName.setText("")
        self.personFKMapper.initialize()
        self.lstDocNaming.load()
        if self.cboImageType.count() > 0:
            self.cboImageType.setCurrentIndex(0)
        
    def onToggleExportImage(self,state):
        """
        Slot raised to enable/disable the image formats combobox
        """
        if state:
            self.cboImageType.setEnabled(True)
        else:
            self.cboImageType.setEnabled(False)
        
    def onGenerate(self):
        """
        Slot raised to initiate the certificate generation process.
        """
        self._notifBar.clear()
        
        #Validate records
        records = self.personFKMapper.entities()
        if records == None:
            self._notifBar.insertErrorNotification(QApplication.translate("PersonDocumentGenerator", \
                                                                          "Please select at least one person record"))
            return
        
        if self._docTemplatePath == "":
            self._notifBar.insertErrorNotification(QApplication.translate("PersonDocumentGenerator", \
                                                                          "Please select a document template to use"))
            return
        
        documentNamingAttrs = self.lstDocNaming.selectedMappings()
        
        if self.chkUseOutputFolder.checkState() == Qt.Checked and len(documentNamingAttrs) == 0:
            self._notifBar.insertErrorNotification(QApplication.translate("PersonDocumentGenerator", \
                                                                          "Please select at least one field for naming the output document."))
            return
        
        #Set output file properties
        if self.rbExpImage.isChecked():
            outputMode = DocumentGenerator.Image
            fileExtension = self.cboImageType.currentText()
            saveAsText = "Image File"
        else:
            outputMode = DocumentGenerator.PDF 
            fileExtension = "pdf"
            saveAsText = "PDF File"
            
        #Show save file dialog if not using output folder
        if self.chkUseOutputFolder.checkState() == Qt.Unchecked:
            docDir = ""
            
            if self._outputFilePath != "":
                fileInfo = QFileInfo(self._outputFilePath)
                docDir = fileInfo.dir().path()
                
            self._outputFilePath = QFileDialog.getSaveFileName(self,QApplication.translate("PersonDocumentGenerator", \
                                                                          "Save Document"), \
                                                               docDir, \
                                                               "{0} (*.{1})".format(QApplication.translate("PersonDocumentGenerator", \
                                                                          saveAsText), \
                                                                                   fileExtension))
            
            if self._outputFilePath == "":
                self._notifBar.insertErrorNotification(QApplication.translate("PersonDocumentGenerator", \
                                                                          "Process aborted. No output file was specified."))
                return
            
            #Include extension in file name
            self._outputFilePath = self._outputFilePath #+ "." + fileExtension
            
        else:
            #Multiple files to be generated.
            pass
                
        docGenerator = DocumentGenerator(self._iface,self)
        #Apply cell formatters for naming output files
        docGenerator.setAttrValueFormatters(self.personFKMapper.cellFormatters())
        entityFieldName = "id"
        
        #Iterate through the selected records
        progressDlg = QProgressDialog(self)
        progressDlg.setMaximum(len(records))
        
        for i,record in enumerate(records):
            progressDlg.setValue(i)
            
            if progressDlg.wasCanceled():
                break
            
            #User-defined location
            if self.chkUseOutputFolder.checkState() == Qt.Unchecked:
                status,msg = docGenerator.run(self._docTemplatePath,entityFieldName,record.id,outputMode, \
                                                          filePath = self._outputFilePath)
            
            #Output folder location using custom naming  
            
            else:
                status,msg = docGenerator.run(self._docTemplatePath,entityFieldName,record.id,outputMode, \
                                                          dataFields = documentNamingAttrs,fileExtension = fileExtension, \
                                                          dbmodel = self._dbModel)
            
            if not status:
                result = QMessageBox.warning(self, QApplication.translate("PersonDocumentGenerator","Document Generate Error"), 
                                             msg, 
                                             QMessageBox.Ignore|QMessageBox.Abort)
                
                if result == QMessageBox.Abort:
                    progressDlg.close()
                    return
                
            else:
                progressDlg.setValue(len(records))
                
                QMessageBox.information(self, 
                                    QApplication.translate("PersonDocumentGenerator","Document Generation Complete"), 
                                    QApplication.translate("PersonDocumentGenerator","Document generation has successfully completed.")
                                    )
        
        #Reset UI
        self.reset()
