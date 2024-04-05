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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QFile,
    QIODevice
)
from qgis.PyQt.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QIcon,
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QApplication,
    QInputDialog,
    QMessageBox
)
from qgis.PyQt.QtXml import QDomDocument

from stdm.composer.document_template import DocumentTemplate
from stdm.settings import current_profile
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import (
    NotificationBar
)
from stdm.utils.util import documentTemplates, user_non_profile_views

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_doc_selector.ui'))


class TemplateDocumentSelector(WIDGET, BASE):
    """
    Dialog for selecting a document template from the saved list.
    """

    def __init__(self, parent=None, selectMode=True, filter_data_source='', access_templates=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.notifBar = NotificationBar(self.vlNotification)

        self._mode = selectMode

        # Filter templates by the specified table name
        self._filter_data_source = filter_data_source

        # Document templates in current profile
        self._profile_templates = []

        self._current_profile = current_profile()

        # Load current profile templates
        self._load_current_profile_templates()

        self.access_templates = access_templates or []

        if selectMode:
            self.buttonBox.setVisible(True)
            self.manageButtonBox.setVisible(False)
            currHeight = self.size().height()
            self.resize(200, currHeight)

        else:
            self.buttonBox.setVisible(False)
            self.manageButtonBox.setVisible(True)
            self.setWindowTitle(
                QApplication.translate(
                    "TemplateDocumentSelector",
                    "Template Manager"
                )
            )

        # Configure manage buttons
        btnEdit = self.manageButtonBox.button(QDialogButtonBox.Ok)
        btnEdit.setText(QApplication.translate("TemplateDocumentSelector", "Edit..."))
        btnEdit.setIcon(GuiUtils.get_icon("edit.png"))

        btnDelete = self.manageButtonBox.button(QDialogButtonBox.Save)
        btnDelete.setText(QApplication.translate("TemplateDocumentSelector", "Delete"))
        btnDelete.setIcon(GuiUtils.get_icon("delete.png"))

        # Connect signals
        self.buttonBox.accepted.connect(self.onAccept)
        btnEdit.clicked.connect(self.onEditTemplate)
        btnDelete.clicked.connect(self.onDeleteTemplate)

        # Get saved document templates then add to the model
        templates = documentTemplates()

        self._docItemModel = QStandardItemModel(parent)
        self._docItemModel.setColumnCount(2)

        # Append current profile templates to the model.
        for dt in self._profile_templates:

            if self._template_contains_filter_table(dt):  # and dt.name in self.access_templates:
                doc_name_item = self._createDocNameItem(dt.name)
                file_path_item = QStandardItem(dt.path)
                self._docItemModel.appendRow([doc_name_item, file_path_item])

        self.lstDocs.setModel(self._docItemModel)
        self.lstDocs.doubleClicked.connect(self.select_template)

    def select_template(self, model_index):
        self.onAccept()

    def _load_current_profile_templates(self):
        # Loads only those templates that refer to tables in the current
        # profile.
        if self._current_profile is None:
            return

        # Get saved document templates then add to the model
        templates = documentTemplates()

        profile_tables = self._current_profile.table_names()

        # Get templates for the current profile
        for name, path in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, path)
            
            if doc_temp.data_source is None:
                continue

            # Assert data source is in the current profile
            if doc_temp.data_source.referenced_table_name in profile_tables or \
                    doc_temp.data_source.name() in user_non_profile_views():
                self._add_doc_temp(doc_temp)
                # self._profile_templates.append(doc_temp)

    def _add_doc_temp(self, doc_temp):
        found = False
        for template in self._profile_templates:
            if template.name == doc_temp.name:
                found = True
                break

        if not found:
            self._profile_templates.append(doc_temp)

    def _template_contains_filter_table(self, document_template):
        # Returns true if the template refers to the filter data source

        # If no filter data source defined then always return True

        if document_template.data_source.name() in user_non_profile_views():
            return True

        if not self._filter_data_source:
            return True

        referenced_table = document_template.referenced_table_name

        if referenced_table == self._filter_data_source:
            return True

        return False

    @property
    def mode(self):
        return self._mode

    @property
    def filter_data_source(self):
        return self._filter_data_source

    def _createDocNameItem(self, docName):
        """
        Create a template document standard item.
        """
        # Set icon
        icon = QIcon()
        icon.addPixmap(
            GuiUtils.get_icon_pixmap(
                "document.png"
            ),
            QIcon.Normal,
            QIcon.Off
        )

        dnItem = QStandardItem(icon, docName)

        return dnItem

    def onEditTemplate(self):
        """
        Slot raised to edit document template.
        """
        self.notifBar.clear()

        if self.documentMapping() is None:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Please select a document template to edit"))
            return

        templateName, filePath = self.documentMapping()

        docName, ok = QInputDialog.getText(self, \
                                           QApplication.translate("TemplateDocumentSelector", "Edit Template"), \
                                           QApplication.translate("TemplateDocumentSelector",
                                                                  "Please enter the new template name below"), \
                                           text=templateName)
        if ok and docName == "":
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Template name cannot be empty"))
            return

        elif docName == templateName:
            return

        elif ok and docName != "":
            result, newTemplatePath = self._editTemplate(filePath, docName)

            if result:
                # Update view
                mIndices = self._selectedMappings()

                docNameItem = self._docItemModel.itemFromIndex(mIndices[0])
                filePathItem = self._docItemModel.itemFromIndex(mIndices[1])

                docNameItem.setText(docName)
                filePathItem.setText(newTemplatePath)

                self.notifBar.insertSuccessNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                               "'{0}' template has been successfully updated".format(
                                                                                   docName)))

            else:
                self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                             "Error: '{0}' template could not be updated".format(
                                                                                 templateName)))

    def onDeleteTemplate(self):
        """
        Slot raised to delete document template.
        """
        self.notifBar.clear()

        if self.documentMapping() == None:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Please select a document template to delete"))
            return

        templateName, filePath = self.documentMapping()

        result = QMessageBox.warning(self, QApplication.translate("TemplateDocumentSelector", \
                                                                  "Confirm delete"),
                                     QApplication.translate("TemplateDocumentSelector", \
                                                            "Are you sure you want to delete '{0}' template?" \
                                                            "This action cannot be undone.\nClick Yes to proceed " \
                                                            "or No to cancel.".format(templateName)),
                                     QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.No:
            return

        status = self._deleteDocument(filePath)

        if status:
            # Remove item from list using model index row number
            selectedDocNameIndices = self.lstDocs.selectionModel().selectedRows(0)
            row = selectedDocNameIndices[0].row()
            self._docItemModel.removeRow(row)
            self.notifBar.insertSuccessNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                           "'{0}' template has been successfully removed".format(
                                                                               templateName)))

        else:
            self.notifBar.insertErrorNotification(QApplication.translate("TemplateDocumentSelector", \
                                                                         "Error: '{0}' template could not be removed".format(
                                                                             templateName)))

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

        return (docNameIndex, filePathIndex)

    def documentMapping(self):
        """
        Returns a tuple containing the selected document name and the corresponding file name.
        """
        mIndices = self._selectedMappings()

        if mIndices == None:
            return None

        docNameItem = self._docItemModel.itemFromIndex(mIndices[0])
        filePathItem = self._docItemModel.itemFromIndex(mIndices[1])

        return (docNameItem.text(), filePathItem.text())

    def _editTemplate(self, templatePath, newName):
        """
        Updates the template document to use the new name.
        """
        templateFile = QFile(templatePath)

        if not templateFile.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector", "Open Operation Error"), \
                                 "{0}\n{1}".format(
                                     QApplication.translate("TemplateDocumentSelector", "Cannot read template file."), \
                                     templateFile.errorString()
                                 ))
            return (False, "")

        templateDoc = QDomDocument()

        if templateDoc.setContent(templateFile):
            composerElement = templateDoc.documentElement()
            titleAttr = composerElement.attributeNode("_title")
            if not titleAttr.isNull():
                titleAttr.setValue(newName)

            # Try remove file
            status = templateFile.remove()

            if not status:
                return (False, "")

            # Create new file
            newTemplatePath = self._composerTemplatesPath() + "/" + newName + ".sdt"
            newTemplateFile = QFile(newTemplatePath)

            if not newTemplateFile.open(QIODevice.WriteOnly):
                QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector", "Save Operation Error"), \
                                     "{0}\n{1}".format(QApplication.translate("TemplateDocumentSelector",
                                                                              "Could not save template file."), \
                                                       newTemplateFile.errorString()
                                                       ))
                return (False, "")

            if newTemplateFile.write(templateDoc.toByteArray()) == -1:
                QMessageBox.critical(self, QApplication.translate("TemplateDocumentSelector", "Save Error"), \
                                     QApplication.translate("TemplateDocumentSelector",
                                                            "Could not save template file."))
                return (False, "")

            newTemplateFile.close()

            return (True, newTemplatePath)

    def _deleteDocument(self, templatePath):
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
