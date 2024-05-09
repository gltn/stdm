"""
/***************************************************************************
Name                 : SupportingDocumentsWidget
Description          : Widget for managing an entity's supporting documents.
Date                 : 24/June/2016
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
from PyQt4. QtGui import (
    QPushButton,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QIcon,
    QLabel,
    QScrollArea,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget
)
from PyQt4.QtCore import (
    QDir,
    QFileInfo
)

from stdm.data.configuration.entity import (
    Entity,
    EntitySupportingDocument
)
from stdm.data.configuration import entity_model
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.ui.sourcedocument import SourceDocumentManager


class _DocumentTypeContainer(QWidget):
    """
    Container for a single document type.
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._gl = QGridLayout(self)
        self._sa = QScrollArea(self)
        self._sa.setFrameShape(QFrame.NoFrame)
        self._sa.setWidgetResizable(True)
        self._sa_content_area = QWidget()
        self._vl_ca = QVBoxLayout(self._sa_content_area)
        self._vl_ca.setSpacing(0)
        self._vl_ca.setMargin(0)
        self._doc_container = QVBoxLayout()
        self._vl_ca.addLayout(self._doc_container)
        self._sa.setWidget(self._sa_content_area)
        self._gl.addWidget(self._sa, 0, 0, 1, 1)

    @property
    def container(self):
        return self._doc_container


class SupportingDocumentsWidget(QWidget):
    """
    Widget for managing an entity's supporting documents. It enables listing
    of documents grouped by tabs depending on type.
    """
    def __init__(self, entity_supporting_document, supporting_doc_model_cls,
                 parent=None):
        """
        Class constructor.
        :param entity_supporting_document: Object containing information
        pertaining to document types, parent entity etc.
        :type entity_supporting_document: EntitySupportingDocument
        :param supporting_doc_model_cls: Class representing the data model
        corresponding to the entity supporting document object.
        :type supporting_doc_model_cls: object
        :param parent: Parent container widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)

        self._init_gui()

        self._entity_supporting_doc = entity_supporting_document

        #Container for document type widgets based on lookup id
        self._doc_type_widgets = {}

        #Init document manager
        self.source_document_manager = SourceDocumentManager(
            self._entity_supporting_doc,
            supporting_doc_model_cls,
            self
        )

        self._load_document_types()

        #Connect signals
        self._btn_add_document.clicked.connect(
            self._on_add_supporting_document
        )
        self._cbo_doc_type.currentIndexChanged.connect(
            self.on_doc_type_changed
        )
        self._doc_tab_container.currentChanged.connect(
            self.on_tab_doc_type_changed
        )

    def _init_gui(self):
        self._gl = QGridLayout(self)
        self._label = QLabel(self)
        self._label.setText(self.tr('Select document type'))
        self._gl.addWidget(self._label, 0, 0, 1, 1)
        self._cbo_doc_type = QComboBox(self)
        self._gl.addWidget(self._cbo_doc_type, 0, 1, 1, 1)
        self._btn_add_document = QPushButton(self)
        doc_ico = QIcon(':/plugins/stdm/images/icons/document.png')
        self._btn_add_document.setIcon(doc_ico)
        self._btn_add_document.setText(self.tr('Add document...'))
        self._btn_add_document.setMaximumWidth(200)
        self._gl.addWidget(self._btn_add_document, 0, 2, 1, 1)
        self._doc_tab_container = QTabWidget(self)
        self._gl.addWidget(self._doc_tab_container, 1, 0, 1, 3)

        self.setMinimumHeight(140)

    def on_doc_type_changed(self, idx):
        """
        Slot raised when the document types changes. The corresponding
        widget in the tab container is also selected.
        :param idx: Item index in the combobox.
        :type idx: int
        """
        if idx == -1:
            return

        self._doc_tab_container.setCurrentIndex(idx)

    def on_tab_doc_type_changed(self, idx):
        """
        Slot raised when the document types changes. The corresponding
        widget in the tab container is also selected.
        :param idx: Item index in the tab widget.
        :type idx: int
        """
        if idx == -1:
            return

        self._cbo_doc_type.setCurrentIndex(idx)

    def current_document_type(self):
        """
        :return: Returns the currently selected document type in the combobox.
        :rtype: str
        """
        return self._cbo_doc_type.currentText()

    def current_document_type_id(self):
        """
        :return: Returns the primary key/id of the currently selected
        document type in the combobox, else -1 if there is not current
        item in the combobox
        :rtype: int
        """
        if not self.current_document_type():
            return -1

        curr_idx = self._cbo_doc_type.currentIndex()

        return self._cbo_doc_type.itemData(curr_idx)

    def count(self):
        """
        :return: Returns the number of document types supported by this
        widget.
        :rtype: int
        """
        return self._cbo_doc_type.count()

    def document_type_containers(self):
        """
        :return: Returns a list of document container widgets for all
        registered document types.
        :rtype: list
        """
        return self.source_document_manager.containers.values()

    def document_type_widget(self, name):
        """
        Searches for the document type widget that corresponds to the given
        name.
        :param name: Name of the document type.
        :type name: str
        :return: Returns the document widget corresponding to the given type
        name.
        :rtype: QWidget
        """
        idx = self._cbo_doc_type.findText(name)

        if idx == -1:
            return None

        rec_id = self._cbo_doc_type.itemData(idx)

        return self._doc_type_widgets.get(rec_id, None)

    def _load_document_types(self):
        #Load document types in the combobox and tab widget
        vl_cls = entity_model(
            self._entity_supporting_doc.document_type_entity,
            entity_only=True
        )

        vl_obj = vl_cls()
        res = vl_obj.queryObject().all()
        for r in res:
            #Add to combo
            self._cbo_doc_type.addItem(r.value, r.id)

            #Add to tab widget
            doc_type_widget = _DocumentTypeContainer(self)
            self._doc_tab_container.addTab(doc_type_widget, r.value)
            self._doc_type_widgets[r.id] = doc_type_widget

            #Register container
            self.source_document_manager.registerContainer(
                doc_type_widget.container,
                r.id
            )

    def _on_add_supporting_document(self):
        #Slot raised when the user select to add a supporting document
        if self.count == 0:
            return

        select = self.tr('Select')
        supporting_docs_str = 'Supporting Documents'
        title = u'{0} {1} {2}'.format(
            select,
            self.current_document_type(),
            supporting_docs_str
        )

        filter_str = u'{0} (*.jpg *.jpeg *.png *.bmp *.tiff *.svg *.pdf *.mp4 *.mp4a *.mp3)'.format(
            supporting_docs_str
        )

        #Get last path for supporting documents
        last_path = last_document_path()
        if last_path is None:
            last_path = '/home'

        else:
            dir = QDir(last_path)
            if not dir.exists():
                last_path = '/home'

        source_docs = QFileDialog.getOpenFileNames(
            self, title, last_path, filter_str
        )

        doc_type_id = self._cbo_doc_type.itemData(self._cbo_doc_type.currentIndex())
        parent_entity = self._entity_supporting_doc.parent_entity

        for doc in source_docs:
            self.source_document_manager.insertDocumentFromFile(
                doc,
                doc_type_id,
                parent_entity
            )

        #Set last path
        if len(source_docs) > 0:
            doc = source_docs[0]
            fi = QFileInfo(doc)
            dir_path = fi.absolutePath()
            set_last_document_path(dir_path)

