# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
from collections import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import *

geometry_collections = {
    QApplication.translate("GeometryProperty",'Point'): 'POINT',
    QApplication.translate("GeometryProperty",'Line'): 'LINESTRING',
    QApplication.translate("GeometryProperty",'Polygon'): 'POLYGON',
    QApplication.translate("GeometryProperty",'Multipolygon'): 'MULTIPOLYGON'
}

data_types = {
        '': '',
        QT_TR_NOOP("Whole Number"): 'integer',
        QT_TR_NOOP("Decimal Number"): 'double precision',
        QT_TR_NOOP("Date"): 'date',
        QT_TR_NOOP("True/ False"): 'boolean',
        QT_TR_NOOP('Short text'): 'character varying',
        QT_TR_NOOP('Long text'): 'text',
        QT_TR_NOOP('Auto Increment'): 'serial',
        QT_TR_NOOP('Geometry'): 'geometry'
         }

actions = {
            QApplication.translate("TableProperty",'CASCADE'): 'cascade',
            QApplication.translate("TableProperty",'SET NULL'): 'setnull'
             }

constraints = {
             QApplication.translate("TableProperty",'Unique'): 'UNIQUE',
             QApplication.translate("TableProperty",'Check'): 'CHECK'
              }

nullable = {
            QApplication.translate("TableProperty",'Yes'): 'no',
            QApplication.translate("TableProperty",'No'): 'yes'
          }

stdm_core_tables = ['household', 'spatial_unit', 'party', 'natural_person', 'group', 'social_tenure_relationship', 'supporting_document']

postgres_defaults = ['integer','date','boolean','time with time zone','serial',
                     'geometry','double precision','text']

RESERVED_ID = 'id'



