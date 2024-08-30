"""
/***************************************************************************
Name                 : Source Document Translator Dialog
Description          : Dialog for defining configuration settings for the
                       SourceDocumentTranslator implementation.
Date                 : 17/August/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
    QDir
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox
)

from stdm.data.configuration import entity_model
from stdm.data.importexport.value_translators import SourceDocumentTranslator
from stdm.settings.registryconfig import (
    last_document_path
)
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.importexport.translator_widget_base import TranslatorDialogBase
from stdm.ui.notification import NotificationBar

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('importexport/ui_source_document_dialog.ui'))


class SourceDocumentTranslatorDialog(TranslatorDialogBase, WIDGET, BASE):
    """
    Dialog for defining configuration settings for the
    SourceDocumentTranslator implementation.
    """

    def __init__(self, parent, source_cols, dest_table, 
                 dest_col, src_col):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.btn_source_doc_folder.setIcon(GuiUtils.get_icon('open_file.png'))

        TranslatorDialogBase.__init__(
            self,
            source_cols,
            dest_table,
            dest_col,
            src_col)
        

        self._notif_bar = NotificationBar(self.vlNotification)

        # Assert if the entity supports documents
        self._assert_entity_supports_documents()

        # Set the source document directory
        self.source_document_directory = None

        # Document type name
        self._document_type_name = self._dest_col

        # Document type ID
        self._document_type_id = None

        # Set document type ID
        self._set_document_type_id()

        # Connect slots
        self.btn_source_doc_folder.clicked.connect(
            self._load_source_document_directory_selector
        )

    @property
    def document_type_id(self):
        """
        :return: Returns source document type id. Otherwise None if not set.
        :rtype: int
        """
        return self._document_type_id

    @property
    def document_type(self):
        """
        :return: Returns the name of the selected document type.
        :rtype: str
        """
        return self._document_type_name

    @property
    def documents_directory(self):
        """
        :return: Returns the specified root directory for supporting
        documents. Otherwise None if not specified by the user.
        :rtype: str
        """
        return self.txtRootFolder.text()

    def _assert_entity_supports_documents(self):
        # Check if the entity supports documents and close automatically if not.
        entity = self.entity()

        if entity is None:
            msg = self.tr('Invalid table object')

            raise RuntimeError(msg)

        if not entity.supports_documents:
            msg = self.tr('The selected destination table does not support '
                          'documents.\nHence, this translator is not '
                          'applicable.')

            raise RuntimeError(msg)

    def _set_document_type_id(self):
        # Load document id based on the name
        entity = self.entity()

        if entity is None:
            return

        vl_cls = entity_model(
            entity.supporting_doc.document_type_entity,
            entity_only=True
        )

        vl_obj = vl_cls()
        res = vl_obj.queryObject().all()
        for r in res:
            if r.value == self._dest_col:
                self._document_type_id = r.id

                break

        if not entity.supports_documents:
            msg = self.tr('The selected column does not correspond to a '
                          'document type.\nHence, this translator is not '
                          'applicable.')
            title = self.tr('Invalid Document Type')
            QMessageBox.critical(self, title, msg)

            # Close dialog
            self.reject()

    def _load_source_document_directory_selector(self):
        # Load file dialog for selecting source documents directory
        title = self.tr('Select Source Document Directory')
        def_path = self.txtRootFolder.text()

        # Use the last set source document directory
        if not def_path:
            def_path = last_document_path()

        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = QDir.fromNativeSeparators(sel_doc_path)
            self.txtRootFolder.clear()
            self.txtRootFolder.setText(normalized_path)

    def value_translator(self):
        source_doc_translator = SourceDocumentTranslator()
        source_doc_translator.set_referencing_table(self._dest_table)
        source_doc_translator.set_referencing_column(self._dest_col)

        # Just use the source column for getting the relative image path
        # and name
        source_doc_translator.add_source_reference_column(
            self._src_col,
            self._dest_col
        )
        source_doc_translator.entity = self.entity()
        source_doc_translator._document_type_id = self._document_type_id
        source_doc_translator._document_type = self._document_type_name
        source_doc_translator._source_directory = self.documents_directory

        return source_doc_translator

    def validate(self):
        """
        :return: Return True if the source document directory exists,
        otherwise False.
        :rtype: bool
        """
        source_doc_path = self.txtRootFolder.text()

        # Clear previous notifications
        self._notif_bar.clear()

        if not source_doc_path:
            msg = self.tr(
                'Please set the root directory of source documents.'
            )
            self._notif_bar.insertErrorNotification(msg)

            return False

        dir = QDir()

        if not dir.exists(source_doc_path):
            msg = self.tr("'{0}' directory does not exist.".format(
                source_doc_path))
            self._notif_bar.insertErrorNotification(msg)

            return False

        return True

    def accept(self):
        """
        Validate before accepting user input.
        """
        if self.validate():
            super(SourceDocumentTranslatorDialog, self).accept()
