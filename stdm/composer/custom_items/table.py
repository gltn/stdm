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
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAttributeTable,
    QgsLayoutMultiFrameAbstractMetadata
)

from stdm.ui.gui_utils import GuiUtils

STDM_DATA_TABLE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 2


class StdmTableLayoutItem(QgsLayoutItemAttributeTable):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_DATA_TABLE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('composer_table.png')

    def getTableContents(self, contents):
        return True


class StdmTableLayoutItemMetadata(QgsLayoutMultiFrameAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_TABLE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Table'))

    def createMultiFrame(self, layout):
        return StdmTableLayoutItem(layout)
