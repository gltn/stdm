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
from stdm.utils import *
from .wigets import widgetCollection
from stdm.data import lookupData
from PyQt4.QtGui import *
from stdm.ui.stdmdialog import  DeclareMapping


class TypePropertyMapper(object):
    def __init__(self, attrMap, options = None):
        
        self._mapper = DeclareMapping.instance()
        self._attr = attrMap
        self.widgetList = OrderedDict()
        self.hideGUID()

    def hideGUID(self):
        for keys in self._attr:
            if keys == 'id':
                self._attr.pop(keys)

    def widget(self):
        isLookup = False
        for attr, dataType in self._attr.iteritems():
            if dataType[1] != False:
                dataType[0] = 'choice'
                options = self.lookupModel(dataType[1])
                if options: isLookup = options
            self.widgetList[attr] = [widgetCollection()[dataType[0]], isLookup]

    def setProperty(self):
        self.widget()
        return self.widgetList
    
    def userLookupOptions(self,DBmodel):
        '''
        Fetch lookup values from the DB.
        '''
        return readComboSelections(DBmodel)
        
    def lookupModel(self, tName):
        '''
        ensure the lookup table is mapped to an SQLALchemy mapper entity
        '''
        self._lkmodel = self._mapper.tableMapping(tName.lower())
        modelItems = self.userLookupOptions(self._lkmodel)
        return modelItems
        