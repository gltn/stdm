"""
/***************************************************************************
Name                 : PGUtils
Description          : Provides generic PostGIS functions that are not
                       available through GeoAlchemy
Date                 : 1/April/2014
copyright            : (C) 2013 by UN-Habitat and implementing partners.
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
from qgis.core import (
    QgsMapLayerRegistry,
    QgsDataSourceURI
)

from stdm.utils import ReverseDict


def pg_layer_names_id_mapping():
    """
    Returns a dictionary containing the original table names and
    corresponding  layer IDs in the QGIS legend for only those layers from a
    postgres database.
    """
    mapping = ReverseDict()
    layers = QgsMapLayerRegistry.instance().mapLayers()

    for name, layer in layers.iteritems():
        if hasattr(layer, 'dataProvider'):
            if layer.dataProvider().name() == 'postgres':
                layer_conn_str = layer.dataProvider().dataSourceUri()
                data_source_uri = QgsDataSourceURI(layer_conn_str)
                mapping[data_source_uri.table()] = layer.id()

    return mapping
