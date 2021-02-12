# ***************************************************************************
# Name                 : QGIS Layer utility functions
# Date                 : 12/Feb/2021
# copyright            : (C) 2021 by Nyall Dawson
# email                : nyall dot dawson at gmail dot com
# ***************************************************************************/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

"""
QGIS Layer utility functions
"""

from qgis.core import (
    QgsMapLayer,
    QgsProject
)


class LayerUtils:
    """
    Utility class for working with QGIS layers
    """

    IS_STDM_LAYER_KEY = 'stdm/is_stdm_layer'

    @staticmethod
    def tag_layer_as_stdm_layer(layer: QgsMapLayer):
        """
        Tags a map layer as a STDM sourced layer
        """
        layer.setCustomProperty(LayerUtils.IS_STDM_LAYER_KEY, True)

    @staticmethod
    def is_layer_stdm_layer(layer: QgsMapLayer) -> bool:
        """
        Returns True if the layer is a STDM sourced layer
        """
        return bool(layer.customProperty(LayerUtils.IS_STDM_LAYER_KEY))

    @staticmethod
    def enable_editing_of_stdm_layers(enabled: bool):
        """
        Enables (or disables) editing of all STDM layers in the current project
        """
        for _, layer in QgsProject.instance().mapLayers().items():
            if LayerUtils.is_layer_stdm_layer(layer) and layer.type() == QgsMapLayer.VectorLayer:
                layer.setReadOnly(not enabled)
