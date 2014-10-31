#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
from downloadCommon import DownloadCommon, getSeqName
from DdlCommonInterface import DdlCommonInterface
import re

class FbDownloader(DownloadCommon):
    def __init__(self):
        self.strDbms = 'firebird'
        
    def connect(self, info):
        try:
            import kinterbasdb
        except:
            print "Missing Firebird support through kinterbasdb"
            return
        
        self.strDbms = 'firebird'
        self.version = info['version']
        self.conn = kinterbasdb.connect(
            dsn='localhost:%s' % info['dbname'],
            user = info['user'], 
            password = info['pass'])
        self.cursor = self.conn.cursor()
        
    def useConnection(self, con, version):
        self.conn = con
        self.version = version
        self.cursor = self.conn.cursor()
        
    def getTables(self, tableList):
        """ Returns the list of tables as a array of strings """
        
        strQuery =  "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG=0 AND RDB$VIEW_SOURCE IS NULL;"
        self.cursor.execute(strQuery)
        return self._confirmReturns([x[0].strip() for x in self.cursor.fetchall() ], tableList)
    
    def getTableColumns(self, strTable):
        """ Returns column in this format
            (nColIndex, strColumnName, strColType, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, bNotNull, strDefault, auto_increment)
        """
        strSql = """
            SELECT RF.RDB$FIELD_POSITION, RF.RDB$FIELD_NAME, RDB$FIELD_TYPE, F.RDB$FIELD_LENGTH, 
            RDB$FIELD_PRECISION, RDB$FIELD_SCALE, RF.RDB$NULL_FLAG, RF.RDB$DEFAULT_SOURCE, F.RDB$FIELD_SUB_TYPE
            FROM RDB$RELATION_FIELDS RF, RDB$FIELDS F
            WHERE RF.RDB$RELATION_NAME = ?
            AND RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
            ORDER BY RF.RDB$FIELD_POSITION;"""
        self.cursor.execute(strSql, [strTable])
        rows = self.cursor.fetchall()
        
        ret = []
       
        # TODO auto_increment
        bAutoIncrement = False
        for row in rows:
            attnum, name, nType, size, numsize, scale, attnull, default, sub_type = row
            
            if scale and scale < 0:
                scale = -scale
            
            if not size and numprecradix == 10:
                size = numsize
            
            strType = self.convertTypeId(nType)
                
            
            if sub_type == 1:
                strType = 'numeric'
            elif sub_type == 2:
                strType = 'decimal'
            
            if numsize > 0:
                size = numsize
                numsize = None
            
            if strType == 'integer' and size == 4:
                size = None
            elif strType == 'date' and size == 4:
                size = None
            elif strType == 'float' and size == 4:
                size = None
            
            if default:
                # Remove the 'DEFAULT ' part of the SQL
                default = default.replace('DEFAULT ', '')
            
            if self.hasAutoincrement(strTable, name):
                bAutoIncrement = True
            else:
                bAutoIncrement = False
                
            ret.append((name.strip(), strType, size, scale, attnull, default, bAutoIncrement))
            
        return ret

    def convertTypeId(self, nType):
        types = {
            261: 'blob',
            14 : 'char',    
            40 : 'cstring',
            11 : 'd_float',
            27 : 'double',
            10 : 'float',
            16 : 'int64',
            8  : 'integer',
            9  : 'quad',
            7  : 'smallint',
            12 : 'date',
            13 : 'time',
            35 : 'timestamp',
            37 : 'varchar',
        }
        
        strType = ''
        if nType in types:
            strType = types[nType]
            if nType not in [14, 40, 37]:
                size = None
        else:
            print "Uknown type %d" % (nType)
        
        return strType

    def hasAutoincrement(self, strTableName, strColName):
        strSql = "SELECT RDB$GENERATOR_NAME FROM RDB$GENERATORS WHERE UPPER(RDB$GENERATOR_NAME)=UPPER(?);"
        self.cursor.execute(strSql, [getSeqName(strTableName, strColName)[0:31]])
        rows = self.cursor.fetchall()
        if rows:
            return True
        
        return False
        
    def getTableComment(self, strTableName):
        """ Returns the comment as a string """
        
        strSql = "SELECT RDB$DESCRIPTION FROM RDB$RELATIONS WHERE RDB$RELATION_NAME=?;"
        self.cursor.execute(strSql, [strTableName])
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return None

    def getColumnComment(self, strTableName, strColumnName):
        """ Returns the comment as a string """
        
        strSql = """SELECT RDB$DESCRIPTION 
            FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = ? AND RDB$FIELD_NAME = ?"""
        
        self.cursor.execute(strSql, [strTableName, strColumnName])
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return None

    def getTableIndexes(self, strTableName):
        """ Returns 
            (strIndexName, [strColumns,], bIsUnique, bIsPrimary, bIsClustered)
            or []
            Warning the Primary key constraint cheats by knowing the name probably starts with pk_
        """
        strSql = """SELECT RDB$INDEX_NAME, RDB$UNIQUE_FLAG
            FROM RDB$INDICES
            WHERE RDB$RELATION_NAME = '%s'
            """ % (strTableName)
        self.cursor.execute(strSql)
        rows = self.cursor.fetchall()
        
        ret = []
        
        if not rows:
            return ret
        
        for row in rows:
            (strIndexName, bIsUnique) = row
            colList = self._fetchTableColumnsForIndex(strIndexName)
            if strIndexName.lower().startswith('pk_'):
                bIsPrimary = True
            else:
                bIsPrimary = False
            strIndexName = strIndexName.strip()
            ret.append((strIndexName, colList, bIsUnique, bIsPrimary, None))
        
        return ret

    def _fetchTableColumnsForIndex(self, strIndexName):
        strSql = """SELECT RDB$FIELD_NAME
            FROM RDB$INDEX_SEGMENTS
            WHERE RDB$INDEX_NAME = ?
            ORDER BY RDB$FIELD_POSITION
            """
        self.cursor.execute(strSql, [strIndexName.strip()])
        rows = self.cursor.fetchall()
        return [row[0].strip() for row in rows]

    def getTableRelations(self, strTableName):
        """ Returns 
            (strConstraintName, colName, fk_table, fk_columns)
            or []
        """
        strSql = """SELECT RDB$CONSTRAINT_NAME
            FROM RDB$RELATION_CONSTRAINTS
            WHERE RDB$RELATION_NAME = '%s'
            """ % (strTableName)
        self.cursor.execute(strSql)
        rows = self.cursor.fetchall()
        
        ret = []
        
        if not rows:
            return ret
        
        return ret

    def _fetchTableColumnsNamesByNums(self, strTableName, nums):
        strSql = """
            SELECT pa.attname
            FROM pg_attribute pa, pg_class pc
            WHERE pa.attrelid = pc.oid
            AND pa.attisdropped = 'f'
            AND pc.relname = %s
            AND pc.relkind = 'r'
            AND pa.attnum in (%s)
            ORDER BY pa.attnum
            """ % ( '%s', ','.join(['%s' for num in nums]) )
            
        self.cursor.execute(strSql, [strTableName] + nums)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]
        
    def _decodeLength(self, type, atttypmod):
        # gleamed from http://www.postgresql-websource.com/psql713/source-format_type.htm
        VARHDRSZ = 4
        
        if type == 'varchar':
            return (atttypmod - VARHDRSZ, None)
        
        if type == 'numeric':
            atttypmod -= VARHDRSZ
            return  ( (atttypmod >> 16) & 0xffff, atttypmod & 0xffff)
        
        if type == 'varbit' or type == 'bit':
            return (atttypmod, None)
        
        return (None, None)

    def getViews(self, viewList):
        strQuery =  "SELECT RDB$VIEW_NAME FROM RDB$VIEW_RELATIONS"
        #TODO add viewList constraint

        self.cursor.execute(strQuery)
        return self._confirmReturns([x[0].strip() for x in self.cursor.fetchall() ], viewList)

    def getViewDefinition(self, strViewName):
        strQuery = "SELECT RDB$RELATION_NAME, RDB$VIEW_SOURCE FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = UPPER(?)"
        self.cursor.execute(strQuery, [strViewName])
        rows = self.cursor.fetchall()
        if rows:
            ret = rows[0][1].strip()
            return ret
        
        return ''

    def getFunctions(self, functionList):
        #strQuery = "SELECT RDB$FUNCTION_NAME FROM RDB$FUNCTIONS WHERE RDB$SYSTEM_FLAG = 0"
        #TODO add functionList constraint
        strQuery = "SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES WHERE RDB$SYSTEM_FLAG = 0"
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        return self._confirmReturns([x[0].strip() for x in rows], functionList)

    def getFunctionDefinition(self, strSpecifiName):
        """ Returns (routineName, parameters, return, language, definition) """
        strQuery = "SELECT RDB$PROCEDURE_NAME, RDB$PROCEDURE_SOURCE FROM RDB$PROCEDURES WHERE RDB$SYSTEM_FLAG = 0 AND RDB$PROCEDURE_NAME = upper(?)"
        self.cursor.execute(strQuery, [strSpecifiName])
        rows = self.cursor.fetchall()
        strProcName, strDefinition = rows[0]
        strDefinition = strDefinition.strip()
        strProcName = strProcName.strip()
        
        strQuery = """SELECT PP.RDB$PARAMETER_NAME, PP.RDB$FIELD_SOURCE, PP.RDB$PARAMETER_TYPE, F.RDB$FIELD_TYPE, F.RDB$FIELD_LENGTH, F.RDB$FIELD_PRECISION, RDB$FIELD_SCALE
            FROM RDB$PROCEDURE_PARAMETERS PP, RDB$FIELDS F
            WHERE PP.RDB$PROCEDURE_NAME = upper(?) 
            AND   PP.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
            ORDER BY PP.RDB$PARAMETER_NUMBER"""
        self.cursor.execute(strQuery, [strSpecifiName])
        rows = self.cursor.fetchall()
        args = []
        rets = []
        
        for row in rows:
            strParamName, strSrc, nParamType, nType, nLen, nPrecision, nScale = row
            strParamName = strParamName.strip().lower()
            strSrc = strSrc.strip()
            strType = self.convertTypeId(nType)
            
            if nParamType == 0:
                args.append(strParamName + ' ' + strType)
            else:
                if strParamName.lower() == 'ret':
                    rets.append(strType)
                else:
                    rets.append(strParamName + ' ' + strType)
        
        return (strProcName.lower(), args, ','.join(rets), '', strDefinition)



class DdlFirebird(DdlCommonInterface):
    def __init__(self):
        DdlCommonInterface.__init__(self, 'firebird')
        self.params['max_id_len'] = { 'default' : 256 }
        self.params['table_desc'] = ["UPDATE RDB$RELATIONS SET RDB$DESCRIPTION = %(desc)s\n\tWHERE RDB$RELATION_NAME = upper('%(table)s')"]
        self.params['column_desc'] = ["UPDATE RDB$RELATION_FIELDS SET RDB$DESCRIPTION = %(desc)s\n\tWHERE RDB$RELATION_NAME = upper('%(table)s') AND RDB$FIELD_NAME = upper('%(column)s')"]
        self.params['drop_constraints_on_col_rename'] = True
        self.params['drop_table_has_cascade'] = False
        self.params['alter_default'] = ['ALTER TABLE %(table_name)s ALTER %(column_name)s TYPE %(column_type)s']
        self.params['rename_column'] = ['ALTER TABLE %(table_name)s ALTER %(old_col_name)s TO %(new_col_name)s']
        self.params['alter_default'] = ['ALTER TABLE %(table_name)s ALTER COLUMN %(column_name)s SET DEFAULT %(new_default)s']
        
        self.params['keywords'] = """
            ACTION ACTIVE ADD ADMIN AFTER ALL ALTER AND ANY AS ASC ASCENDING AT AUTO AUTODDL AVG BASED BASENAME BASE_NAME 
            BEFORE BEGIN BETWEEN BLOB BLOBEDIT BUFFER BY CACHE CASCADE CAST CHAR CHARACTER CHARACTER_LENGTH CHAR_LENGTH
            CHECK CHECK_POINT_LEN CHECK_POINT_LENGTH COLLATE COLLATION COLUMN COMMIT COMMITTED COMPILETIME COMPUTED CLOSE 
            CONDITIONAL CONNECT CONSTRAINT CONTAINING CONTINUE COUNT CREATE CSTRING CURRENT CURRENT_DATE CURRENT_TIME 
            CURRENT_TIMESTAMP CURSOR DATABASE DATE DAY DB_KEY DEBUG DEC DECIMAL DECLARE DEFAULT
            DELETE DESC DESCENDING DESCRIBE DESCRIPTOR DISCONNECT DISPLAY DISTINCT DO DOMAIN DOUBLE DROP ECHO EDIT ELSE 
            END ENTRY_POINT ESCAPE EVENT EXCEPTION EXECUTE EXISTS EXIT EXTERN EXTERNAL EXTRACT FETCH FILE FILTER FLOAT 
            FOR FOREIGN FOUND FREE_IT FROM FULL FUNCTION GDSCODE GENERATOR GEN_ID GLOBAL GOTO GRANT GROUP GROUP_COMMIT_WAIT 
            GROUP_COMMIT_ WAIT_TIME HAVING HELP HOUR IF IMMEDIATE IN INACTIVE INDEX INDICATOR INIT INNER INPUT INPUT_TYPE 
            INSERT INT INTEGER INTO IS ISOLATION ISQL JOIN KEY LC_MESSAGES LC_TYPE LEFT LENGTH LEV LEVEL LIKE LOGFILE 
            LOG_BUFFER_SIZE LOG_BUF_SIZE LONG MANUAL MAX MAXIMUM MAXIMUM_SEGMENT MAX_SEGMENT MERGE MESSAGE MIN MINIMUM 
            MINUTE MODULE_NAME MONTH NAMES NATIONAL NATURAL NCHAR NO NOAUTO NOT NULL NUMERIC NUM_LOG_BUFS NUM_LOG_BUFFERS 
            OCTET_LENGTH OF ON ONLY OPEN OPTION OR ORDER OUTER OUTPUT OUTPUT_TYPE OVERFLOW PAGE PAGELENGTH PAGES PAGE_SIZE 
            PARAMETER PASSWORD PLAN POSITION POST_EVENT PRECISION PREPARE PROCEDURE PROTECTED PRIMARY PRIVILEGES PUBLIC QUIT 
            RAW_PARTITIONS RDB$DB_KEY READ REAL RECORD_VERSION REFERENCES RELEASE RESERV RESERVING RESTRICT RETAIN RETURN 
            RETURNING_VALUES RETURNS REVOKE RIGHT ROLE ROLLBACK RUNTIME SCHEMA SECOND SEGMENT SELECT SET SHADOW SHARED SHELL 
            SHOW SINGULAR SIZE SMALLINT SNAPSHOT SOME SORT SQLCODE SQLERROR SQLWARNING STABILITY STARTING STARTS STATEMENT 
            STATIC STATISTICS SUB_TYPE SUM SUSPEND TABLE TERMINATOR THEN TIME TIMESTAMP TO TRANSACTION TRANSLATE TRANSLATION 
            TRIGGER TRIM TYPE UNCOMMITTED UNION UNIQUE UPDATE UPPER USER USING VALUE VALUES VARCHAR VARIABLE VARYING VERSION 
            VIEW WAIT WEEKDAY WHEN WHENEVER WHERE WHILE WITH WORK WRITE YEAR YEARDAY""".split()
        # Note you need to remove the constraints like:
        # alter table table1 drop constraint pk_table1;
        # before dropping the table (what a pain)

    def addFunction(self, strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs):
        argumentList = [ '%s' % arg for arg in argumentList ]
        info = {
            'functionname' : self.quoteName(strNewFunctionName),
            'arguments'  : ', '.join(argumentList),
            'returns'  : strReturn,
            'contents' : strContents.replace("'", "''"),
            'language' : '',
        }
        if 'language' in attribs:
            info['language'] = ' LANGUAGE %s' % (attribs['language'])

        diffs.append(('Add function',  # OR REPLACE
            "CREATE PROCEDURE %(functionname)s(%(arguments)s) RETURNS (ret %(returns)s) AS \n%(contents)s;" % info )
        )

    def dropFunction(self, strOldFunctionName, argumentList, diffs):
        info = {
            'functionname' : self.quoteName(strOldFunctionName),
        }
        diffs.append(('Drop function',
            'DROP PROCEDURE %(functionname)s' % info )
        )
