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

datatypes = {
        'Short integer': 'integer',
        'Long integer': 'bigint',
        'True/ False': 'boolean',
        'Date': 'date',
        'Double/ decimal': 'double precision',
        'Auto Increment': 'serial',
        'Geometry': 'geometry',
        'Short text': 'character varying',
        'Long text': 'text'
         }

actions = {
            'CASCADE': 'cascade',
            'SET NULL': 'setnull'
             }

constraints = {
             'Unique': 'UNIQUE', 
             'Check': 'CHECK'
              }

nullable = {
            'Yes': 'no',
            'No': 'yes'
          }



