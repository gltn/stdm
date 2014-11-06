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
from stdm.data import lookupData

class TypePropertyMapper(object):
    def __init__(self, attrMap, options = None):
        self._attr = attrMap
        self.widgetList = OrderedDict()
        self._attr.pop('id')

    def widget(self):
        isLookup = False
        for attr, dataType in self._attr.iteritems():
            if dataType[1] != False:
                dataType[0] = 'choice'
                options = self.lookupOptions(dataType[1])
                if options: isLookup = options
            self.widgetList[attr] = [widgetCollection()[dataType[0]], isLookup]

    def setProperty(self):
        self.widget()
        return self.widgetList

    def lookupOptions(self, tName):
        '''
        if it is a lookup get values from the config
        :return:
        '''
        choice_list = lookupData(tName)
        return choice_list
