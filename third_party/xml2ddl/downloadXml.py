#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import re, os
from xml.sax.saxutils import escape 
from downloadCommon import getSeqName
from xml.dom.minidom import parse, parseString
from OracleInterface import OracleDownloader
from PostgreSQLInterface import PgDownloader
from MySqlInterface import MySqlDownloader
from FirebirdInterface import FbDownloader
from DdlCommonInterface import g_dbTypes

__author__ = "Scott Kirkwood (scott_kirkwood at berlios.com)"
__keywords__ = ['XML', 'DML', 'SQL', 'Databases', 'Agile DB', 'ALTER', 'CREATE TABLE', 'GPL']
__licence__ = "GNU Public License (GPL)"
__url__ = 'http://xml2dml.berlios.de'

import os,sys

sys.path += ['./tests']
if os.path.exists('tests/my_conn.py') or os.path.exists('my_conn.py'):
    from my_conn import conn_info
else:
    try:
        from connect_info import conn_info
    except:
        pass

"""
INFORMATION_SCHEMA....
http://developer.mimer.com/documentation/html_92/Mimer_SQL_Engine_DocSet/Data_dic_views2.html#wp1118541

MySQL uses:
SHOW DATABASES (1 column)
SHOW TABLES (1 column)
DESCRIBE <table>;
Columns Field  | Type             | Null | Key | Default | Extra       
The "Extra" field records special information about columns. 
If you have selected the "auto_increment" functionality for a column, for example, that would show up in the "Extra" field when doing a "describe".
SHOW INDEX FROM tbl_name
"""

class DownloadXml:
    def __init__(self, downloader, options):
        self.db = downloader
        self.options = options
        if 'tables' not in self.options:
            self.options['tables'] = []
        if 'views' not in self.options:
            self.options['views'] = []
        if 'functions' not in self.options:
            self.options['functions'] = []
        
    def downloadSchema(self, tableList = None, of = sys.stdout):
        tables = self.db.getTables(tableList = self.options['tables'])
        of.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        of.write('<schema generated="yes">\n')
        
        for strTableName in tables:
            curTable = {
                'name' : strTableName,
                'columns' : []
            }
            desc = self.db.getTableComment(strTableName)
            if desc:
                curTable['desc'] = escape(desc)
            
            if self.options == None or 'getindexes' not in self.options or self.options['getindexes'] == True:
                curTable['indexes'] = self.db.getTableIndexes(strTableName)
            
            pkMap = {}
            for index in curTable['indexes']:
                if index[3]: # If Primary key
                    for nIndex, colName in enumerate(index[1]):
                        pkMap[colName] = nIndex + 1
            
            if self.options == None or 'getrelations' not in self.options or self.options['getrelations'] == True:
                curTable['relations'] = self.db.getTableRelations(strTableName)
            
            for colRow in self.db.getTableColumns(strTableName):
                (strColumnName, type, attlen, precision, attnotnull, default, bAutoIncrement) = colRow
                curCol = {
                    'name' : str(strColumnName),
                    'type' : str(type),
                }   
                if attlen:
                    curCol['size'] = attlen
                
                if precision:
                    curCol['precision'] = precision
                
                if attnotnull:
                    curCol['null'] = 'no'
                
                if strColumnName in pkMap:
                    curCol['key'] = pkMap[strColumnName]
                
                if default:
                    curCol['default'] = default
                
                strComment = self.db.getColumnComment(strTableName, strColumnName)
                if strComment:
                    curCol['desc'] = escape(strComment)
                
                if bAutoIncrement:
                    curCol['autoincrement'] = "yes"
                
                curTable['columns'].append(curCol)
            
            self.dumpTable(curTable, of)
            
        if self.options == None or 'getviews' not in self.options or self.options['getviews'] == True:
            self.getViews(of)


        if self.options == None or 'getfunctions' not in self.options or self.options['getfunctions'] == True:
            self.getFunctions(of)

        of.write('</schema>\n')

    def getViews(self, of):
        views = self.db.getViews(self.options['views'])
        for viewName in views:
            definition = self.db.getViewDefinition(viewName)
            info = {
                'name' : viewName,
                'definition' : definition,
            }
            self.dumpView(info, of)
    
    def dumpView(self, info, of):
        of.write('  <view %s>\n' % (self.doAttribs(info, ['name'])))
        of.write('    %s\n' % (escape(info['definition'])))
        of.write('  </view>\n')

    def getFunctions(self, of):
        mangledNames = self.db.getFunctions(self.options['functions'])
        for mangledName in mangledNames:
            strFuncName, params, strReturn, strLanguage, definition = self.db.getFunctionDefinition(mangledName)
            info = {
                'name'       : strFuncName,
                'definition' : definition,
                'arguments'  : ', '.join(params),
                'returns'    : strReturn,
            }
            if strLanguage and len(strLanguage) > 0:
                info['language'] = strLanguage
            
            self.dumpFunction(info, of)
    
    def dumpFunction(self, info, of):
        of.write('  <function %s>\n' % (self.doAttribs(info, ['name', 'arguments', 'returns', 'language'])))
        of.write('%s\n' % (escape(info['definition'].strip())))
        of.write('  </function>\n')

    def dumpTable(self, info, of):
        of.write('  <table %s>\n' % (self.doAttribs(info, ['name', 'desc'])))
        
        # Would be nice to align the columns
        for col in info['columns']:
            of.write('    <column %s/>\n' % (self.doAttribs(col, ['name', 'type', 'size', 'precision', 'null', 'default', 'key', 'desc', 'autoincrement'])))
    
        if 'indexes' in info:
            strIndexes = ""
            for index in info['indexes']:
                if not index[3]:
                    strIndexes += '        <index name="%s" columns="%s"/>\n' % (index[0], ','.join(index[1]))
                
            if len(strIndexes) > 0:
                of.write('    <indexes>\n')
                of.write(strIndexes)
                of.write('    </indexes>\n')
            
        if 'relations' in info and len(info['relations']) > 0:
            of.write('    <relations>\n')
            for index in info['relations']:
                # Need to add On Delete, and On Update 
                """
                confdeltype = 'c' THEN 0 -- Cascade 
                confdeltype = 'r' THEN 1 -- Restrict
                confdeltype = 'n' THEN 2 -- set Null
                confdeltype = 'a' THEN 3 -- no Action
                confdeltype = 'd' THEN 4 -- Default """
                curInfo = {
                    'name' : index[0],
                    'column' : ','.join(index[1]),
                    'table'  : index[2],
                    'fk'     : ','.join(index[3])
                }
                if index[4] == 'c':
                    curInfo['onupdate'] = 'cascade'
                elif index[4] == 'r':
                    curInfo['onupdate'] = 'restrict'
                elif index[4] == 'n':
                    curInfo['onupdate'] = 'setnull'
                elif index[4] == 'd':
                    curInfo['onupdate'] = 'default'
                    
                if index[5] == 'c':
                    curInfo['ondelete'] = 'cascade'
                elif index[5] == 'r':
                    curInfo['ondelete'] = 'restrict'
                elif index[5] == 'n':
                    curInfo['ondelete'] = 'setnull'
                elif index[5] == 'd':
                    curInfo['ondelete'] = 'default'
                    
                of.write('        <relation %s/>\n' % (self.doAttribs(curInfo, ['name', 'column', 'table', 'fk', 'ondelete', 'onupdate'])))
            
            of.write('    </relations>\n')
            
        of.write('  </table>\n')
    
    def doAttribs(self, attribs, nameList):
        ret = []
        for name in nameList:
            if name in attribs:
                ret.append('%s="%s"' % (name, attribs[name]))
        
        return ' '.join(ret)
    
def createDownloader(dbms, conn = None, info = None, options = None):
    if dbms.startswith('postgres'):
        db = PgDownloader()
    elif dbms.startswith('mysql'):
        db = MySqlDownloader()
    elif dbms.startswith('firebird'):
        db = FbDownloader()
    elif dbms.startswith('oracle'):
        db = OracleDownloader()

    if conn:
        db.useConnection(conn, info['version'])
    elif info:
        db.connect(info)
    else:
        info = conn_info[dbms]
        db.connect(info)
        
    return DownloadXml(db, options)

def parseCommandLine():
    import optparse
    parser = optparse.OptionParser()
    dbmsDefault = g_dbTypes[0]
    parser.add_option("-b", "--dbms",
        dest="strDbms", metavar="DBMS", default=dbmsDefault,
        help="Dowload for which Database Managment System (postgres, mysql, or firebird), defaults to %s" % (dbmsDefault))
    parser.add_option("", "--host",
        dest="strHost", metavar="HOST", default="localhost",
        help="Hostname or IP of machine")
    parser.add_option("-d", "--dbname",
        dest="strDbName", metavar="DATABASE", 
        help="Dowload for which named Database")
    parser.add_option("-u", "--user",
        dest="strUserName", metavar="USER", 
        help="User to login with")
    parser.add_option("-p", "--pass",
        dest="strPassword", metavar="PASS", 
        help="Password for the user")

    parser.add_option("-t", "--tables",
        dest="strTables", metavar="TABLES", default=None,
        help="Comma separated list of tables")

    parser.add_option("-v", "--views",
        dest="strViews", metavar="VIEWS", default=None,
        help="Comma separated list of views")

    parser.add_option("-f", "--funcs",
        dest="strFuncs", metavar="FUNCTIONS", default=None,
        help="Comma separated list of functions")

    (options, args) = parser.parse_args()
    
    info = {
        'dbname' : options.strDbName, 
        'user'   : options.strUserName, 
        'pass'   : options.strPassword,
        'host'   : options.strHost,
        'version' : 99,
    }

    if options.strTables:
        tables = options.strTables.split(',')
    else:
        tables = None
        
    if options.strViews:
        views = options.strViews.split(',')
    else:
        views = None
    
    if options.strFuncs:
        functions = options.strFuncs.split(',')
    else:
        functions = None

    runOptions = {
        'getfunctions' : True,
        'getviews'     : True,
        'getrelations' : True,
        'getindexes'   : True,
        'tables'       : tables,
        'views'        : views,
        'functions'    : functions,
    }
    if info['dbname'] == None or info['user'] == None:
        parser.print_help()
        sys.exit(-1)
        
    cd = createDownloader(options.strDbms, info = info, options = runOptions)
    cd.downloadSchema()

if __name__ == "__main__":
    parseCommandLine()
