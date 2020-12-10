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

from qgis.core import (
    QgsLayout
)


class LayoutUtils:

    @staticmethod
    def get_stdm_data_source_for_layout(layout: QgsLayout) -> Optional[str]:
        return layout.customProperty('variable_stdm_data_source', None)

    @staticmethod
    def set_stdm_data_source_for_layout(layout: QgsLayout, source: Optional[str]):
        layout.setCustomProperty('variable_stdm_data_source', source)
