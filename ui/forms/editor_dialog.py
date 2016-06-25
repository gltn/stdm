"""
/***************************************************************************
Name                 : EntityEditorDialog
Description          : Creates an editor dialog for an entity object.
Date                 : 8/June/2016
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
from PyQt4.QtCore import (
    Qt
)
from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget
)

from stdm.data.configuration import entity_model
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import table_column_names
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    UserTipLabel
)
from stdm.ui.forms.documents import SupportingDocumentsWidget
from stdm.ui.notification import NotificationBar

class EntityEditorDialog(QDialog, MapperMixin):
    """
    Dialog for editing entity attributes.
    """
    def __init__(self, entity, model=None, parent=None, manage_documents=True):
        """
        Class constructor.
        :param entity: Entity object corresponding to a table object.
        :type entity: Entity
        :param model: Data object for loading data into the form widgets.
        If the model is set, then the editor dialog is assumed to be in edit
        mode.
        :type model: object
        :param parent: Parent widget that the form belongs to.
        :type parent: QWidget
        :param manage_documents: True if the dialog should provide controls
        for managing supporting documents. Only applicable if the entity
        allows for supporting documents to be attached.
        :type manage_documents: bool
        """
        QDialog.__init__(self, parent)

        #Set minimum width
        self.setMinimumWidth(350)

        #Flag for mandatory columns
        self.has_mandatory = False

        self._entity = entity

        #Set notification layout bar
        self.vlNotification = QVBoxLayout()
        self.vlNotification.setObjectName('vlNotification')
        self._notifBar = NotificationBar(self.vlNotification)

        #Set manage documents only if the entity supports documents
        if self._entity.supports_documents:
            self._manage_documents = manage_documents

        else:
            self._manage_documents = False

        #Setup entity model
        self._ent_document_model = None
        if self._entity.supports_documents:
                ent_model, self._ent_document_model = entity_model(
                    self._entity,
                    with_supporting_document=True
                )
        else:
            ent_model = entity_model(self._entity)

        if not model is None:
            ent_model = model

        MapperMixin.__init__(self, ent_model)

        #Initialize UI setup
        self._init_gui()

        #Set title
        editor_trans = self.tr('Editor')
        title = u'{0} {1}'.format(self._entity.short_name, editor_trans)
        self.setWindowTitle(title)

    def _init_gui(self):
        #Setup base elements
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName('glMain')
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 1)

        #Set column widget area
        column_widget_area = self._setup_columns_content_area()
        self.gridLayout.addWidget(column_widget_area, 1, 0, 1, 1)

        #Add notification for mandatory columns if applicable
        next_row = 2
        if self.has_mandatory:
            self.required_fields_lbl = QLabel(self)
            msg = self.tr('Please fill out all required (*) fields.')
            msg = self._highlight_asterisk(msg)
            self.required_fields_lbl.setText(msg)
            self.gridLayout.addWidget(self.required_fields_lbl, next_row, 0, 1, 2)

            #Bump up row reference
            next_row += 1

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.buttonBox.setObjectName('buttonBox')
        self.gridLayout.addWidget(self.buttonBox, next_row, 0, 1, 1)

        #Connect to MapperMixin slots
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
    def _setup_columns_content_area(self):
        #Only use this if entity supports documents
        self.entity_tab_widget = None

        self.entity_scroll_area = QScrollArea(self)
        self.entity_scroll_area.setFrameShape(QFrame.NoFrame)
        self.entity_scroll_area.setWidgetResizable(True)
        self.entity_scroll_area.setObjectName('scrollArea')
        self.scroll_widget_contents = QWidget()
        self.scroll_widget_contents.setObjectName('scrollAreaWidgetContents')
    
        #Grid layout for controls
        self.gl = QGridLayout(self.scroll_widget_contents)
        self.gl.setObjectName('gl_widget_contents')
    
        #Append column labels and widgets
        table_name = self._entity.name
        columns = table_column_names(table_name)
        #Iterate entity column and assert if they exist
        row_id = 0
        for c in self._entity.columns.values():
            if not c.name in columns and not isinstance(c, VirtualColumn):
                continue
    
            #Get widget factory
            column_widget = ColumnWidgetRegistry.create(
                c,
                self.scroll_widget_contents
            )
            if not column_widget is None:
                header = c.header()
                self.c_label = QLabel(self.scroll_widget_contents)

                #Format label text if it is a mandatory field
                if c.mandatory:
                    header = '{0} *'.format(c.header())
                    #Highlight asterisk
                    header = self._highlight_asterisk(header)

                self.c_label.setText(header)
                self.gl.addWidget(self.c_label, row_id, 0, 1, 1)

                self.column_widget = column_widget
                self.gl.addWidget(self.column_widget, row_id, 1, 1, 1)

                #Add user tip if specified for the column configuration
                if c.user_tip:
                    self.tip_lbl = UserTipLabel(user_tip=c.user_tip)
                    self.gl.addWidget(self.tip_lbl, row_id, 2, 1, 1)

                if c.mandatory and not self.has_mandatory:
                    self.has_mandatory = True

                col_name = c.name
                #Replace name accordingly based on column type
                if isinstance(c, MultipleSelectColumn):
                    col_name = c.model_attribute_name
    
                #Add widget to MapperMixin collection
                self.addMapping(
                    col_name,
                    self.column_widget,
                    c.mandatory,
                    pseudoname=c.header()
                )
    
                #Bump up row_id
                row_id += 1
    
        self.entity_scroll_area.setWidget(self.scroll_widget_contents)

        #Add tab widget if entity supports documents
        if self._entity.supports_documents:
            self.doc_widget = SupportingDocumentsWidget(
                self._entity.supporting_doc,
                self._ent_document_model,
                self
            )
            self.entity_tab_widget = QTabWidget(self)

            #Add attribute tab
            self.entity_tab_widget.addTab(
                self.entity_scroll_area,
                self.tr('Primary')
            )

            #Add supporting documents tab
            self.entity_tab_widget.addTab(
                self.doc_widget,
                self.tr('Supporting Documents')
            )

            return self.entity_tab_widget
    
        return self.entity_scroll_area

    def _highlight_asterisk(self, text):
        #Highlight asterisk in red
        c = '*'

        #Do not format if there is no asterisk
        if text.find(c) == -1:
            return text

        asterisk_highlight = '<span style=\" color:#ff0000;\">*</span>'
        text = text.replace(c, asterisk_highlight)

        return u'<html><head/><body><p>{0}</p></body></html>'.format(text)