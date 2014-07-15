"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
email                : njoroge.solomon.com
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
from .wigets import widgetCollection
class TypePropertyMapper(object):
    def __init__(self, attrMap, options=None):
        
        self._attr=attrMap
        self.attripMap=[]
        self.widgetList=OrderedDict()
        self._attr.pop('id')
        
    def widget(self):
        for attr, dataType in self._attr.iteritems():
            self.widgetList[attr]=widgetCollection()[dataType[0]]
            
    def setProperty(self):
        self.widget()
        return self.widgetList
        