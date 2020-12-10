# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Contains custom layout item types
"""
from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPolyline,
    QgsApplication
)
from qgis.gui import (
    QgsGui,
    QgsLayoutItemAbstractGuiMetadata
)

from stdm.ui.gui_utils import GuiUtils

BASE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337
STDM_LINE_ITEM_TYPE = BASE_ITEM_TYPE + 0


class StdmLineLayoutItem(QgsLayoutItemPolyline):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_LINE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('line.png')


class StdmLineLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'Line'))

    def createItem(self, layout):
        return StdmLineLayoutItem(layout)


class StdmLineLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'Line'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('line.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


class StdmCustomLayoutItems:
    CUSTOM_CLASSES = [StdmLineLayoutItemMetadata]
    GUI_CLASSES = [StdmLineLayoutItemGuiMetadata]

    metadata = []
    gui_metadata = []

    @classmethod
    def add_custom_item_types(cls):
        for m in cls.CUSTOM_CLASSES:
            item_metadata = m()
            if item_metadata.type() in QgsApplication.layoutItemRegistry().itemTypes():
                continue  # already added

            cls.metadata.append(item_metadata)
            QgsApplication.layoutItemRegistry().addLayoutItemType(item_metadata)

    @classmethod
    def register_gui(cls):
        existing_items_types = [QgsGui.layoutItemGuiRegistry().itemMetadata(_id).type() for _id in
                                QgsGui.layoutItemGuiRegistry().itemMetadataIds()]

        for m in cls.GUI_CLASSES:
            item_metadata = m()

            if item_metadata.type() in existing_items_types:
                continue  # already added

            cls.gui_metadata.append(item_metadata)
            QgsGui.layoutItemGuiRegistry().addLayoutItemGuiMetadata(item_metadata)

    @classmethod
    def stdm_action_text(cls):
        items = [m().visibleName() for m in cls.GUI_CLASSES]
        return [QCoreApplication.translate('StdmItems', 'Add {}'.format(t)) for t in items]
