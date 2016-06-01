#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

from downloadCommon import DownloadCommon, getSeqName
from DdlCommonInterface import DdlCommonInterface
import re

class PgDownloader(DownloadCommon):
    """ Silly me, I didn't know about INFORMATION_SCHEMA """
    def __init__(self):
        self.strDbms = 'postgres'
        
    def connect(self, info):
        try:
            import psycopg
        except:
            print "Missing PostgreSQL support through psycopg"
            return
        
        self.conn = psycopg.connect('host=%(host)s dbname=%(dbname)s user=%(user)s password=%(pass)s' % info)
        self.cursor = self.conn.cursor()
        #self.doSomeTests()
        
    def useConnection(self, con, version):
        self.conn = con
        self.cursor = self.conn.cursor()
        
    def doSomeTests(self):
        sql = "select tablename from pg_tables where tablename in %s"
        inList = (('sample', 'companies', 'table1'), )
        self.cursor.execute(sql, inList)
        print self.cursor.fetchall()
        
        sql = "select tablename from pg_tables where tablename = %(tbl)s"
        inDict = {  'tbl' : 'sample' }
        self.cursor.execute(sql, inDict)
        print self.cursor.fetchall()

        sys.exit(-1)

    def getTablesStandard(self, tableList):
        """ Returns the list of tables as a array of strings """
        
        strQuery = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA not in ('pg_catalog', 'information_schema') and TABLE_NAME NOT LIKE 'pg_%' AND TABLE_TYPE = 'BASE TABLE'"
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], tableList)
        
        return []

    def getTables(self, tableList):
        """ Returns the list of tables as a array of strings """
        self.cursor.execute("select tablename from pg_tables where schemaname not in ('pg_catalog', 'information_schema')")
        return self._confirmReturns([x[0] for x in self.cursor.fetchall() ], tableList)

    def getTableColumnsStandard(self, strTable):
        """ Returns column in this format
            (nColIndex, strColumnName, strColType, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, bNotNull, strDefault, auto_increment)
        """
        strSql = """
            SELECT ORDINAL_POSITION, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_PRECISION_RADIX, NUMERIC_SCALE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION"""
        self.cursor.execute(strSql, [strTable])
        rows = self.cursor.fetchall()
        
        ret = []
        for row in rows:
            attnum, name, type, size, numsize, numprecradix, numprec, attnotnull, default = row
            type = self._fixTypeNames(type)
            
            if not size and numprecradix == 10:
                size = numsize
            
            if attnotnull.lower() == "yes":
                attnotnull = False
            else:
                attnotnull = True
            
            if default:
                # remove the '::text stuff
                default = default.replace('::text', '')
            
            bAutoIncrement = False
            if default == "nextval('%s')" % (getSeqName(strTable, name)):
                default = ''
                bAutoIncrement = True
                
            ret.append((name, type, size, numprec, attnotnull, default, bAutoIncrement))
            
        return ret

    def getTableColumns(self, strTable):
        """ Returns column in this format
            (strColumnName, strColType, nColSize, nColPrecision, bNotNull, strDefault, bAutoIncrement)
        """
        strSql = """
            SELECT pa.attnum, pa.attname, pt.typname, pa.atttypmod, pa.attnotnull, pa.atthasdef, pc.oid
            FROM pg_attribute pa, pg_type pt, pg_class pc
            WHERE pa.atttypid = pt.oid 
            AND pa.attrelid = pc.oid
            AND pa.attisdropped = 'f'
            AND pc.relname = %s
            AND pc.relkind = 'r'
            ORDER BY attnum"""
        self.cursor.execute(strSql, [strTable])
        rows = self.cursor.fetchall()
        
        specialCols = ['cmax', 'cmin', 'xmax', 'xmin', 'oid', 'ctid', 'tableoid']
        ret = []
        for row in rows:
            attnum, name, type, attlen, attnotnull, atthasdef, clasoid = row
            if name not in specialCols:
                type = self._fixTypeNames(type)
                
                attlen, precision = self.decodeLength(type, attlen)
                    
                default = None
                bAutoIncrement = False
                if atthasdef:
                    default = self.getColumnDefault(clasoid, attnum)
                    if default == "nextval('%s')" % (getSeqName(strTable, name)):
                        default = ''
                        bAutoIncrement = True

                ret.append((name, type, attlen, precision, attnotnull, default, bAutoIncrement))
            
        return ret

    def _fixTypeNames(self, type):
        fixNames = {
            'int4'    : 'integer',
            'int'     : 'integer',
            'bool'    : 'boolean',
            'float8'  : 'double precision',
            'int8'    : 'bigint',
            'serial8' : 'bigserial',
            'serial4' : 'serial',
            'float4'  : 'real',
            'int2'    : 'smallint',
            'character varying' : 'varchar',
        }
        if type in fixNames:
            return fixNames[type]
        
        return type
    
    def decodeLength(self, type, atttypmod):
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
        
    def getColumnDefault(self, clasoid, attnum):
        """ Returns the default value for a comment or None """
        strSql = "SELECT adsrc FROM pg_attrdef WHERE adrelid = %s AND adnum = %s"
        self.cursor.execute(strSql, [clasoid, attnum])
        rows = self.cursor.fetchall()
        if not rows:
            return None
        
        strDefault = rows[0][0]
        
        strDefault = strDefault.replace('::text', '')
        return strDefault

    def getTableComment(self, strTableName):
        """ Returns the comment as a string """
        
        strSql = """SELECT description FROM pg_description pd, pg_class pc 
            WHERE pc.relname = %s AND pc.relkind = 'r' AND pd.objoid = pc.oid AND pd.objsubid = 0"""
        self.cursor.execute(strSql, [strTableName])
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return None

    def getColumnCommentStandard(self, strTableName, strColumnName):
        """ Returns the comment as a string """
        
        strSql = """SELECT description FROM pg_description pd, pg_class pc, pg_attribute pa
            WHERE pc.relname = %s AND pc.relkind = 'r' 
            AND pd.objoid = pc.oid AND pd.objsubid = pa.attnum AND pa.attname = %s AND pa.attrelid = pc.oid"""
        
        self.cursor.execute(strSql, [strTableName, strColumnName])
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return None

    def getTableIndexes(self, strTableName):
        """ Returns 
            (strIndexName, [strColumns,], bIsUnique, bIsPrimary, bIsClustered)
            or []
        """
        strSql = """SELECT pc.relname, pi.indkey, indisunique, indisprimary, indisclustered
            FROM pg_index pi, pg_class pc, pg_class pc2
            WHERE pc2.relname = %s
            AND pc2.relkind = 'r'
            AND pc2.oid = pi.indrelid
            AND pc.oid = pi.indexrelid
            """
        self.cursor.execute(strSql, [strTableName])
        rows = self.cursor.fetchall()
        
        ret = []
        
        if not rows:
            return ret
        
        for row in rows:
            (strIndexName, strColumns, bIsUnique, bIsPrimary, bIsClustered) = row
            colList = self._fetchTableColumnsNamesByNums(strTableName, strColumns.split())
            ret.append((strIndexName, colList, bIsUnique, bIsPrimary, bIsClustered))
        
        return ret

    def getTableRelations(self, strTableName):
        """ Returns 
            (strConstraintName, colName, fk_table, fk_columns, confupdtype, confdeltype)
            or []
        """
        strSql = """SELECT pcon.conname, pcon.conkey, pcla2.relname, pcon.confkey, pcon.confupdtype, pcon.confdeltype
            FROM pg_constraint pcon, pg_class pcla, pg_class pcla2
            WHERE pcla.relname = %s
            AND pcla.relkind = 'r'
            AND pcon.conrelid = pcla.oid
            AND pcon.confrelid = pcla2.oid
            AND pcon.contype = 'f'
            """
        self.cursor.execute(strSql, [strTableName])
        rows = self.cursor.fetchall()
        
        ret = []
        
        if not rows:
            return ret
        
        for row in rows:
            (strConstraintName, cols, fk_table, fkeys, chUpdateType, chDelType) = row
            cols = cols[1:-1]
            colList = self._fetchTableColumnsNamesByNums(strTableName, cols.split(','))
            fkeys = fkeys[1:-1]
            fkColList = self._fetchTableColumnsNamesByNums(fk_table, fkeys.split(','))
            ret.append((strConstraintName, colList, fk_table, fkColList, chUpdateType, chDelType))
        
        return ret

    def _fetchTableColumnsNamesByNums(self, strTableName, nums):
        ret = []
        
        for num in nums:
            strSql = """
                SELECT pa.attname
                FROM pg_attribute pa, pg_class pc
                WHERE pa.attrelid = pc.oid
                AND pa.attisdropped = 'f'
                AND pc.relname = %s
                AND pc.relkind = 'r'
                AND pa.attnum = %s
                ORDER BY pa.attnum
                """
            
            self.cursor.execute(strSql, [strTableName] + [num])
            rows = self.cursor.fetchall()
            ret.append(rows[0][0])
                
        return ret
        
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
        """ Returns the list of views as a array of strings """

        self.cursor.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname not in ('pg_catalog', 'information_schema') 
            AND   viewname not in ('pg_logdir_ls')""")
        
        return self._confirmReturns([x[0] for x in self.cursor.fetchall() ], viewList)

    def getViewsStandard(self, viewList):
        strQuery =  """SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA not in ('pg_catalog', 'information_schema') 
        AND   TABLE_NAME NOT LIKE 'pg_%' AND 
        TABLE_TYPE = 'VIEW'"""
        #TODO add viewList constraint
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], viewList)
        
        return []

    def getViewDefinition(self, strViewName):
        strQuery = "SELECT definition FROM pg_views WHERE viewname = %s"
        self.cursor.execute(strQuery, [strViewName])
        rows = self.cursor.fetchall()
        if rows:
            return rows[0][0]
        
        return []

    def getFunctions(self, functionList):
        """ Returns functions """
        #TODO: Add function list constraint
        
        strQuery = """SELECT proname
        FROM pg_proc pp, pg_language pl
        WHERE proname not in ('_get_parser_from_curcfg', 'ts_debug', 'pg_file_length', 'pg_file_rename')
        AND  pl.oid = pp.prolang
        AND  lower(pl.lanname) not in ('c', 'internal', 'sql')
        """
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return self._confirmReturns([x[0] for x in rows], functionList)
        
        return []

    def getFunctionsStandard(self, functionList):
        """ Returns functions """
        #TODO: Add function list constraint
        
        strQuery = """SELECT SPECIFIC_NAME
        FROM INFORMATION_SCHEMA.ROUTINES 
        WHERE SPECIFIC_SCHEMA not in ('pg_catalog', 'information_schema')
        AND ROUTINE_NAME not in ('_get_parser_from_curcfg', 'ts_debug', 'pg_file_length', 'pg_file_rename')
        AND lower(external_language) not in ('c', 'internal') """
        self.cursor.execute(strQuery)
        rows = self.cursor.fetchall()
        if rows:
            return [x[0] for x in rows]
        
        return []

    def getFunctionDefinition(self, strSpecifiName):
        """ Returns (routineName, parameters, return, language, definition) """
        
        strQuery = """SELECT pp.proname, pp.prosrc, pt.typname, pl.lanname, pp.proargtypes
        FROM pg_proc pp, pg_type pt, pg_language pl
        WHERE proname = %s
        AND  pt.oid = pp.prorettype
        AND  pl.oid = pp.prolang"""
        self.cursor.execute(strQuery, [strSpecifiName])
        rows = self.cursor.fetchall()
        if not rows:
            return (None, None, None, None, None)
        
        strRoutineName, strDefinition, retType, strLanguage, strArgTypes = rows[0]
        retType = self._fixTypeNames(retType)
        argTypes = strArgTypes.split(',')
        
        strQuery = """SELECT typname FROM pg_type WHERE oid = %s"""
        params = []
        for typeNum in argTypes:
            self.cursor.execute(strQuery, [typeNum])
            row = self.cursor.fetchone()
            if row:
                params.append(self._fixTypeNames(row[0]))
            
        if self.strDbms != 'postgres7':
            strQuery = """SELECT proargnames FROM pg_proc WHERE proname = %s"""
            argnames = []
            self.cursor.execute(strQuery, [strSpecifiName])
            argnames = self.cursor.fetchone()
            if argnames:
                argnames = argnames[0]
                if argnames != None:
                    argnames = argnames[1:-1]
                    argnames = argnames.split(',')
                    for nIndex, argName in enumerate(argnames):
                        params[nIndex] += ' ' + argName
        
        # Cleanup definition by removing the stuff we added.
        #strDefinition = re.compile('|'.join(repList), re.DOTALL | re.MULTILINE).sub('', strDefinition)
        strDefinition = re.compile(r'\s*DECLARE\s+.*BEGIN', re.DOTALL | re.MULTILINE).sub('BEGIN', strDefinition)
        return (strRoutineName, params, retType, strLanguage, strDefinition)

class DdlPostgres(DdlCommonInterface):
    def __init__(self, strDbms):
        DdlCommonInterface.__init__(self, strDbms)
        
        self.params['max_id_len'] = { 'default' : 63 }
        
        if self.dbmsType == 'postgres7':
            self.params['change_col_type'] = [
                    'ALTER TABLE %(table_name)s ADD tmp_%(column_name)s %(column_type)s',
                    'UPDATE %(table_name)s SET tmp_%(column_name)s = %(column_name)s',
                    'ALTER TABLE %(table_name)s DROP %(column_name)s',
                    'ALTER TABLE %(table_name)s RENAME tmp_%(column_name)s TO %(column_name)s',
            ]
        
        self.params['keywords'] = """
            ALL AND ANY AS ASC AUTHORIZATION BETWEEN BINARY BOTH CASE CAST CHECK COLLATE COLUMN CONSTRAINT CREATE
            CROSS CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP CURRENT_USER DEFAULT DEFERRABLE DESC DISTINCT ELSE
            END EXCEPT FALSE FOR FOREIGN FREEZE FROM FULL GRANT GROUP HAVING ILIKE IN INITIALLY INNER INTERSECT
            INTO IS ISNULL JOIN LEADING LEFT LIKE LIMIT LOCALTIME LOCALTIMESTAMP NATURAL NEW NOT NOTNULL NULL 
            OFF OLD ON ONLY OR ORDER OUTER OVERLAPS PRIMARY REFERENCES RIGHT SELECT SESSION_USER SIMILAR SOME TABLE 
            THEN TO TRAILING TRUE UNION UNIQUE USER USING VERBOSE WHEN WHERE""".split()
     
    def addFunction(self, strNewFunctionName, argumentList, strReturn, strContents, attribs, diffs):
        newArgs = []
        declares = []
        
        if self.dbmsType == 'postgres7':
            for nIndex, arg in enumerate(argumentList):
                oneArg = arg.strip().split()
                newArgs.append(oneArg[-1])
                declares.append('    %s ALIAS FOR $%d;' % (oneArg[0], nIndex + 1))
        else:
            newArgs = argumentList
        
        if len(declares) > 0:
            match = re.compile('(\s*declare)(.*)', re.IGNORECASE | re.MULTILINE | re.DOTALL).match(strContents)
            if match:
                strContents = match.group(1) + '\n' + '\n'.join(declares) + match.group(2)
            else:
                strContents = 'DECLARE\n' + '\n'.join(declares) + "\n" + strContents
            
        info = {
            'functionname' : self.quoteName(strNewFunctionName),
            'arguments'  : ', '.join(newArgs),
            'returns'  : strReturn,
            'contents' : strContents.replace("'", "''"),
        }
        if 'language' not in attribs:
            info['language'] = ' LANGUAGE plpgsql'
        else:
            info['language'] = ' LANGUAGE %s' % (attribs['language'])

        diffs.append(('Add view',  # OR REPLACE 
            "CREATE FUNCTION %(functionname)s(%(arguments)s) RETURNS %(returns)s AS '\n%(contents)s'%(language)s" % info )
        )
