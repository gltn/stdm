# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-30
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
from xmlconfig_reader import XMLTableElement, tableColumns, tableRelations,lookupTable,AllColumns
from xmlconfig_writer import writeXml, writeHTML
from stdm.data import listEntityViewer, EntityColumnModel
from stdm.utils.configfile_paths import FilePaths


class ConfigTableReader(object):
    def __init__(self,parent=None):
        
        self._doc=''
        self.fileHandler=FilePaths()
        
    def loadTableData(self,widget):
        '''method returns the model to the passed listview widget'''
        model=self.tableListModel() 
        widget.setModel(model)
        return widget
   
    def tableListModel(self):
        '''pass the table to a list view model'''
        tData=self.tableNames()
        model=listEntityViewer(tData)
        return model
            
    def tableNames(self):
        '''Get the default table names as defined in the config'''
        tableData=XMLTableElement()
        if tableData is not None:
            return tableData
        
    def lookupTable(self):
        lookups=lookupTable()
        model=listEntityViewer(lookups)
        return model
    
    def lookupColumns(self,lookupName):
        columnModel=None
        tableAttrib=AllColumns(lookupName)
        if len(tableAttrib)>0:
            colHeaders=tableAttrib[0].keys()
            colVals=[]
            for item in tableAttrib:
                colVals.append(item.values())
            columnModel=EntityColumnModel(colHeaders,colVals)
            return columnModel
        else: 
            return None
    
    def columns(self, tableName):
        '''Functions to read columns details from the config for the given table''' 
        columnModel=None
        tableAttrib=tableColumns(tableName)
        if len(tableAttrib)>0:
            colHeaders=tableAttrib[0].keys()
            colVals=[]
            for item in tableAttrib:
                colVals.append(item.values())
            columnModel=EntityColumnModel(colHeaders,colVals)
            return columnModel
        else: 
            return None
    
    def tableRelation(self,tableName):
        '''Method to read all defined table relationship in the config file'''
        relationModel=None
        tableAttrib=tableRelations(tableName)
        if tableAttrib==None:
            return
        if len(tableAttrib)>0:
            colHeaders=tableAttrib[0].keys()
            colVals=[]
            for item in tableAttrib:
                colVals.append(item.values())
            relationModel=EntityColumnModel(colHeaders,colVals)
            return relationModel
        else:
            return None
    def htmlTableDefinition(self):
        '''load the table definition info in html file'''
        #=self.fileHandler.getHTMLObject()
        #docfile=self.fileHandler.getXMLObject()
        docfile=self.fileHandler.SQLFile()
        return docfile
    
    def saveXMLchanges(self):
        writeXml()
        writeHTML()
        
        