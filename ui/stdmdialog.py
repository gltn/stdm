# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdmDialog
                                 A QGIS plugin
 Securing land and property rights for all
                             -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : gltn_stdm@unhabitat.org
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
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#from .entity_browser import ContentGroupEntityBrowser

# create the dialog for zoom to point

from sqlalchemy import Table
from sqlalchemy.orm import mapper
from stdm.data import Model, Base, STDMDb
#from stdm.data import tableCols
from stdm.data.config_utils import tableCols

from collections import OrderedDict
import types

from stdm.data.database import Singleton

        
@Singleton                  
class DeclareMapping(object):
    '''
    this class takes an instance of the table defined the schema and returns a model objects
    '''
    def __init__(self,list=None):
        self.list=list
        self.mapping={}
        self.attDictionary = OrderedDict()
        self.type_dictionary = OrderedDict()
    
    def setTableMapping(self,list):
        for table in list:
            className=table.capitalize()
            classObject=self.classFromTable(className)
            pgtable=Table(table,Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
            self.column_mapping_for_table(pgtable)
            self.datatype_for_column(pgtable)
            mapper(classObject,pgtable)
            self.mapping[table]=classObject
              
    #@property
    def tableMapping(self,table):
        if table in self.mapping:
            modelCls = self.mapping[table]
            Model.attrTranslations = self.displayMapping(table)
            return modelCls
        
    def instance(self,*args,**kwargs):
        '''
        Dummy method
        '''
        pass

    def displayMapping(self,table=''):
        """
        Replaces the depreciated method where column names were read from the config.
        column names already stored in a dictionary.
        :param table:
        :return:
        """
        attribs = OrderedDict()
        if table != '':
            col_list = self.attDictionary.get(table)
            for col in col_list:
                attribs[col]=col.replace('_',' ').title()
        else:
            return None
        return attribs
    
    def createDynamicClass(self,className,**attr):
        '''create a python class from database table name'''
        return type(className,(Model,),dict(**attr))
    
    def classFromTable(self,className):
        return self.createDynamicClass(className)
    
    def resetMapping(self):
        self.mapping={}
        
    def column_mapping_for_table(self,table):
        """
        Method to store all the columns names from the database table into an array.

        :param table:
        :return:
        """
        self.attDictionary[table.name] = [column.name for column in table.columns]

    def datatype_for_column(self, table):
        """

        :param table:
        :return:
        """
        self.typemapping = OrderedDict()
        for column in table.columns:
            self.typemapping[column.name] = column.type
        self.type_dictionary[table.name] = self.typemapping

    def column_data_types(self, table):
        """
        Return the table columns datatype as a dictionary
        :return:
        """
        return self.type_dictionary.get(table)
