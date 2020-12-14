# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Contains utility functions for working with layouts
"""
from typing import Optional

from qgis.PyQt.QtCore import (
    QFile,
    QIODevice
)
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsLayout,
    QgsReadWriteContext,
    QgsLayoutItem
)


class LayoutUtils:

    DATA_SOURCE_PROPERTY = 'variable_stdm_data_source'
    DATA_CATEGORY_PROPERTY = 'variable_stdm_data_category'
    REFERENCED_TABLE_PROPERTY = 'variable_stdm_referenced_table'

    @staticmethod
    def get_stdm_data_source_for_layout(layout: QgsLayout) -> Optional[str]:
        return layout.customProperty(LayoutUtils.DATA_SOURCE_PROPERTY, None)

    @staticmethod
    def set_stdm_data_source_for_layout(layout: QgsLayout, source: Optional[str]):
        layout.setCustomProperty(LayoutUtils.DATA_SOURCE_PROPERTY, source)

    @staticmethod
    def get_stdm_data_category_for_layout(layout: QgsLayout) -> Optional[str]:
        return layout.customProperty(LayoutUtils.DATA_CATEGORY_PROPERTY, None)

    @staticmethod
    def set_stdm_data_category_for_layout(layout: QgsLayout, category: Optional[str]):
        layout.setCustomProperty(LayoutUtils.DATA_CATEGORY_PROPERTY, category)

    @staticmethod
    def get_stdm_referenced_table_for_layout(layout: QgsLayout) -> Optional[str]:
        return layout.customProperty(LayoutUtils.REFERENCED_TABLE_PROPERTY, None)

    @staticmethod
    def set_stdm_referenced_table_for_layout(layout: QgsLayout, table: Optional[str]):
        layout.setCustomProperty(LayoutUtils.REFERENCED_TABLE_PROPERTY, table)

    @staticmethod
    def load_template_into_layout(layout: QgsLayout, file_path: str):
        """
        Loads a document template into the view and updates the necessary STDM-related composer items.
        """
        copy_file = file_path.replace('sdt', 'cpy')

        # remove existing copy file
        if QFile.exists(copy_file):
            copy_template = QFile(copy_file)
            copy_template.remove()

        orig_template_file = QFile(file_path)

        layout.setCustomProperty('variable_template_path', file_path)

        # make a copy of the original
        orig_template_file.copy(copy_file)

        # work with copy
        template_file = QFile(copy_file)

        if not template_file.open(QIODevice.ReadOnly):
            raise IOError(template_file.errorString())

        template_doc = QDomDocument()
        if template_doc.setContent(template_file):

            # First load vector layers for the table definitions in the config
            # collection before loading the composition from file.

            from stdm.composer.table_configuration import TableConfigurationCollection

            #  table_config_collection = TableConfigurationCollection.create(template_doc)


            # Load items into the composition and configure STDM data controls
            context = QgsReadWriteContext()
            layout.loadFromTemplate(template_doc, context)

            LayoutUtils.sync_ids_with_uuids(layout)

        template_file.close()

    @staticmethod
    def sync_ids_with_uuids(layout: QgsLayout):
        """
        Matches IDs of custom STDM items with the corresponding UUIDs. This
        is applied when loading existing templates so that the saved
        document contains a matching pair of ID and UUID for each composer
        item.
        """
        items = [i for i in layout.items() if isinstance(i, QgsLayoutItem)]
        for i in items:
            i.setId(i.uuid())
