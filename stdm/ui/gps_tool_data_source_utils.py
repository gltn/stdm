"""
/***************************************************************************
Name                 : GPS Feature Import Data Source Utility Module
Description          : Utility module that handles GPX file source
Date                 : 17/January/2017
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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

import os.path
import re
import logging

from PyQt4.QtGui import QApplication
from osgeo import ogr


LOGGER = logging.getLogger('stdm')
FEATURE_TYPES = ['waypoint', 'track', 'route']

def validate_file_path(gpx_file):
    """
    Validate source file path since the user is allowed to type in the path
    :param gpx_file: Input GPX file
    :return: True if file path is valid and None when not valid
    :rtype: Boolean
    """
    if gpx_file:
        reg_ex = re.compile(r'^(([a-zA-Z]:)|((\\|/){1,2}\w+)\$?)((\\|/)(\w[\w ]*.*))+\.(gpx)$')
        return True if reg_ex.search(gpx_file) and _file_readable(gpx_file) else None
    return None


def _file_readable(file_path):
    """
    Checks if source file is readable
    :param file_path: Full file path
    :return: True if it is a file and readable at
             the same time. otherwise return None
    :rtype: Boolean
    """
    try:
        return None if not os.path.isfile(file_path) and not os.access(file_path, os.R_OK) else True
    except IOError as ex:
        LOGGER.debug("I/O error({0}): {1}".format(ex.errno, ex.strerror))


def open_gpx_file(gpx_file):
    """
    Opens input GPX file
    :param gpx_file: Input GPX file
    :return: File object
    :rtype: Object
    """
    gpx_data_source = ogr.Open(gpx_file)
    if not gpx_data_source:
        raise Exception(
            "File {0} could not be accessed. "
            "It could be in use by another application".format(
                os.path.basename(gpx_file)
            )
        )
    return gpx_data_source


def get_feature_layer(gpx_data_source, feature_type):
    """
    Gets valid feature layer from the GPX file based on
    the selected feature type
    :param gpx_data_source: Open file object
    :param feature_type: User feature type input
    :return  gpx_layer: GPX file feature layer
    :return feature_count: Number of features
    :rtype gpx_layer: Layer object
    :rtype feature_count: Integer
    """
    if feature_type >= 0:
        if FEATURE_TYPES[feature_type] == 'track' or \
                        FEATURE_TYPES[feature_type] == 'route':
            feature_type = '{}_points'.format(FEATURE_TYPES[feature_type])
        else:
            feature_type = '{}s'.format(FEATURE_TYPES[feature_type])
        gpx_layer = gpx_data_source.GetLayerByName(feature_type)
        feature_count = gpx_layer.GetFeatureCount()
        return None if feature_count == 0 else gpx_layer, feature_count


def get_active_layer_type(active_layer):
    """
    Gets the active layer and its geometry type
    :param active_layer: QGIS active layer
    :return active_layer: Active layer in the layer panel
    :return active_layer_type: The active layer geometry type
    :rtype: Layer object
    """
    geometry_types = ['Point', 'LineString', 'Polygon']
    active_layer_geom_type = int(active_layer.geometryType())
    if active_layer_geom_type > 2:
        return None
    for i, geom_type in enumerate(geometry_types):
        if active_layer_geom_type == i:
            return geom_type, active_layer_geom_type
