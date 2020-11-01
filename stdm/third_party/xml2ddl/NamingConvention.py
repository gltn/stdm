#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

""" 
The purpose of this file (NamingConvention.py) is to allow a standardized naming 
schemes for tables, columns, and so on. 

For example, you may define an abbreviation for the table name and the column names will use
that abbreviation + "_" + the column name given in the XML file.

There is still some work to be done here. To make this truly useful.
"""


def getTableName(table):
    """ Here the table name is just the name attribute """
    return table.getAttribute('name')
    
def getColName(col):
    """ The column name is the concatination of the table's "abbr" and the column name.
    If abbr doesn't exist, it's just the column name
    """
    strAbbr = col.parentNode.parentNode.getAttribute('abbr')
    if len(strAbbr) > 0:
        return strAbbr + '_' + col.getAttribute('name')
    
    return col.getAttribute('name')
    
def getRelationName(relation):
    """ If the relation has a "name" use it. otherwise create a name using
     fk_<fkcolumnname>
    """
    strConstraintName = relation.getAttribute('name')
    if len(strConstraintName) == 0:
        strConstraintName = "fk_%s" % (relation.getAttribute('column'))

    return strConstraintName

def getIndexName(strTableName, index):
    """ If an index name is given, use it otherwise,
    use idx_<tablename>_<colNames>
    """
    strIndexName = index.getAttribute("name")
    if strIndexName and len(strIndexName) > 0:
        return strIndexName
    
    cols = index.getAttribute("columns").split(',')
    cols = [col.strip() for col in cols ] # Remove spaces
    
    strIndexName = "idx_" + strTableName + '_'.join([col.strip() for col in cols])
    
    return strIndexName

def getPkContraintName(strTableName):
    """ The primary key name is pk_<tablename>
    TODO: should pass the xml doc not the name and pass the col name """
    return 'pk_%s' % (strTableName)
    

def getSeqName(strTableName, strColName):
    """ The sequence name is the <tablename>_<colname>_seq 
    TODO: should pass the XML docs not the name"""
    return '%s_%s_seq' % (strTableName, strColName)

def getAiTriggerName(strTableName, strColName):
    """ The auto increment trigger is "ai_<tablename>_<colname> 
    TODO: should pass the XML doc objects not the names """
    
    return 'ai_%s_%s' % (strTableName, strColName)