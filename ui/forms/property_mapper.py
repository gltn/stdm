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
from stdm.data import STDMDb
from .widgets import widgetCollection
from stdm.data import lookupData
from PyQt4.QtGui import *
from stdm.ui.stdmdialog import  DeclareMapping
from Lookup import  LookupModeller


class TypePropertyMapper(object):
    def __init__(self, attrMap, options = None):
        """ Class to read and match the datatype to respective control on the form"""
        self._modeller = LookupModeller()
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
            if dataType[1]:
                dataType[0] = 'choice'
                self._modeller.setLookupAttribute(dataType[0])
                lkModel = self._modeller.lookupModel(dataType[1])
                options = self.lookupItems(lkModel)
                if options: isLookup = options
            self.widgetList[attr] = [widgetCollection()[dataType[0]], isLookup]

    def setProperty(self):
        self.widget()
        return self.widgetList
    
    def userLookupOptions(self, DBmodel):
        """
        Fetch lookup values from the DB.
        """
        try:
            lkupModel = readComboSelections(DBmodel)
        except Exception as ex:
            QMessageBox.information(None,'Lookup choices', str(ex.message))
        finally:
            self.clearMapping()
        return lkupModel

    def lookupItems(self, model):
        modelItems = self.userLookupOptions(model)
        #QMessageBox.information(None,'modeller', str(model.displayMapping()))
        return modelItems

    def clearMapping(self):
        STDMDb.instance().session.rollback()