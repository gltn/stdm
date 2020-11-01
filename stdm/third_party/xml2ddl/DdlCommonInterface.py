#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
import re, os
from NamingConvention import *

class DdlCommonInterface:
    """ Class which has the common interfaces for creating DDL.  
    
      You normally don't use this class alone but derive a subclass which will handle how
      your class differs from the standard. (Not that DdlCommonInterface really follows a standard)
    """
    def __init__(self, strDbms):
        self.dbmsType = strDbms
        self.params = {
            # Table
            'add_table'       : ['CREATE TABLE %(table_name)s (\n\t%(col_defs)s%(primary_keys)s)%(extra)s'],
            'drop_table'      : ['DROP TABLE %(table_name)s%(cascade)s'],
            'rename_table'    : ['ALTER TABLE %(table_name)s RENAME TO %(new_table_name)s'],
            'table_desc'      : ["COMMENT ON TABLE %(table)s IS %(desc)s"],
            # Column
            'add_column'      : ['ALTER TABLE %(table_name)s ADD %(column_name)s %(column_type)s'],
            'drop_column'     : ['ALTER TABLE %(table_name)s DROP %(column_name)s'],
            'rename_column'   : ['ALTER TABLE %(table_name)s RENAME %(old_col_name)s TO %(new_col_name)s'],
            'change_col_type' : ['ALTER TABLE %(table_name)s ALTER %(column_name)s TYPE %(column_type)s'],
            'column_desc'     : ["COMMENT ON COLUMN %(table)s.%(column)s IS %(desc)s"],
            # Column Default
            'drop_default'    : ['ALTER TABLE %(table_name)s ALTER %(column_name)s DROP DEFAULT'],
            'alter_default'   : ['ALTER TABLE %(table_name)s ALTER %(column_name)s SET DEFAULT %(new_default)s'],
            # Relation
            'add_relation'    : ['ALTER TABLE %(tablename)s ADD CONSTRAINT %(constraint)s FOREIGN KEY (%(thiscolumn)s) REFERENCES %(othertable)s(%(fk)s)%(ondelete)s%(onupdate)s'],
            'drop_relation'   : ['ALTER TABLE %(tablename)s DROP CONSTRAINT %(constraintname)s'],
            # View
            'create_view'     : ['CREATE VIEW %(viewname)s AS %(contents)s'],
            'drop_view'       : ['DROP VIEW %(viewname)s'],
            # Function
            'create_function' : ["CREATE FUNCTION %(functionname)s(%(arguments)s) RETURNS %(returns)s AS '\n%(contents)s'%(language)s"],
            'drop_function'   : ['DROP FUNCTION %(functionname)s(%(params)s)'],
            # Key Constraint
            'add_key_constraint'  : ['ALTER TABLE %(table_name)s ADD CONSTRAINT %(pk_constraint)s PRIMARY KEY (%(keys)s)'],
            'drop_key_constraint' : ['ALTER TABLE %(table_name)s DROP CONSTRAINT %(constraint_name)s'],
            # Index
            'add_index'       : ['CREATE INDEX %(index_name)s ON %(table_name)s (%(col_names)s)'],
            'drop_index'      : ['DROP INDEX %(index_name)s'],
            
            'unquoted_id'     : re.compile(r'^[A-Za-z][A-Za-z0-9_]+$'),
            'max_id_len'      : { 'default' : 256 },
            'has_auto_increment' : False,
            'keywords'        : [ 'NULL', 'SELECT', 'FROM' ],
            'quote_l'         : '"',
            'quote_r'         : '"',
            'drop_constraints_on_col_rename' : False,
            'drop_table_has_cascade' : False, # Test
            'can_change_table_comment' : True,
        }

    # Tables
    def addTable(self, strTableName, colDefs, keys, strTableStuff, diffs):
        info = {
            'table_name' : self.quoteName(strTableName),
            'col_defs'   : ',\n\t'.join(colDefs),
            'primary_keys' : '\n',
            'extra'      : strTableStuff,
        }
        if len(keys) > 0:
            info['primary_keys'] = ',\n\tCONSTRAINT pk_%s PRIMARY KEY (%s)' % (info['table_name'], ',\n\t'.join(keys))

        for strDdl in self.params['add_table']:
            diffs.append(('Create Table', strDdl % info))

        
    def dropTable(self, strTableName, strCascade, diffs):
        info = {
            'table_name' : self.quoteName(strTableName),
            'cascade'    : strCascade,
        }
        
        for strDdl in self.params['drop_table']:
            diffs.append(('Drop Table', strDdl % info))

    def renameTable(self, strTableOld, strTableNew, diffs):
        info = {
            'table_name' : self.quoteName(strTableOld), 
            'new_table_name' : self.quoteName(strTableNew),
        }
        
        for strDdl in self.params['rename_table']:
            diffs.append(('Rename Table', strDdl % info) )

    def addTableComment(self, tableName, desc, ddls):
        info = {
            'table' : tableName,
            'desc' : self.quoteString(desc),
        }
        
        for strDdl in self.params['table_desc']:
            ddls.append(('Add Table Comment', strDdl % info ))
    
    # Columns
    def addColumn(self, strTableName, strColName, strColType, nAfter, diffs):
        """ nAfter not used yet """
        
        info = { 
            'table_name' : self.quoteName(strTableName),
            'column_name' : self.quoteName(strColName),
            'column_type' : strColType
        }
        
        for strDdl in self.params['add_column']:
            diffs.append(('Add Column', strDdl % info))
        
    def dropColumn(self, strTableName, strColName, diffs):
        info = { 
            'table_name' : self.quoteName(strTableName),
            'column_name' : self.quoteName(strColName),
        }
        
        for strDdl in self.params['drop_column']:
            diffs.append(('Drop Column', strDdl % info))
        
    def renameColumn(self, strTableName, strOldName, strNewName, strNewColType, diffs):
        info = {
            'table_name'   : self.quoteName(strTableName),
            'old_col_name' : self.quoteName(strOldName),
            'new_col_name' : self.quoteName(strNewName),
            'column_type'  : strNewColType,
        }
        
        for strDdl in self.params['rename_column']:
            diffs.append(('Rename column', strDdl % info))
        

    def addColumnComment(self, strTableName, strColumnName, strDesc, strColType, ddls):
        info = {
            'table' : strTableName,
            'column' : strColumnName,
            'desc' :  self.quoteString(strDesc),
            'type' : strColType + ' ',
        }
        for strDdl in self.params['column_desc']:
            ddls.append(('Add Column comment', strDdl % info ))

    def changeColumnComment(self, strTableName, strColumnName, strDesc, strColType, ddls):
        self.addColumnComment(strTableName, strColumnName, strDesc, strColType, ddls)

    # Primary Keys
    def addKeyConstraint(self, strTableName, keylist, diffs):
        info = {
            'table_name'    : self.quoteName(strTableName), 
            'pk_constraint' : self.quoteName(getPkContraintName(strTableName)),
            'keys'          : ', '.join(keylist),
        }
        for strDdl in self.params['add_key_constraint']:
            diffs.append( ('Add key constraint', strDdl % info))

    def dropKeyConstraint(self, strTable, strConstraintName, diffs):
        info = {
            'table_name' : strTable,
            'constraint_name' : strConstraintName,
        }
        for strDdl in self.params['drop_key_constraint']:
            diffs.append(('Drop key constraint', strDdl % info))
    
    # Indexes
    def addIndex(self, strTableName, strIndexName, cols, ddls):
        cols = [self.quoteName(col) for col in cols]
        info = {
            'index_name' : self.quoteName(strIndexName),
            'table_name' : self.quoteName(strTableName),
            'col_names'  : ', '.join(cols),
        }
        for strDdl in self.params['add_index']:
            ddls.append(('Add Index', strDdl  % info))


    def deleteIndex(self, strTableName, strIndexName, diffs):
        info = { 
            'index_name' : self.quoteName(strIndexName),
            'table_name' : strTableName,
        }
        for strDdl in self.params['drop_index']:
            diffs.append(('Drop Index', strDdl % info))

    def renameIndex(self, strTableName, strOldIndexName, strNewIndexName, cols, diffs):
        self.deleteIndex(strTableName, strOldIndexName, diffs)
        self.addIndex(strTableName, strNewIndexName, cols, diffs)

    def changeIndex(self, strTableName, strOldIndexName, strNewIndexName, cols, diffs):
        self.deleteIndex(strTableName, strOldIndexName, diffs)
        self.addIndex(strTableName, strNewIndexName, cols, diffs)

    # Relations
    def addRelation(self, strTableName, strRelationName, strColumn, strFkTable, strFk, strOnDelete, strOnUpdate, diffs):
        info = {
            'tablename'  : self.quoteName(strTableName),
            'thiscolumn' : self.quoteName(strColumn),
            'othertable' : self.quoteName(strFkTable),
            'constraint' : self.quoteName(strRelationName),
            'ondelete' : '',
            'onupdate' : '',
        }
        if len(strFk) > 0:
            info['fk'] = strFk
        else:
            info['fk'] = info['thiscolumn']
        
        if len(strOnDelete) > 0:
            action = strOnDelete.upper()
            if action == 'SETNULL':
                action = 'SET NULL'
            info['ondelete'] = ' ON DELETE ' + action
        
        if len(strOnUpdate) > 0:
            action = strOnUpdate.upper()
            if action == 'SETNULL':
                action = 'SET NULL'
            info['onupdate'] = ' ON UPDATE ' + action
            
        for strDdl in self.params['add_relation']:
            diffs.append(('Add Relation', strDdl % info))

    def dropRelation(self, strTableName, strRelationName, diffs):
        info = {
            'tablename': self.quoteName(strTableName),
            'constraintname' : strRelationName,
        }
        
        for strDdl in self.params['drop_relation']:
            diffs.append(('Drop Relation', strDdl % info))

    # Autoincrement
    def addAutoIncrement(self, strTableName, strColName, strDefault, strPreDdl, strPostDdl):
        info = {
            'table_name' : strTableName,
            'col_name'   : strColName,
            'seq_name'   : getSeqName(strTableName, strColName),
            'ai_trigger' : getAiTriggerName(strTableName, strColName),
        }
        
        if self.params['has_auto_increment']:
            return ' AUTO_INCREMENT'
    
        if self.dbmsType == 'firebird':
            strPreDdl.append(('Add Autoincrement Generator',
                'CREATE GENERATOR %(seq_name)s' % info))
            strPostDdl.append(('Add Autoincrement Trigger',
                """CREATE TRIGGER %(ai_trigger)s FOR %(table_name)s
                BEFORE INSERT AS
                BEGIN
                    NEW.%(col_name)s = GEN_ID(%(seq_name)s, 1);
                END""" % info))
            return ''
        
        strPreDdl.append(('Add Autoincrement', 
            'CREATE SEQUENCE %(seq_name)s' % info))
            
        if strDefault:
            print "Error: can't have a default and autoincrement together"
            return ''
            
        return " DEFAULT nextval('%(seq_name)s')" % info

    def dropAutoIncrement(self, strTableName, col, diffs):
        # Todo get rid of the col
        
        strColName = col.get('name')
        info = {
            'table_name' : strTableName,
            'col_name'   : strColName,
            'seq_name'   : getSeqName(strTableName, strColName),
            'ai_trigger' : getAiTriggerName(strTableName, strColName),
        }
        if self.params['has_auto_increment']:
            self.doChangeColType(strTableName, strColName, self.retColTypeEtc(col), diffs)
            return

        
        if self.dbmsType == 'firebird':
            diffs.append(('Drop Autoincrement Trigger', 
                'DROP TRIGGER %(ai_trigger)s' % info))
            
            diffs.append(('Drop Autoincrement', 
                'DROP GENERATOR %(seq_name)s' % info))
            return
            
        # For postgres
        diffs.append(('Drop Autoincrement', 
            'DROP SEQUENCE %(seq_name)s' % info))
        
        self.dropDefault(strTableName, col, diffs)
    
    # Column default
    def dropDefault(self, strTableName, col, diffs):
        info = {
            'table_name' : self.quoteName(strTableName),
            'column_name' : self.quoteName(col.get('name')),
            'column_type' : self.retColTypeEtc(col),
        }
        
        for strDdl in self.params['drop_default']:
            diffs.append(('Drop Default', strDdl % info))

    def changeColDefault(self, strTableName, strColumnName, strNewDefault, strColType, diffs):
        info = {
            'table_name' : self.quoteName(strTableName),
            'column_name' : self.quoteName(strColumnName),
            'new_default' : strNewDefault,
            'column_type' : strColType,
        }
        
        for strDdl in self.params['alter_default']:
            diffs.append(('Change Default',  strDdl % info))

    # Column type
    def doChangeColType(self, strTableName, strColumnName, strNewColType, diffs):
        info = {
            'table_name' : strTableName,
            'column_name' : strColumnName,
            'column_type' : strNewColType,
        }
        
        for strDdl in self.params['change_col_type']:
            diffs.append(('Change Col Type', strDdl % info))

    def renameView(self, strOldViewName, strNewViewName, newDefinition, newAttribs, diffs):
        self.dropView(strOldViewName, diffs)
        self.addView(strNewViewName, newDefinition, newAttribs, diffs)
    
    def dropView(self, strOldViewName, diffs):
        info = {
            'viewname' : self.quoteName(strOldViewName),
        }
        for strDdl in self.params['drop_view']:
            diffs.append(('Drop view', strDdl % info ))
    
    def addView(self, strNewViewName, strContents, attribs, diffs):
        info = {
            'viewname' : self.quoteName(strNewViewName),
            'contents' : strContents,
        }
        for strDdl in self.params['create_view']:
            diffs.append(('Add view',  strDdl % info ))
    
    def updateView(self, strViewName, strContents, attribs, diffs):
        self.addView(strViewName, strContents, attribs, diffs)

    # Function stuff
    def renameFunction(self, strOldFunctionName, strNewFunctionName, newDefinition, newAttribs, diffs):
        self.dropFunction(strOldFunctionName, newAttribs['arguments'].split(','), diffs)
        self.addFunction(strNewFunctionName, newAttribs['arguments'].split(','), newAttribs['returns'], newDefinition, newAttribs, diffs)
    
    def dropFunction(self, strOldFunctionName, argumentList, diffs):
        if argumentList:
            paramList = [arg.split()[-1] for arg in argumentList]
        else:
            paramList = ''
        info = {
            'functionname' : self.quoteName(strOldFunctionName),
            'params'       : ', '.join(paramList),
        }
        for strDdl in self.params['drop_function']:
            diffs.append(('Drop function', strDdl % info ))
    
    def addFunction(self, strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs):
        info = {
            'functionname' : self.quoteName(strNewFunctionName),
            'arguments'  : ', '.join(argumentList),
            'returns'  : strReturn,
            'contents' : strContents.replace("'", "''"),
        }
        if 'language' not in attribs:
            info['language'] = ' LANGUAGE plpgsql'
        else:
            info['language'] = ' LANGUAGE %s' % (attribs['language'])

        for strDdl in self.params['create_function']:
            diffs.append(('Add function',  strDdl % info))
    
    def updateFunction(self, strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs):
        self.dropFunction(strNewFunctionName, argumentList, diffs)
        self.addFunction(strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs)

    def retColTypeEtc(self, col):
        strNull = ''
        if 'null' in col:
            strVal = col.get('null')
            if re.compile('not|no', re.IGNORECASE).search(strVal):
                strNull = ' NOT NULL'

        strDefault = ''
        if 'default' in col:
            strDefault = ' DEFAULT ' + col.get('default')
        elif self.dbmsType == 'mysql' and col.get('type') == 'timestamp':
            # MySQL silently sets the default to CURRENT_TIMESTAMP
            strRet += ' DEFAULT null'

        strType = col.get('type', None)
        strSize = col.get('size', None)
        strPrec = col.get('precision', None)
        
        if strPrec:
            strRet = '%s(%s, %s)%s%s' % (strType, strSize, strPrec, strDefault, strNull)
        elif strSize:
            strRet = '%s(%s)%s%s' % (strType, strSize, strDefault, strNull)
        else:
            strRet = '%s%s%s' % (strType, strDefault, strNull)

        return strRet

    def quoteName(self, strName):
        bQuoteName = False
        
        if not self.params['unquoted_id'].match(strName):
            bQuoteName = True

        if strName.upper() in self.params['keywords']:
            bQuoteName = True
        
        if not bQuoteName:
            if strName[0] == '"' and strName[-1] == '"':
                # Already quoted.
                bQuoteName = False

        if bQuoteName:
            return self.params['quote_l'] + strName + self.params['quote_r']
        
        return strName

    def quoteString(self, strStr):
        return "'%s'" % (strStr.replace("'", "''"))

# Here we list the known subclasses
g_dbTypes = ['postgres', 'postgres7', 'mysql', 'mysql4', 'oracle', 'firebird']