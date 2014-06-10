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
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import mapper, relationship , clear_mappers, backref
from stdm.data import STDMEntity, STDMDb, Base
from qtalchemy.foreign_key import ForeignKeyReferral

class TableMapper(object):
    '''Mapper class from pgsql table to sqlalchemy model'''
    def __init__(self,table):
        self.lookup=None
        self.table=table
    
    def postgresTable(self):
        '''read selected table metadata using existing engine'''
        mappingTable=Table(self.table,Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
        return mappingTable
    
    def postgresTable2(self):
        '''read selected table metadata using existing engine'''
        mappingTable=Table(self.table,Base.metadata,autoload=True,non_primary=True,autoload_with=STDMDb.instance().engine)
        return mappingTable
    
    def setMapping(self,table):
        '''map db table to a python object'''
        #mappingTable=self.postgresTable()
        mapper(STDMEntity,table)
        
    def isreferenceTable(self):
        '''Check if the reference table is already loaded in metadata'''
        linkTables=[]
        for table in self.meta.sorted_tables:
            linkTables.append(table.name)
        return linkTables
        
    def referenceTable(self,list):
        refTable=[]
        for table in list:
            if table in self.meta.tables:
                table=Table(table,self.metadata)
                refTable.append(table)
        return refTable
    
        
        