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

from stdm.composer.custom_items.photo import StdmPhotoLayoutItem
from stdm.composer.layout_utils import LayoutUtils
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

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_photo_data_source.ui'))


class ComposerPhotoDataSourceEditor(WIDGET, BASE):
    def __init__(self, item: StdmPhotoLayoutItem, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        print('Photo::DS')

        self._layout = item.layout()
        self._item = item

        print('Layout ITEM: ', item.linked_table)

        self._notif_bar = NotificationBar(self.vl_notification)

        self._curr_profile = current_profile()

        # Load fields if the data source has been specified
        ds_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self.ref_table.load_data_source_fields(ds_name)

        # Base document table in the current profile
        self._base_document_table = self._curr_profile.supporting_document.name

        # Add it to the list of tables to omit
        self.ref_table.add_omit_table(self._base_document_table)

        '''
        Load referenced table list and filter so to only load supporting
        doc tables.
        '''
        reg_exp = supporting_doc_tables_regexp()
        self.ref_table.load_link_tables(reg_exp)
        #self.ref_table.load_link_tables(supporting_doc_tables_regexp())

        self.ref_table.set_layout(self._layout)

        self.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
            self.update_document_types
        )

        # self.ref_table._load_source_table_fields(
        #         self._item.linked_table())

        self.set_from_item()

        self.ref_table.changed.connect(self._item_changed)
        self.cbo_document_type.currentTextChanged.connect(self._item_changed)

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

    def _item_changed(self):
        linked_table_props = self.ref_table.properties()

        self._item.set_linked_table(linked_table_props.linked_table)
        self._item.set_source_field(linked_table_props.source_field)
        self._item.set_linked_column(linked_table_props.linked_field)
        self._item.set_document_type(self.cbo_document_type.currentText())

        doc_type_id = self.cbo_document_type.itemData(
            self.cbo_document_type.currentIndex()
        )
        self._item.set_document_type_id(doc_type_id)

        self._item.set_referencing_field(self.ref_table.cbo_referencing_col.currentText())
        self._item.update()

    def set_from_item(self):
        # Load referenced table editor with item configuration settings.
        try:

            photo_props = LinkedTableProps(linked_table=self._item.linked_table,
                                        source_field=self._item.source_field,
                                        linked_field=self._item.linked_field)


            self.ref_table.set_properties(photo_props)

            GuiUtils.set_combo_current_index_by_text(
                self.cbo_document_type,
                self._item.document_type()
            )

            GuiUtils.set_combo_current_index_by_text(
                    self.ref_table.cbo_ref_table,
                    self._item.linked_table()
                    )

            GuiUtils.set_combo_current_index_by_text(
                    self.ref_table.cbo_referencing_col,
                    self._item.referencing_field()
                    )
        except:
            pass


