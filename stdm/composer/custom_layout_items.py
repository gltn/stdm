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

from qgis.core import (
    QgsApplication,
)

from stdm.composer.custom_items.chart import StdmChartLayoutItemMetadata
from stdm.composer.custom_items.label import StdmDataLabelLayoutItemMetadata
from stdm.composer.custom_items.line import StdmLineLayoutItemMetadata
from stdm.composer.custom_items.map import StdmMapLayoutItemMetadata
from stdm.composer.custom_items.photo import StdmPhotoLayoutItemMetadata
from stdm.composer.custom_items.qrcode import StdmQrCodeLayoutItemMetadata
from stdm.composer.custom_items.table import StdmTableLayoutItemMetadata


class StdmCustomLayoutItems:
    CUSTOM_CLASSES = [StdmLineLayoutItemMetadata,
                      StdmDataLabelLayoutItemMetadata,
                      StdmMapLayoutItemMetadata,
                      StdmPhotoLayoutItemMetadata,
                      StdmChartLayoutItemMetadata,
                      StdmQrCodeLayoutItemMetadata]
    CUSTOM_MULTIFRAME_CLASSES = [
        StdmTableLayoutItemMetadata
    ]
    metadata = []

    @classmethod
    def add_custom_item_types(cls):
        for m in cls.CUSTOM_CLASSES:
            item_metadata = m()
            if item_metadata.type() in QgsApplication.layoutItemRegistry().itemTypes():
                continue  # already added

            cls.metadata.append(item_metadata)
            QgsApplication.layoutItemRegistry().addLayoutItemType(item_metadata)

        for mf in cls.CUSTOM_MULTIFRAME_CLASSES:
            item_metadata = mf()
            if item_metadata.type() in QgsApplication.layoutItemRegistry().itemTypes():
                continue  # already added

            cls.metadata.append(item_metadata)
            QgsApplication.layoutItemRegistry().addLayoutMultiFrameType(item_metadata)
