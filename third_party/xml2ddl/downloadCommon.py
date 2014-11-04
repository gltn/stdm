#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-


def getSeqName(strTableName, strColName):
    return '%s_%s_seq' % (strTableName.strip(), strColName.strip())

class DownloadCommon:
    def connect(self, info):
        pass
        
    def useConnection(self, con, version):
        pass
        
    def getTables(self, tableList = None):
        """ Returns the list of tables as a array of strings """
        
        return []

    def getTableColumns(self, strTable):
        """ Returns column in this format
            (nColIndex, strColumnName, strColType, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, bNotNull, strDefault, auto_increment)
        """
        return []
    
    def getTableComment(self, strTableName):
        """ Returns the comment as a string """
        return None

    def getColumnComment(self, strTableName, strColumnName):
        """ Returns the comment as a string """
        return None

    def getTableIndexes(self, strTableName):
        """ Returns 
            (strIndexName, [strColumns,], bIsUnique, bIsPrimary, bIsClustered)
            or []
        """
        
        return []

    def getTableRelations(self, strTableName):
        """ Returns 
            (strConstraintName, colName, fk_table, fk_columns, confupdtype, confdeltype)
            or []
        """
        return []
        
    def getViews(self, viewList = None):
        """ Returns the list of views as a array of strings """
        
        return []

    def getViewDefinition(self, strViewName):
        """ Returns the select statement used to do the view's query """
        
        return None

    def getFunctions(self, functionList = None):
        """ Returns functions """
        
        return []

    def getFunctionDefinition(self, strSpecifiName):
        """ Returns (routineName, parameters, return, language, definition) """
        
        return (None, None, None, None)
        
    def _confirmReturns(self, newList, okList):
        if not okList:
            return newList
            
        for item in newList:
            if item not in okList:
                newList.remove(item)
            
        return newList