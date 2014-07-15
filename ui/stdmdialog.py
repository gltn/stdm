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
from .dialog_generator import  ContentView
from sqlalchemy import Table
from sqlalchemy.orm import mapper
from stdm.data import Model, Base, STDMDb
#from stdm.data import tableCols
from stdm.data.config_utils import tableCols

from collections import OrderedDict
import types

from stdm.data.database import Singleton

class STDMDialog(object):
    '''
    this class reads the selected table model and returns the associated qtalchemy dialog
    '''
    def __init__(self,module,parent):
        
        self.tableName=module
        self.parent=parent
        self.columns=[]
        #self.loadUI()
       
    def loadUI(self):    
        self.toqtalchemyMapping()
            
    def toqtalchemyMapping(self):
        mapping=declareMapping.instance()
        tableCls=mapping.tableMapping(self.tableName)
        self.columns=self.tablecolums()
        Session=STDMDb.instance().session
        #QMessageBox.information(None,"test",str(self.propertyAttribute(tableCls)))
        contentMd=ContentView(self.parent,tableCls,self.columns,Session=Session)
        contentMd.show()
        contentMd.exec_()

    def propertyAttribute(self,classObj):
        for attrib in self.columns:
            classname=classObj.__table__
            attrTranslation=OrderedDict()
            # attrTranslation[attrib]=attrib.replace('_',' ').title()
            return classname
                   
        
    def tablecolums(self):
        return tableCols(self.tableName)
        
@Singleton                  
class declareMapping():  
    '''
    this class takes an instance of the table defined the schema and returns a model objects
    '''
    def __init__(self,list=None):
        self.list=list
        self.mapping={}
    
    def setTableMapping(self,list):
        for table in list:
            className=table.capitalize()
            classObject=self.classFromTable(className)
            pgtable=Table(table,Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
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
        attribs=OrderedDict()
        if table!='':
            cols=tableCols(table)
            
            for col in cols:
                attribs[col]=col.replace('_',' ').title()
        else:
            return None
        return attribs
    
    def createDynamicClass(self,className,**attr):
        '''create a python class from database table name'''
        return type(className,(Model,),dict(**attr))
    
    def classFromTable(self,className):
        return self.createDynamicClass(className)
        
