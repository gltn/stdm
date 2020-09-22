"""
/***************************************************************************
Name                 : PGUtils
Description          : Provides generic PostGIS functions that are not
                       available through GeoAlchemy
Date                 : 1/April/2014
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

from stdm import ReverseDict

def pg_layerNamesIDMapping():
    '''
    Returns a dictionary containing the original table names and corresponding layer IDs in the
    QGIS legend for only those layers from a postgres database.
    '''
    mapping = ReverseDict()
    layers = QgsMapLayerRegistry.instance().mapLayers()

    for name,layer in layers.iteritems():
        if hasattr(layer, 'dataProvider'):
            if layer.dataProvider().name() == 'postgres':
                layerConnStr = layer.dataProvider().dataSourceUri()
                dataSourceURI = QgsDataSourceURI(layerConnStr)
                mapping[dataSourceURI.table()] = layer.id()

    return mapping








