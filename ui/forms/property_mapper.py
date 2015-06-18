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
from .widgets import WidgetCollection
from PyQt4.QtGui import QMessageBox
from stdm.ui.stdmdialog import DeclareMapping
from lookup_dlg import LookupModeller


class TypePropertyMapper(object):
    def __init__(self, attrMap, options = None):
        """ Class to read and match the datatype to respective control on the form"""
        self._modeller = LookupModeller()
        self._mapper = DeclareMapping.instance()
        self._attr = attrMap
        self.widgetList = OrderedDict()
        self.hideGUID()

    def hideGUID(self):
        try:
            for keys in self._attr.keys():
                if keys == 'id':
                    self._attr.pop(keys)
        except KeyError as ex:
            raise ex.message

    def widget(self):
        isLookup = False
        lk_items = None
        widget_collection = WidgetCollection()
        for attr, attr_data_type in self._attr.iteritems():
            if attr_data_type[1]:
                attr_data_type[0] = 'choice'
                lkModel = self._modeller.lookupModel(attr_data_type[1])
                lk_items = self.lookupItems(lkModel)
                if lk_items:
                    isLookup = True
            controlwidget = widget_collection.widget_control_type(attr_data_type[0])
            self.widgetList[attr] = [controlwidget, isLookup, lk_items]

    def setProperty(self):
            self.widget()
            return self.widgetList


    def userLookupOptions(self, DBmodel):
        """
        Fetch lookup values from the DB.
        """
       # try:
        lkupModel = readComboSelections(DBmodel)
        return lkupModel
        #except Exception as ex:
           # QMessageBox.information(None,'Lookup choices',
            #QApplication.translate(u'TypePropertyMapper',"Error loading %s lookup values"%str(ex.message)))
        #finally:
       #     self.clearMapping()
        

    def lookupItems(self, model):
        modelItems = self.userLookupOptions(model)
        return modelItems

    def clearMapping(self):
        STDMDb.instance().session.rollback()