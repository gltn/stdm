import re, os, sys
import xml2ddl
import copy
import optparse
from xml.dom.minidom import parse, parseString
from ddlInterface import createDdlInterface, attribsToDict
from NamingConvention import *

__author__ = "Scott Kirkwood (scott_kirkwood at berlios.com)"
__keywords__ = ['XML', 'DML', 'SQL', 'Databases', 'Agile DB', 'ALTER', 'CREATE TABLE', 'GPL']
__licence__ = "GNU Public License (GPL)"
__longdescr__ = ""
__url__ = 'http://xml2dml.berlios.de'
__version__ = "$Revision: 0.2 $"

"""
This is the core routines to perform a difference on two XML files and output the DML that is
required to bring one Schema up-to-date with the other schema.

TODO:
    - Unique constraint
    - check constraint
"""

class DiffXml2Ddl:
    def __init__(self):
        self.xml2ddl = xml2ddl.Xml2Ddl()
        self._defaults()
        self.reset()
        
    def reset(self):
        self.strTableName = None
        self.diffs = []
        self.xml2ddl.reset()
        
    def _defaults(self):
        self.dbmsType = 'postgres'
        self.params = {
            'drop_constraints_on_col_rename' : False,
            'drop_table_has_cascade' : False, # test
            'can_change_table_comment' : True,
        }
    
    def setDbms(self, dbmsType):
        self._defaults()
        self.reset()
        
        self.dbmsType = dbmsType.lower()
        
        self.xml2ddl.setDbms(self.dbmsType)
        self.ddli = createDdlInterface(self.dbmsType)
        
        self.params['drop_constraints_on_col_rename'] = self.ddli.params['drop_constraints_on_col_rename']
        self.params['drop_table_has_cascade']   = self.ddli.params['drop_table_has_cascade']
        self.params['can_change_table_comment'] = self.ddli.params['can_change_table_comment'] 
            

    def changeAutoIncrement(self, strTableName, old, new):
        # Remove old, and new
        strOldAuto = old.getAttribute('autoincrement').lower()
        strNewAuto = new.getAttribute('autoincrement').lower()
        if strOldAuto != strNewAuto:
            if strNewAuto == 'yes':
                # Hmm, if we created the column the autoincrement would already be there anyway.
                pass
                #print "Add Autoincrement TODO"
            else:
                self.ddli.dropAutoIncrement(strTableName, attribsToDict(old), self.diffs)

    def changeCol(self, strTableName, old, new):
        self.changeColType(strTableName, attribsToDict(old), attribsToDict(new))
        
        self.changeAutoIncrement(strTableName, old, new)
        
        self.changeColDefaults(strTableName, old, new)
        
        self.changeColComments(strTableName, old, new)

    def changeColType(self, strTableName, old, new):
        oldDefault = None
        if 'default' in old:
            oldDefault = old.get('default')
            del old['default']

        newDefault = None
        if 'default' in new:
            newDefault = new.get('default')
            del new['default']
        strOldColType = self.ddli.retColTypeEtc(old)
        strNewColType = self.ddli.retColTypeEtc(new)
        
        if oldDefault:
            old['default'] = oldDefault

        if newDefault:
            new['default'] = newDefault
        
        if self.normalizedColType(strNewColType) != self.normalizedColType(strOldColType):
            #print "Different\n%s\n%s" % (self.normalizedColType(strNewColType), self.normalizedColType(strOldColType))
            self.ddli.doChangeColType(strTableName, old.get('name'), strNewColType, self.diffs)

    def normalizedColType(self, strColTypeEtc):
        if not self.bGenerated:
            return strColTypeEtc
        
        # The purpose here is to compare two column types and see if the appear to be the same (essentially).
        # I'm not trying to convert them to SQL9x which would make more sense, perhaps.
        strColTypeEtc = strColTypeEtc.lower();
        strColTypeEtc = strColTypeEtc.replace('integer', 'int')
        strColTypeEtc = strColTypeEtc.replace('numeric', 'decimal')
        strColTypeEtc = strColTypeEtc.replace('double precision', 'float')
        if strColTypeEtc == 'number' or strColTypeEtc == 'decimal':
            strColTypeEtc = 'int'
        else:
            strColTypeEtc = strColTypeEtc.replace('number', 'decimal') # Oracle
        strColTypeEtc = strColTypeEtc.replace('number ', 'int ')
        strColTypeEtc = strColTypeEtc.replace('decimal ', 'int ')
        strColTypeEtc = strColTypeEtc.replace('varchar2', 'varchar') # Oracle
        return strColTypeEtc
    
    def changeColDefaults(self, strTableName, old, new):
        strOldDefault = old.getAttribute('default')
        strNewDefault = new.getAttribute('default')
        if strNewDefault != strOldDefault:
            self.ddli.changeColDefault(strTableName, getColName(new), strNewDefault, self.ddli.retColTypeEtc(attribsToDict(new)), self.diffs)

    def changeColComments(self, strTableName, old, new):
        # Check for difference in comments.
        strNewComment = safeGet(new, 'desc')
        strOldComment = safeGet(old, 'desc')
        if strNewComment and strNewComment != strOldComment:
            # Fix to delete comments?
            self.ddli.changeColumnComment(strTableName, getColName(new), strNewComment, self.ddli.retColTypeEtc(attribsToDict(new)), self.diffs)
            

    def renameColumn(self, strTableName, old, new):
        strOldName = getColName(old)
        strNewName = getColName(new)
        
        if self.params['drop_constraints_on_col_rename']:
            self.dropRelatedConstraints(strTableName, strOldName)
            
        columnType = self.ddli.retColTypeEtc(attribsToDict(new))
        self.ddli.renameColumn(strTableName, strOldName, strNewName, columnType, self.diffs)
        
        if self.params['drop_constraints_on_col_rename']:
            self.rebuildRelatedConstraints(strTableName, strNewName)
        
    def rebuildRelatedConstraints(self, strTable, strColumnName):
        tables = self.new_xml.getElementsByTagName('table')
        for table in tables:
            strCurTableName = table.getAttribute('name')
            if strCurTableName == strTable:
                # Find if the PK constraint is on this table
                for col in table.getElementsByTagName('column'):
                    strCurColName = getColName(col)
                    if strCurColName == strColumnName:
                        if col.hasAttribute('key'):
                            self.addKeyConstraint(table)
                            break
            else:
                relations = table.getElementsByTagName('relation')
                for relation in relations:
                    strCurTableName = relation.getAttribute('table')
                    if strCurTableName == strTable:
                        strCurColName = relation.getAttribute('name')
                        
                        fk = safeGet(relation, 'fk', strCurColName)
                        
                        if fk == strColumnName:
                            self.addRelation(getTableName(table), relation)

    def addKeyConstraint(self, tableDoc):
        """ The Primary Key constraint is always called pk_<tablename> and can't be changed """
        
        strTableName = getTableName(tableDoc)
        columns = tableDoc.getElementsByTagName('column')
        keys = []
        for column in columns:
            if column.hasAttribute('key'):
                keys.append(getColName(column))
                
        self.ddli.addKeyConstraint(strTableName, keys, self.diffs)
        
    def dropKeyConstraint(self, strTable, col, diffs):
        self.ddli.dropKeyConstraint(strTable, 'pk_%s' % (strTable), diffs)
    
    def addRelation(self, strTable, relation):
        self.ddli.addRelation(strTable, relation, self.diffs)
        
    def dropRelatedConstraints(self, strTable, strColumnName = None):
        if strColumnName != None:
            self._dropRelatedConstraints(strTable, strColumnName)
        else:
            table = self.findTable(self.old_xml.getElementsByTagName('table'), strTable)
            columns = table.getElementsByTagName('column')
            for column in columns:
                self._dropRelatedConstraints(strTable, getColName(column))
        
    def _dropRelatedConstraints(self, strTable, strColumnName):
        tables = self.old_xml.getElementsByTagName('table')
        
        relationLst = []
        pkList = []
        # need to sometimes reverse the order
        for table in tables:
            strCurTableName = getTableName(table)
            if strCurTableName == strTable:
                # Find if the PK constraint is on this table
                for col in table.getElementsByTagName('column'):
                    strCurColName = getColName(col)
                    if strCurColName == strColumnName:
                        if col.hasAttribute('key'):
                            self.dropKeyConstraint(strTable, col, pkList)
                            break
            else:
                relations = table.getElementsByTagName('relation')
                for relation in relations:
                    strCurTableName = relation.getAttribute('table')
                    if strCurTableName == strTable:
                        strCurColName = relation.getAttribute('column')
                        
                        fk = safeGet(relation, 'fk', strCurColName)
                        
                        if len(strCurColName) > 0 and fk == strColumnName:
                            relationLst.append(self.dropRelation(getTableName(table), relation))
        
        for relation in relationLst:
            self.diffs.append(relation)
        
        for pk in pkList:
            self.diffs.append(pk)
        
    def dropRelatedSequences(self, strTableName):
        if self.dbmsType == 'firebird' or self.dbmsType.startswith('postgres'):
            table = self.findTable(self.old_xml.getElementsByTagName('table'), strTableName)
            columns = table.getElementsByTagName('column')
            for column in columns:
                self._dropRelatedSequence(strTableName, column)
            
            return
        
    def _dropRelatedSequence(self, strTableName, col):
        if col.getAttribute('autoincrement').lower() == 'yes':
            self.ddli.dropAutoIncrement(strTableName, attribsToDict(col), self.diffs)


    def addColumn(self, strTableName, new, nAfter):
        """ nAfter not used yet """
        
        self.ddli.addColumn(strTableName, getColName(new), self.ddli.retColTypeEtc(attribsToDict(new)), nAfter, self.diffs)

    def dropColumn(self, strTableName, oldCol):
        self.ddli.dropColumn(strTableName, getColName(oldCol), self.diffs)

    def diffTable(self, strTableName, tbl_old, tbl_new):
        """ strTableName is there just to be consistant with the other diff... """
        self.strTableName = getTableName(tbl_new)
        
        self.diffColumns(tbl_old, tbl_new)
        self.diffRelations(tbl_old, tbl_new)
        self.diffIndexes(tbl_old, tbl_new)
        self.diffTableComment(tbl_old, tbl_new)

    def diffTableComment(self, tbl_old, tbl_new):
        strNewComment = safeGet(tbl_new, 'desc')
        strOldComment = safeGet(tbl_old, 'desc')

        if self.params['can_change_table_comment'] == False:
            return
            
        if strOldComment != strNewComment and strNewComment:
            self.ddli.addTableComment(self.strTableName, strNewComment, self.diffs)

    def diffColumns(self, old, new):
        self.diffSomething(old, new, 'column', self.renameColumn,  self.changeCol, self.addColumn, self.dropColumn, self.findColumn, getColName)

    def diffSomething(self, old, new, strTag, renameFunc, changeFunc, addFunc, deleteFunc, findSomething, getName):
        newXs = new.getElementsByTagName(strTag)
        oldXs = old.getElementsByTagName(strTag)
        
        nOldIndex = 0
        skipXs = []
        for nIndex, newX in enumerate(newXs):
            strnewXName = getName(newX)
            oldX = findSomething(oldXs, strnewXName)
            
            if oldX:
                changeFunc(self.strTableName, oldX, newX)
            else:
                if newX.hasAttribute('oldname'):
                    strOldName = newX.getAttribute('oldname')
                    oldX = findSomething(oldXs, strOldName)
                    
                if oldX:
                    changeFunc(self.strTableName, oldX, newX)
                    renameFunc(self.strTableName, oldX, newX)
                    skipXs.append(strOldName)
                    # Just in case user changed name and the type as well.
                else:                    
                    addFunc(self.strTableName, newX, nIndex)
            
        newXs = new.getElementsByTagName(strTag)
        oldXs = old.getElementsByTagName(strTag)
        for nIndex, oldX in enumerate(oldXs):
            stroldXName = getName(oldX)
            if stroldXName in skipXs:
                continue
            
            newX = findSomething(newXs, stroldXName)
            
            if not newX:
                try:
                    strTableName = getTableName(old)
                except:
                    strTableName = None
                
                deleteFunc(strTableName, oldX)
        
    def getColName(self, col):
        return getColName(col)
        
    def findColumn(self, columns, strColName):
        strColName = strColName.lower()
        for column in columns:
            strCurColName = getColName(column).lower()
            if strCurColName == strColName:
                return column
            
        return None
        
    def getTableName(self, table):
        return table.getAttribute('name')

    def findTable(self, tables, strTableName):
        strTableName = strTableName.lower()
        for tbl in tables:
            strCurTableName = tbl.getAttribute('name').lower()
            if strCurTableName == strTableName:
                return tbl
            
        return None
        
    def diffIndexes(self, old_xml, new_xml):
        self.diffSomething(old_xml, new_xml, 'index', self.renameIndex, self.changeIndex, self.insertIndex, self.deleteIndex, self.findIndex, self.getIndexName)

    def getIndexName(self, index):
        return getIndexName(self.strTableName, index)
        
    def renameIndex(self, strTableName, old, new):
        strColumns = new.getAttribute("columns")
        self.ddli.renameIndex(strTableName, 
            getIndexName(strTableName, old), 
            getIndexName(strTableName, new), 
            strColumns.split(','), 
            self.diffs)
    
    def deleteIndex(self, strTableName, old):
        strIndexName = getIndexName(strTableName, old)
        self.ddli.deleteIndex(strTableName, strIndexName, self.diffs)

    def changeIndex(self, strTableName, old, new):
        strColumnsOld = old.getAttribute('columns').replace(' ', '').lower()
        strColumnsNew = new.getAttribute('columns').replace(' ', '').lower()
        if strColumnsOld != strColumnsNew:
            self.ddli.changeIndex(strTableName,
                getIndexName(strTableName, old), 
                getIndexName(strTableName, new), 
                strColumnsNew.split(','), 
                self.diffs)
    
    def insertIndex(self, strTableName, new, nIndex):
        strColumns = new.getAttribute("columns")
        self.ddli.addIndex(self.strTableName, getIndexName(strTableName, new), strColumns.split(','), self.diffs)

    def findIndex(self, indexes, strIndexName):
        strIndexName = strIndexName.lower()
        for index in indexes:
            strCurIndexName = self.getIndexName(index).lower()
            if strCurIndexName == strIndexName:
                return index
            
        return None
        
    def diffRelations(self, old_xml, new_xml):
        self.diffSomething(old_xml, new_xml, 'relation', self.renameRelation, self.changeRelation, self.insertRelation, self.dropRelation, self.findRelation, getRelationName)

    def renameRelation(self, strTableName, old, new):
        # TODO put in ddlinterface
        self.dropRelation(strTableName, old)
        self.insertRelation(strTableName, new, -1)
    
    def changeRelation(self, strTableName, old, new):
        strColumnOld = old.getAttribute('column').lower()
        strColumnNew = new.getAttribute('column').lower()
        
        strTableOld = old.getAttribute('table').lower()
        strTableNew = new.getAttribute('table').lower()
        
        strFkOld = old.getAttribute('fk').lower()
        strFkNew = old.getAttribute('fk').lower()
        
        strDelActionOld = old.getAttribute('ondelete').lower()
        strDelActionNew = new.getAttribute('ondelete').lower()

        strUpdateActionOld = old.getAttribute('onupdate').lower()
        strUpdateActionNew = old.getAttribute('onupdate').lower()
        
        if len(strFkOld) == 0:
            strFkOld = strColumnOld
        
        if len(strFkNew) == 0:
            strFkNew = strColumnNew
        
        if strColumnOld != strColumnNew or strTableOld != strTableNew or strFkOld != strFkNew or strDelActionOld != strDelActionNew or strUpdateActionOld != strUpdateActionNew:
            #print "Col %s != %s or\nTable %s != %s, or\nFk %s != %s or\nDel %s != %s or\nUpdate %s != %s" % (strColumnOld, strColumnNew, strTableOld, strTableNew, strFkOld, strFkNew, strDelActionOld, strDelActionNew, strUpdateActionOld, strUpdateActionNew)
            self.dropRelation(strTableName, old)
            self.insertRelation(strTableName, new, 0)
    
    def insertRelation(self, strTableName, old, nIndex):
        strRelationName = getRelationName(old)
        strFk = old.getAttribute('fk')
        strOnDelete = old.getAttribute('ondelete')
        strOnUpdate = old.getAttribute('onupdate')
        strFkTable = old.getAttribute('table')
        strColumn = old.getAttribute('column')
        self.ddli.addRelation(strTableName, strRelationName, strColumn, strFkTable, strFk, strOnDelete, strOnUpdate, self.diffs)

    def dropRelation(self, strTableName, old):
        strRelationName = getRelationName(old)
        self.ddli.dropRelation(strTableName, strRelationName, self.diffs)

    def findRelation(self, relations, strRelationName):
        strRelationName = strRelationName.lower()
        for relation in relations:
            strCurRelationName = getRelationName(relation)
            if strCurRelationName.lower() == strRelationName:
                return relation
        
        return None
        
    def createTable(self, strTableName, xml, nIndex):
        self.xml2ddl.reset()
        self.xml2ddl.params['drop-tables'] = False

        self.xml2ddl.createTable(xml)
        self.diffs.extend(self.xml2ddl.ddls)

    def dropTable(self, strTableName, xml):
        self.strTableName = xml.getAttribute('name')
        strCascade = ''
        if self.params['drop_table_has_cascade']:
            strCascade = ' CASCADE'
        else:
            self.dropRelatedConstraints(self.strTableName)

        self.dropRelatedSequences(self.strTableName)
        
        self.ddli.dropTable(self.strTableName, strCascade, self.diffs)
        
    def renameTable(self, strTableName, tblOldXml, tblNewXml):
        strTableOld = tblOldXml.getAttribute('name')
        strTableNew = tblNewXml.getAttribute('name')
        
        self.ddli.renameTable(strTableOld, strTableNew, self.diffs)

    # View stuff
    def renameView(self, ignore, old, new):
        attribs = attribsToDict(new)
        strDefinition = new.firstChild.nodeValue.rstrip()
        
        if self.inDbms(new):
            self.ddli.renameView(old.getAttribute('name'), new.getAttribute('name'), strDefinition, attribs, self.diffs)
        
    def diffView(self, ignore, oldView, newView):
        strOldContents = oldView.firstChild.nodeValue.rstrip()
        strNewContents = newView.firstChild.nodeValue.rstrip()
        
        if not self.inDbms(newView):
            return
            
        if strOldContents != strNewContents:
            attribs = attribsToDict(newView)
            strDefinition = newView.firstChild.nodeValue.rstrip()
            
            self.ddli.updateView(newView.getAttribute('name'), strDefinition, attribs, self.diffs)
        
    def createView(self, ignore, new, nIndex):
        attribs = attribsToDict(new)
        strDefinition = new.firstChild.nodeValue.rstrip()
        
        if self.inDbms(new):
            self.ddli.addView(new.getAttribute('name'), strDefinition, attribs, self.diffs)
        
    def dropView(self, ignore, view):
        if self.inDbms(view):
            self.ddli.dropView(view.getAttribute('name'), self.diffs)
        
    def findView(self, views, strViewName):
        strViewName = strViewName.lower()
        for view in views:
            strCurViewName = view.getAttribute('name').lower()
            if strCurViewName == strViewName:
                return view
            
        return None
        
    def getViewName(self, node):
        return node.getAttribute('name')

    # function stuff
    def renameFunction(self, ignore, old, new):
        attribs = attribsToDict(new)
        strDefinition = new.firstChild.nodeValue.strip()
        
        if self.inDbms(new):
            self.ddli.renameFunction(old.getAttribute('name'), new.getAttribute('name'), strDefinition, attribs, self.diffs)
        
    def diffFunction(self, ignore, oldFunction, newFunction):
        strOldContents = oldFunction.firstChild.nodeValue.strip()
        strNewContents = newFunction.firstChild.nodeValue.strip()
        
        if not self.inDbms(newFunction):
            return
        
        if strOldContents != strNewContents:
            attribs = attribsToDict(newFunction)
            strDefinition = newFunction.firstChild.nodeValue.strip()
            
            self.ddli.updateFunction(newFunction.getAttribute('name'), 
                newFunction.getAttribute('arguments').split(','), newFunction.getAttribute('returns'), strDefinition, attribs, self.diffs)
        
    def createFunction(self, ignore, new, nIndex):
        attribs = attribsToDict(new)
        strDefinition = new.firstChild.nodeValue.strip()
        
        # strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs
        argumentList = [arg.strip() for arg in new.getAttribute('arguments').split(',')]
        
        if self.inDbms(new):
            self.ddli.addFunction(new.getAttribute('name'), argumentList, new.getAttribute('returns'), strDefinition.strip(), attribs, self.diffs)
        
    def dropFunction(self, ignore, func):
        if self.inDbms(func):
            self.ddli.dropFunction(func.getAttribute('name'), func.getAttribute('arguments').split(','), self.diffs)
        
    def findFunction(self, funcs, strFunctionName):
        strFunctionName = strFunctionName.lower()
        for func in funcs:
            strCurFunctionName = func.getAttribute('name').lower()
            if strCurFunctionName == strFunctionName and self.inDbms(func):
                return func
            
        return None
        
    def getFunctionName(self, node):
        return node.getAttribute('name')

    def diffFiles(self, strOldFilename, strNewFilename):
        self.old_xml = xml2ddl.readMergeDict(strOldFilename) # parse an XML file by name
        self.new_xml = xml2ddl.readMergeDict(strNewFilename)
        
        self.diffTables(self.old_xml, self.new_xml)
        
        self.old_xml.unlink()
        self.new_xml.unlink()
        
        return self.diffs

    def diffTables(self, old_xml, new_xml):
        self.old_xml = old_xml
        self.new_xml = new_xml
        
        self.bGenerated = False
        try:
            schema = new_xml.getElementsByTagName('schema')[0]
        except:
            schema = new_xml
            
        if schema.hasAttribute('generated'):
            self.bGenerated = True
            if schema.getAttribute('generated').lower() == 'no':
                self.bGenerated = False
            
        
        self.diffSomething(old_xml, new_xml, 'table', self.renameTable,  self.diffTable, self.createTable, self.dropTable, self.findTable, self.getTableName)

        self.diffSomething(old_xml, new_xml, 'view', self.renameView,  self.diffView, self.createView, self.dropView, self.findView, self.getViewName)

        self.diffSomething(old_xml, new_xml, 'function', self.renameFunction,  self.diffFunction, self.createFunction, self.dropFunction, self.findFunction, self.getFunctionName)

        self.sortDiffs()
        return self.diffs

    def sortDiffs(self):
        self.diffs.sort(self.ddlSorter)
    
    def ddlSorter(self, a, b):
        orderDict = {
            'Create Table'                        :  0,
            'Drop Table'                          :  0,
            'Rename Table'                        :  0,
            'Add Table Comment'                   :  0,
            'Add Column'                          :  0,
            'Drop Column'                         :  0,
            'Rename column'                       :  0,
            'Add view'                            :  0,
            'Drop view'                           :-99,
            'Add Column comment'                  :  0,
            'Add key constraint'                  :  0,
            'Drop key constraint'                 :  0,
            'Add Index'                           :  0,
            'Drop Index'                          : -99,
            'Add Relation'                        :  0,
            'Drop Relation'                       :-99,
            'Add Autoincrement Generator'         : -1, # Drop sequence drop table
            'Add Autoincrement Trigger'           :  0,
            'Add Autoincrement'                   :  0,
            'Drop Autoincrement Trigger'          :  0,
            'Drop Autoincrement'                  : 99, # Do last
            'Change Col Type'                     : -9, # Change col type needs to be before change default
            'Change Default'                      : -5,
            'Drop Default'                        : -5,
            'Add for change type'                 : -4,
            'Copy the data over for change type'  : -3,
            'Drop the old column for change type' : -2,
            'Rename column for change type'       : -1,
            'Add function'                        :  0,
            'Drop function'                       :  0,
        }
        
        if a and b:
            return orderDict[a[0]] - orderDict[b[0]]
        
        return 0
    
    def inDbms(self, node):
        if not node.hasAttribute('dbms'):
            return True
        
        dbmsList = node.getAttribute('dbms').lower().split(',')
        
        if len(dbmsList) == 0 or self.dbmsType in dbmsList:
            return True
        
        return False

def safeGet(dom, strKey, default = None):
    if dom.hasAttribute(strKey):
        return dom.getAttribute(strKey)
    return default
    
def parseCommandLine():
    usage = "usage: %prog [options] <filename>"
    parser = optparse.OptionParser(usage)
    parser.add_option("-b", "--dbms",
                  dest="strDbms", metavar="DBMS", default="postgres",
                  help="Output for which Database System")
    (options, args) = parser.parse_args()

    fc = DiffXml2Ddl()
    fc.setDbms(options.strDbms)
    if len(args) == 0:
        parser.print_help()
        parser.error("Need a filename to compare against")
    else:
        strNewFile = args[0]
    
    if len(args) == 2:
        strOldFile = args[1]
    else:
        strOldFile = './.svn/text-base/%s.svn-base' % strNewFile
  
    results = fc.diffFiles(strOldFile, strNewFile)
    for result in results:
        print '%s;' % (result[1])
    
if __name__ == "__main__":
    parseCommandLine()
