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
INSERTSQL=("INSERT INTO %s %s VALUES %s")
class SQLInsert(object):
    def __init__(self,table,args):
        self.args=args
        self.table=table
        self.sqlDef=[]
        
    def keyColAttrib(self):
        '''get column keys into the SQL prepend statement'''
        'temporary fix, data column is only one...can be improved'
        colKeys=["value"]
        if colKeys:
            sqlPrepend=r'("'+r'", "'.join(colKeys) + r'")'
        return sqlPrepend
        
    def colValues(self):
        if len(self.keyColAttrib())>1:
            if self.args:
                sqlInsert = r'('"'"+r"','".join(self.args) +r"');"
                return sqlInsert
        
    def setInsertStatement(self):
        '''Run through the table list and return the full insert statement'''
        for value in self.args:
            sqlInsert =  r'('+r"'"+value +r"');"
            self.sqlDef.append(INSERTSQL%(self.table,self.keyColAttrib(),str(sqlInsert)))
        self.sqlDef.append(self.spatialRelation())
        return self.sqlDef
    
    def spatialRelation(self):
        # needed for creation of map on the composer
        defaultView = "CREATE OR REPLACE VIEW spatial_unit_relations AS SELECT party.id, party.family_name AS sirname, party.other_names,\
        party.unique_id AS identification, \
        spatial_unit.spatial_unit_id AS identifier, spatial_unit.name AS type_name,spatial_unit.geom_polygon AS polygon \
        FROM party, spatial_unit, social_tenure_relationship \
        WHERE spatial_unit.id = social_tenure_relationship.spatial_unit AND party.id = social_tenure_relationship.party;"
            
        return defaultView
        
        
    