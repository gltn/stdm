# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Custom table type
"""

from qgis.PyQt.QtCore import (
    QCoreApplication
)

from qgis.PyQt.QtXml import (
        QDomDocument,
        QDomElement
)

from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAttributeTable,
    QgsLayoutMultiFrameAbstractMetadata,
    QgsReadWriteContext
)

from stdm.ui.gui_utils import GuiUtils

STDM_DATA_TABLE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 2


class StdmTableLayoutItem(QgsLayoutItemAttributeTable):

    def __init__(self, layout):
        super().__init__(layout)

        print('* B *')

        self._table = None
        self._datasource_field = None
        self._referencing_field = None

    def type(self):
        return STDM_DATA_TABLE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('composer_table.png')

    @property
    def table(self) -> str:
        """
        return: Name of the referenced table.
        """
        return self._table

    def set_table(self, tab: str):
        """
        Set the name of the referenced table.
        """
        self._table = tab

    @property
    def datasource_field(self) -> str:
        return self._datasource_field

    def set_datasource_field(self, field: str):
        self._datasource_field = field

    @property
    def referencing_field(self) -> str:
        return self._referencing_field

    def set_referencing_field(self, field: str):
        self._referencing_field = field

    # def getTableContents(self, contents):
    #      return True

    def writePropertiesToElement(self, element: QDomElement, document:QDomDocument,
                                 context: QgsReadWriteContext) -> bool:
        super().writePropertiesToElement(element, document, context)
        
        if self._table:
            element.setAttribute('table', self._table)

        if self._datasource_field:
            element.setAttribute('datasource_field', self._datasource_field)

        if self._referencing_field:
            element.setAttribute('referencing_field', self._referencing_field)

        self.recalculateFrameSizes()

        return True

    def readPropertiesFromElement(self, element: QDomElement, document: QDomDocument,
                                  context: QgsReadWriteContext) -> bool:
        super().readPropertiesFromElement(element, document, context)

        self._table = element.attribute('table') or None
        self._datasource_field = element.attribute('datasource_field') or None
        self._referencing_field = element.attribute('referencing_field') or None

        return True



class StdmTableLayoutItemMetadata(QgsLayoutMultiFrameAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_TABLE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Table'))

    def createMultiFrame(self, layout):
        return StdmTableLayoutItem(layout)
