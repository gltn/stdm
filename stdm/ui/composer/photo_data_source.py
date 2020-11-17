"""
/***************************************************************************
Name                 : ComposerPhotoDatSourceEditor
Description          : Widget for specifying data properties for photos in
                       the document designer.
Date                 : 9/December/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from qgis.PyQt.QtWidgets import (
    QWidget
)

from stdm.data.configuration import entity_model
from stdm.data.supporting_documents import supporting_doc_tables_regexp
from stdm.settings import (
    current_profile
)
from stdm.ui.composer.referenced_table_editor import LinkedTableProps
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import (
    NotificationBar
)
from stdm.utils.util import setComboCurrentIndexWithText

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_photo_data_source.ui'))


class ComposerPhotoDataSourceEditor(WIDGET, BASE):
    def __init__(self, composer_wrapper, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._composer_wrapper = composer_wrapper

        self._notif_bar = NotificationBar(self.vl_notification)

        self._curr_profile = current_profile()

        # Load fields if the data source has been specified
        ds_name = self._composer_wrapper.selectedDataSource()
        self.ref_table.load_data_source_fields(ds_name)

        # Base document table in the current profile
        self._base_document_table = self._curr_profile.supporting_document.name

        # Add it to the list of tables to omit
        self.ref_table.add_omit_table(self._base_document_table)

        '''
        Load referenced table list and filter so to only load supporting
        doc tables.
        '''
        self.ref_table.load_link_tables(supporting_doc_tables_regexp())

        # Connect signals
        self._composer_wrapper.dataSourceSelected.connect(self.ref_table.on_data_source_changed)
        self.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
            self.update_document_types
        )

    def composer_item(self):
        return self._picture_item

    def update_document_types(self, document_table):
        # Updates the types of documents for the specified supporting doc table
        self.cbo_document_type.clear()

        if not document_table:
            return

        # Get list of supporting document entities in the current profile
        s_doc_entities = self._curr_profile.supporting_document_entities()
        selected_doc_entity = [de for de in s_doc_entities
                               if de.name == document_table]

        if len(selected_doc_entity) == 0:
            return

        doc_type_vl = selected_doc_entity[0].document_type_entity

        # Query id values from the document type lookup table
        lk_cls = entity_model(doc_type_vl, entity_only=True)
        lk_obj = lk_cls()
        res = lk_obj.queryObject().filter().all()

        for r in res:
            self.cbo_document_type.addItem(r.value, r.id)

    def configuration(self):
        from stdm.stdm.composer import PhotoConfiguration

        linked_table_props = self.ref_table.properties()

        ph_config = PhotoConfiguration()
        ph_config.set_linked_table(linked_table_props.linked_table)
        ph_config.set_source_field(linked_table_props.source_field)
        ph_config.set_linked_column(linked_table_props.linked_field)
        ph_config.document_type = self.cbo_document_type.currentText()

        doc_type_id = self.cbo_document_type.itemData(
            self.cbo_document_type.currentIndex()
        )
        ph_config.document_type_id = doc_type_id

        return ph_config

    def set_configuration(self, configuration):
        # Load referenced table editor with item configuration settings.
        photo_props = LinkedTableProps(linked_table=configuration.linked_table(),
                                       source_field=configuration.source_field(),
                                       linked_field=configuration.linked_field())

        self.ref_table.set_properties(photo_props)
        setComboCurrentIndexWithText(
            self.cbo_document_type,
            configuration.document_type
        )
