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

from typing import Optional

from qgis.PyQt.QtWidgets import (
    QLabel,
    QSizePolicy
)
from qgis.core import (
    QgsLayoutItem
)
from qgis.gui import (
    QgsGui,
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget
)


class LayoutGuiUtils:

    @staticmethod
    def get_gui_metadata_for_item_type(item_type: int) -> Optional[QgsLayoutItemAbstractGuiMetadata]:
        for item_gui_id in QgsGui.layoutItemGuiRegistry().itemMetadataIds():
            if QgsGui.layoutItemGuiRegistry().itemMetadata(item_gui_id).type() == item_type:
                return QgsGui.layoutItemGuiRegistry().itemMetadata(item_gui_id)
        return None

    @staticmethod
    def create_standard_item_widget(item: QgsLayoutItem, standard_item_type: int) -> Optional[QgsLayoutItemBaseWidget]:
        metadata = LayoutGuiUtils.get_gui_metadata_for_item_type(standard_item_type)
        if metadata is None:
            return None

        return metadata.createItemWidget(item)

    @staticmethod
    def create_heading_label(text: str) -> QLabel:
        label = QLabel(text)
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sp)
        label.setStyleSheet("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);")
        return label
