#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

from downloadCommon import DownloadCommon, getSeqName
from DdlCommonInterface import DdlCommonInterface
import re

class OracleDownloader(DownloadCommon):
    def __init__(self):
        self.strDbms = 'oracle'
        
    def connect(self, info):
        try:
            import cx_Oracle
        except:
            print "Missing Oracle support through cx_Oracle, see http://www.computronix.com/utilities.shtml#Oracle"
            return
        
        self.version = info['version']
        self.conn = cx_Oracle.connect(info['user'], info['pass'], info['dbname'])
        self.cursor = self.conn.cursor()
        
    def _tableInfo(self, strTable):
        self.cursor.execute("select * from %s" % (strTable,))
        for col in self.cursor.description:
            print col[0]
        
    def useConnection(self, con, version):
        self.conn = con
        self.version = version
        self.cursor = self.conn.cursor()
        
    def getTables(self, tableList):
        """ Returns the list of tables as a array of strings """
        
        if tableList and len(tableList) > 0:
            # Note we are always case insensitive here
            inTables = "AND upper(TABLE_NAME) IN ('%s')" % ("' , '".join([name.upper() for name in tableList]))
        else:
            inTables = ""
        strQuery = """SELECT TABLE_NAME FROM ALL_TABLES WHERE 
            TABLE_NAME NOT IN ('DUAL')
            AND OWNER NOT IN ('SYS', 'SYSTEM', 'OLAPSYS', 'WKSYS', 'WMSYS', 'CTXSYS', 'DMSYS', 'MDSYS', 'EXFSYS', 'ORDSYS')
            AND TABLE_NAME NOT LIKE 'BIN$%%' 
            %s
            ORDER BY TABLE_NAME
            """ % (inTables)
        
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], tableList)
        
        return []

    def getTableColumns(self, strTable):
        """ Returns column in this format
            (nColIndex, strColumnName, strColType, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, bNotNull, strDefault, auto_increment)
        """
        strSql = """
            SELECT COLUMN_ID, COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, DATA_SCALE, NULLABLE, DATA_DEFAULT
            FROM ALL_TAB_COLUMNS
            WHERE TABLE_NAME = :tablename
            ORDER BY COLUMN_ID"""
        # self._tableInfo('ALL_TAB_COLUMNS')
        self.cursor.execute(strSql, { 'tablename' : strTable})
        rows = self.cursor.fetchall()
        
        ret = []
        fixNames = {
            'character varying' : 'varchar',
        }
        for row in rows:
            attnum, name, type, size, numsize, numprec, nullable, default = row
            if type in fixNames:
                type = fixNames[type]
            
            if nullable == "Y":
                bNotNull = False
            else:
                bNotNull = True
            
            # TODO
            bAutoIncrement = False
            
            if numsize != None or numprec != None:
                size = numsize
            
            if type == 'DATE' or type == 'TIMESTAMP':
                size = None
            elif type == 'FLOAT' and size == 126:
                size = None
            
            if default:
                default = default.rstrip()
            
            #~ if name.upper() == name:
                #~ name = name.lower()
            
            ret.append((name, type, size, numprec, bNotNull, default, bAutoIncrement))
            
        return ret
    
    def getTableComment(self, strTableName):
        """ Returns the comment as a string """
        # TODO
        
        strSql = "SELECT COMMENTS from ALL_TAB_COMMENTS WHERE TABLE_NAME = :TABLENAME"
        self.cursor.execute(strSql, { 'TABLENAME' : strTableName })
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return None

    def getColumnComment(self, strTableName, strColumnName):
        """ Returns the comment as a string """
        strSql = "SELECT COMMENTS from  ALL_COL_COMMENTS WHERE TABLE_NAME = :TABLENAME AND COLUMN_NAME = :COLUMNAME"
        self.cursor.execute(strSql, { 'TABLENAME' : strTableName, 'COLUMNAME' : strColumnName })
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return []
        return None

    def getTableIndexes(self, strTableName):
        """ Returns 
            (strIndexName, [strColumns,], bIsUnique, bIsPrimary, bIsClustered)
            or []
        """
        
        #self._tableInfo("ALL_INDEXES")
        strSql = """SELECT index_name, uniqueness, clustering_factor
            FROM ALL_INDEXES
            WHERE table_name = :tablename
            """
        self.cursor.execute(strSql, { 'tablename' : strTableName} )
        rows = self.cursor.fetchall()
        
        ret = []
        if not rows:
            return ret
        #self._tableInfo("ALL_IND_COLUMNS")
        
        for row in rows:
            (strIndexName, bIsUnique, bIsClustered) = row
            strSql = """SELECT column_name FROM ALL_IND_COLUMNS 
                WHERE table_name = :tablename AND index_name = :indexname
                ORDER BY COLUMN_POSITION """
            self.cursor.execute(strSql, { 'tablename' : strTableName, 'indexname' : strIndexName } )
            colrows = self.cursor.fetchall()
            colList = [col[0] for col in colrows]
            
            bIsPrimary = False
            if bIsUnique == 'UNIQUE':
                strSql = """select c.*
                    from   all_constraints c, all_cons_columns cc
                    where  c.table_name = :tablename
                    and    cc.constraint_name = c.constraint_name
                    and    c.constraint_type = 'P'
                    and    cc.column_name in (:colnames)
                    and    c.status = 'ENABLED'"""
                self.cursor.execute(strSql, { 'tablename' : strTableName, 'colnames' : ','.join(colList) })
                indexRows = self.cursor.fetchall()
                if indexRows and len(indexRows) > 0:
                    bIsPrimary = True

            ret.append((strIndexName, colList, bIsUnique, bIsPrimary, bIsClustered))
        
        return ret

    def _getTableViaConstraintName(self, strConstraint):
        """ Returns strTablename """
        
        strSql = """SELECT TABLE_NAME FROM ALL_CONSTRAINTS WHERE CONSTRAINT_NAME = :strConstraint"""
        self.cursor.execute(strSql, { 'strConstraint' : strConstraint } )
        rows = self.cursor.fetchall()
        
        if rows:
            return rows[0][0]
        
        return None

    def _getColumnsViaConstraintName(self, strConstraint):
        """ Returns strTablename """
        
        strSql = """SELECT COLUMN_NAME FROM all_cons_columns WHERE CONSTRAINT_NAME = :strConstraint ORDER BY POSITION"""
        self.cursor.execute(strSql, { 'strConstraint' : strConstraint } )
        rows = self.cursor.fetchall()
        
        if rows:
            return [ col[0] for col in rows ]
        
        return []

    def getTableRelations(self, strTableName):
        """ Returns 
            (strConstraintName, colName, fk_table, fk_columns, confupdtype, confdeltype)
            or []
        """
        # CONSTRAINT_TYPE == "P" primary key
        # CONSTRAINT_TYPE == "R" 'Ref. Integrity'
        # CONSTRAINT_TYPE == "U" 'Unique Constr.'
        # CONSTRAINT_TYPE == "C" 'Check Constr.'
        strSql = """SELECT CONSTRAINT_NAME, TABLE_NAME, R_CONSTRAINT_NAME, DELETE_RULE
            FROM  ALL_CONSTRAINTS
            WHERE TABLE_NAME = :tablename
            AND   CONSTRAINT_TYPE = 'R'
            AND   STATUS='ENABLED'
            """
        self.cursor.execute(strSql, { 'tablename' : strTableName })
        rows = self.cursor.fetchall()
        
        ret = []
        
        if not rows:
            return ret
        
        for row in rows:
            (strConstraintName, strTable, fk_constraint, chDelType) = row
            # Todo get the fk table name
            # and the col list
            # and the fk col list
            if fk_constraint:
                fk_table = self._getTableViaConstraintName(fk_constraint)
            else:
                fk_table = None
            
            colList = self._getColumnsViaConstraintName(strConstraintName)
            if fk_constraint:
                fkColList = self._getColumnsViaConstraintName(fk_constraint)
            else:
                fkColList = []
            
            #print "del type %s" % (chDelType)
            if chDelType == 'NO ACTION':
                chDelType = 'a'
            elif chDelType == 'CASCADE':
                chDelType = 'c'
            elif chDelType == 'SET NULL':
                chDelType = 'n'
            elif chDelType == 'DEFAULT': # Check TODO
                chDelType = 'd'
            
            chUpdateType = ''
            ret.append((strConstraintName, colList, fk_table, fkColList, chUpdateType, chDelType))
        
        return ret
        
    def getViews(self, viewList):
        """ Returns the list of views as a array of strings """
        
        if viewList and len(viewList) > 0:
            inViews = "AND VIEW_NAME IN ('%s')" % ("','".join([name.upper() for name in viewList]))
        else:
            inViews = ""
        
        strQuery = """SELECT VIEW_NAME 
        FROM ALL_VIEWS
        WHERE OWNER NOT IN ('SYS', 'SYSTEM', 'OLAPSYS', 'WKSYS', 'WMSYS', 'CTXSYS', 'DMSYS', 'MDSYS', 'EXFSYS', 'ORDSYS', 'WK_TEST', 'XDB')
        %s
        ORDER BY VIEW_NAME""" % (inViews)
              
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], viewList)
        
        return []

    def getViewDefinition(self, strViewName):
        strQuery = "SELECT TEXT FROM ALL_VIEWS WHERE VIEW_NAME = :viewName"
        self.cursor.execute(strQuery, { 'viewName' : strViewName })
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0].rstrip()
        
        return None

    def getFunctions(self, functionList):
        """ Returns functions """
        
        if functionList and len(functionList) > 0:
            inFunctions = "AND OBJECT_NAME IN ('%s')" % ("','".join([name.upper() for name in functionList]))
        else:
            inFunctions = ""
        
        strQuery = """SELECT OBJECT_NAME
        FROM ALL_OBJECTS
        WHERE OBJECT_TYPE in ('PROCEDURE', 'FUNCTION')
        AND   OWNER NOT IN ('SYS', 'SYSTEM', 'OLAPSYS', 'WKSYS', 'WMSYS', 'CTXSYS', 'DMSYS', 'MDSYS', 'EXFSYS', 'ORDSYS', 'WK_TEST', 'XDB')
        %s
        ORDER BY OBJECT_NAME""" % (inFunctions)
        
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], functionList)
        
        return []

    def getFunctionDefinition(self, strSpecifiName):
        """ Returns (routineName, parameters, return, language, definition) """
        
        strSpecifiName = strSpecifiName.upper()
        
        strQuery = "select TEXT from all_source where name=:strSpecifiName ORDER BY LINE"
        self.cursor.execute(strQuery, { 'strSpecifiName' : strSpecifiName })
        rows = self.cursor.fetchall()
        if not rows:
            return (None, None, None, None)
        
        lines = []
        for row in rows:
            lines.append(row[0])
        
        
        strDefinition = ''.join(lines)
        strDefinition = strDefinition.rstrip('; ') # Remove trailing ; on last line
        
        re_def = re.compile(r".+\s(AS|IS)\s", re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        strDefinition = re_def.sub('', strDefinition)
        
        strQuery = """select lower(ARGUMENT_NAME), lower(DATA_TYPE), SEQUENCE, IN_OUT
            FROM ALL_ARGUMENTS 
            WHERE object_name = :strSpecifiName AND ARGUMENT_NAME is not null
            AND IN_OUT IN ('IN', 'IN/OUT') 
            ORDER BY POSITION"""
        self.cursor.execute(strQuery, { 'strSpecifiName' : strSpecifiName })
        rows = self.cursor.fetchall()
        parameters = [] 
        if rows: 
            for row in rows:
                (ARGUMENT_NAME, DATA_TYPE, SEQUENCE, IN_OUT) = row
                if ARGUMENT_NAME:
                    parameters.append(ARGUMENT_NAME + " " + DATA_TYPE)
                else:
                    parameters.append(DATA_TYPE)
            
        strQuery = """select lower(DATA_TYPE)
            FROM ALL_ARGUMENTS
            WHERE object_name = :strSpecifiName 
            AND IN_OUT = 'OUT'"""
        self.cursor.execute(strQuery, { 'strSpecifiName' : strSpecifiName })
        rows = self.cursor.fetchall()
        strReturn = None
        if rows:
            if len(rows) > 1:
                print "More than one return statement?, please check code"
            else:
                DATA_TYPE = rows[0][0]
                strReturn = DATA_TYPE
        return (strSpecifiName.lower(), parameters, strReturn, None, strDefinition)


class DdlOracle(DdlCommonInterface):
    def __init__(self, strDbms):
        DdlCommonInterface.__init__(self, strDbms)
        
        self.params['max_id_len'] = { 'default' : 63 }
        self.params['alter_default']    = ['ALTER TABLE %(table_name)s MODIFY %(column_name)s %(column_type)s']
        self.params['drop_default']     = ['ALTER TABLE %(table_name)s ALTER %(column_name)s %(column_type)s']
        self.params['rename_column']    = ['ALTER TABLE %(table_name)s RENAME COLUMN %(old_col_name)s TO %(new_col_name)s']
        self.params['change_col_type']  = ['ALTER TABLE %(table_name)s MODIFY %(column_name)s %(column_type)s']
        self.params['drop_column']      = ['ALTER TABLE %(table_name)s DROP COLUMN %(column_name)s']
        self.params['add_relation']     = ['ALTER TABLE %(tablename)s ADD CONSTRAINT %(constraint)s FOREIGN KEY (%(thiscolumn)s) REFERENCES %(othertable)s(%(fk)s)%(ondelete)s']
        self.params['create_view']      = ['CREATE VIEW %(viewname)s AS %(contents)s']
        self.params['create_function']  = ["CREATE FUNCTION %(functionname)s(%(arguments)s) RETURN %(returns)s AS\n%(contents)s;"]
        self.params['drop_function']    = ['DROP FUNCTION %(functionname)s']
        
        self.params['keywords'] = """AS ASC AUDIT ACCESS BY ADD ALL ALTER CHAR AND ANY CHECK DATE CLUSTER COLUMN COMMENT DECIMAL DEFAULT COMPRESS
            DELETE CONNECT DESC DISTINCT DROP CREATE CURRENT ELSE CURSOR GRANT GROUP EXCLUSIVE EXISTS HAVING IDENTIFIED IMMEDIATE
            IN FILE INCREMENT INDEX FLOAT FOR INITIAL INSERT FROM INTEGER INTERSECT INTO IS MINUS MLSLABEL LEVEL LIKE MODE 
            MODIFY LOCK LONG NOAUDIT NOCOMPRESS MAXEXTENTS NOT NOTFOUND NOWAIT NULL NUMBER PCTFREE OF OFFLINE ON ONLINE PRIOR
            PRIVILEGES OPTION OR PUBLIC ORDER RAW SELECT RENAME SESSION SET SHARE RESOURCE SIZE REVOKE SMALLINT ROW ROWID ROWLABEL
            ROWNUM SQLBUF ROWS START UID SUCCESSFUL UNION UNIQUE SYNONYM SYSDATE TABLE UPDATE USER THEN VALIDATE VALIDATION VALUE
            VALUES TO VARCHAR VARCHAR2 VIEW TRIGGER WHENEVER WHERE WITH""".split()
        
    def addFunction(self, strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs):
        newArgs = []
        for arg in argumentList:
            if ' IN ' not in arg.upper():
                arg = ' IN '.join(arg.split())
            newArgs.append(arg)
            
        info = {
            'functionname' : self.quoteName(strNewFunctionName),
            'arguments'  : ', '.join(newArgs),
            'returns'  : strReturn,
            'contents' : strContents.replace("'", "''"),
        }
        
        for strDdl in self.params['create_function']:
            diffs.append(('Add function',  strDdl % info))
    