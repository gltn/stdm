# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : xmldata2sql
Description          : 
Date                 : 24/September/2013
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
    def __init__(self, table, args):
        self.args = args
        self.table = table
        self.sql_def = []
        
    def key_col_attrib(self):
        '''get column keys into the SQL prepend statement'''
        'temporary fix, because data column is only one...can be improved'
        col_keys=["value"]
        if col_keys:
            sql_prepend = r'("'+r'", "'.join(col_keys) + r'")'
        return sql_prepend
        
    def col_values(self):
        if len(self.key_col_attrib())>1:
            if self.args:
                sql_insert = r'('"'"+r"','".join(self.args) +r"');"
                return sql_insert
        
    def set_insert_statement(self):
        '''Run through the lookup table list and return the full insert statement'''
        for value in self.args:
            sql_insert =  r'('+r"'"+value +r"');"
            self.sql_def.append(INSERTSQL%(self.table, self.key_col_attrib(), str(sql_insert)))
        return self.sql_def

    def social_tenure_duplicate_enforce(self):
        """
        Method to create constraint to enforce duplicate values in STR tables
        :return:
        """
        return "ALTER TABLE social_tenure_relationship ADD CONSTRAINT social_tenure_relationship_party_spatial_unit_key UNIQUE (party, spatial_unit)"

    def spatial_relation(self):
        # needed for creation of map on the composer and reporting on social tenure
        social_tenure = "CREATE OR REPLACE VIEW social_tenure_relations AS SELECT party.id, party.family_name AS party_surname, party.other_names, \
        party.identification, spatial_unit.code AS spatial_unit_number, spatial_unit.name AS spatial_unit_name, spatial_unit.geom_polygon AS geometry, \
        social_tenure_relationship.social_tenure_type FROM party, spatial_unit, social_tenure_relationship \
        WHERE spatial_unit.id = social_tenure_relationship.spatial_unit AND party.id = social_tenure_relationship.party; "
            
        return social_tenure
