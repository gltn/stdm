#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import re, os
from xml.dom.minidom import parse, parseString
import xml2ddl

__author__ = "Scott Kirkwood (scott_kirkwood at berlios.com)"
__keywords__ = ['XML', 'DDL', 'SQL', 'Databases', 'Agile DB', 'ALTER', 'CREATE TABLE', 'GPL']
__licence__ = "GNU Public License (GPL)"
__url__ = 'http://xml2ddl.berlios.de'
__version__ = "$Revision: 0.3.1 $"

def evenOdd(nIndex):
    if (nIndex % 2) == 0:
        return 'even'
    else:
        return 'odd'

class Xml2Html:
    """ Given an XML schema will produce HTML from it with lot's of nice hypertext links 
    """
    def __init__(self):
        self.lines = []
        self.Xml2Ddl = xml2ddl.Xml2Ddl()
        
    def addHeader(self):
        schema = self.xml.getElementsByTagName('schema')
        strSchemaName = schema[0].getAttribute("name")
        self.lines += ['<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">']
        self.lines += ["<html>"]
        self.lines += ["<head>"]
        self.lines += ["<title>%s schema</title>" % (strSchemaName)]
        self.lines += ['<link  type="text/css" rel="stylesheet" type="text/css" href="schema.css" />']
        self.lines += ['</style>']


        self.lines += ["</head>"]
        self.lines += ["<body>"]
        
    def addTrailer(self):
        self.lines += ["</body>"]
        self.lines += ["</html>"]

    def tableToc(self):
        tables = self.xml.getElementsByTagName('table')
        self.lines += ['<h1>List of Tables</h1>']
        self.lines += ['<table class="schema">']
        self.lines += ['<tr>']
        self.lines += ['<th>Table Name</th>']
        self.lines += ['<th>Full Name</th>']
        self.lines += ['<th>Description</th>']
        self.lines += ['</tr>']
        for nIndex, table in enumerate(tables):
            self.lines += ['<tr class="%s">' % (evenOdd(nIndex))]
            strTable = table.getAttribute('name')
            strFullName = table.getAttribute('fullname')
            if len(strFullName) == 0:
                strFullName = strTable
                
            self.lines += ['<td><a href="#%s">%s</a></td>' % (strTable, strTable)]
            self.lines += ['<td>%s</td>' % (strFullName)]
            self.lines += ['<td>%s</td>' % (table.getAttribute('desc'))]
            self.lines += ['</tr>']
        self.lines += ['</table>']
        
    def outTables(self):
        tables = self.xml.getElementsByTagName('table')
        for table in tables:
            self.outputTable(table)
    
    def outputTable(self, table):
        strTableName = table.getAttribute("name")
        strFullName = table.getAttribute("fullname")
        strDesc = table.getAttribute("desc")
        
        if len(strFullName) == 0:
            strFullName = strTableName
        
        self.lines += ['<h1 id="%s">%s</h1>' % (strTableName, strFullName) ]
        self.lines += ['<div>%s</div>' % (strDesc) ]
        
        self.outputColumns(table)

        self.outputRelations(table)
        
        self.outputIndexes(table)

        self.outputDetailColumns(table)

        self.outputDataset(table)

    def outputColumns(self, table):
        self.lines += ['<table class="schema">']
        self.lines += ['<tr>']
        self.lines += ['<th>Column Name</th>']
        self.lines += ['<th>Full Name</th>']
        self.lines += ['<th>Data Type</th>']
        self.lines += ['<th>Null</th>']
        self.lines += ['<th>Key</th>']
        self.lines += ['</tr>']
        
        strTableName = table.getAttribute('name')
        nIndex = 0
        for column in table.getElementsByTagName('column'):
            self.outputColumn(strTableName, column, nIndex)
            nIndex += 1
        
        self.lines += ['</table>']
        
    def getType(self, column):
        strSize = column.getAttribute('size')
        strType = column.getAttribute('type')
        if len(strSize) > 0:
            return '%s(%s)' % (strType, strSize)
        
        return strType
        
    def outputColumn(self, strTableName, column, nIndex):
        strColName = column.getAttribute('name')
        strFullName = column.getAttribute('fullname')
        strType = self.getType(column)
        strNull = column.getAttribute('null')
        strKey = column.getAttribute('key')
        strDeprecated = column.getAttribute('deprecated')
        
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        self.lines += ['<td><a href="#full_%s.%s" id="%s.%s"/>%s</td>' % (strTableName, strColName, strTableName, strColName, strColName)  ]
        if len(strDeprecated) > 0:
            self.lines += ['<td><span class="deprecated">deprecated</span></td>']
        else:
            self.lines += ['<td>%s</td>' % strFullName]
        
        self.lines += ['<td>%s</td>' % strType]
        self.lines += ['<td>%s</td>' % strNull]
        self.lines += ['<td>%s</td>' % strKey]
        self.lines += ['</tr>']
    
    def outputDetailColumns(self, table):
        self.lines += ['<h3>Column Definitions</h3>']
        
        strTableName = table.getAttribute('name')
        
        self.lines += ['<table class="schema">']
        self.lines += ['<tr>']
        self.lines += ['<th>Column name</th>']
        self.lines += ['<th>Information</th>']
        self.lines += ['</tr>']
        nIndex = 0
        for column in table.getElementsByTagName('column'):
            self.outputDetailColumn(strTableName, column, nIndex)
            nIndex += 1
        self.lines += ['</table>']
        
    def outputDetailColumn(self, strTableName, column, nIndex):
        strColName = column.getAttribute('name')
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        self.lines += ['<td class="def" rowspan="2" id="full_%s.%s">' % (strTableName, strColName)]
        self.lines += [ '<a href="#%s.%s">%s</a></td>' % (strTableName, strColName, strColName) ]
        if column.hasAttribute('fullname'):
            strFullName = column.getAttribute('fullname')
            self.lines += ['<td class="extradef">%s</td>' % strFullName]
        else:
            self.lines += ['<td></td>']
        self.lines += ['</tr>']
        
        self.lines += ['<tr>']
        self.lines += ['<td>']
        strDesc = ''
        if column.hasAttribute('desc'):
            strDesc = column.getAttribute('desc')
        
        strRelCol = self.getRelatedColumn(column)
        if strRelCol and len(strDesc) == 0:
            strDesc = 'Foreign key to <a href="#%s">%s<a>' % (strRelCol, strRelCol)
        
        if column.hasAttribute('deprecated'):
            strDesc += ' (<span class="deprecated">deprecated</span>)'
        
        self.lines += [strDesc]
        self.lines += ['</td></tr>']
    
    def getRelatedColumn(self, column):
        strColName = column.getAttribute('name')
        parent = column.parentNode.parentNode
        relations = parent.getElementsByTagName('relation')
        if not relations:
            return None
            
        for relation in relations:
            columns = relation.getAttribute('column').split(',')
            if strColName in columns and len(columns) == 1:
                strFkTable = relation.getAttribute('table')
                strFkCol = relation.getAttribute('fk')
                return "%s.%s" % (strFkTable, strFkCol)
        
        
    def outputDataset(self, table):
        datasets = table.getElementsByTagName('dataset')
        if not datasets:
            return
        
        # We need to get the column list in the right order, get it from the list of columns
        colNames = []
        for column in table.getElementsByTagName('column'):
            colNames.append(column.getAttribute('name'))
            
        vals = datasets[0].getElementsByTagName('val')
        self.lines += ['<h2>Data values</h2>']
        self.lines += ['<table class="schema">']
        attribs = vals[0].attributes
        self.lines += ['<tr>']
        for strColName in colNames:
            self.lines += ['<th>%s</th>' % (strColName)]
        
        self.lines += ['</tr>']
        
        nIndex = 0
        for valLine in vals:
            self.lines += ['<tr class="%s">' % (evenOdd(nIndex))]
            attribs = valLine.attributes
            for strColName in colNames:
                strColValue = valLine.getAttribute(strColName)
                self.lines += ['<td>%s</td>' % (strColValue)]
            self.lines += ['</tr>']
            nIndex += 1
        self.lines += ['</table>']

    def outputRelations(self, table):
        relationsNode = table.getElementsByTagName('relations')
        if not relationsNode:
            return
        
        self.lines += ['<h3>Relations</h3>']
        
        strTableName = table.getAttribute('name')
        relations = relationsNode[0].getElementsByTagName('relation')
        self.lines += ['<table class="schema">']
        
        self.lines += ['<tr>']
        self.lines += ['<th>Column Name</th>']
        self.lines += ['<th>Related Table</th>']
        self.lines += ['<th>Related Column</th>']
        self.lines += ['</tr>']
        
        nIndex = 0
        for relation in relations:
            self.outputRelation(strTableName, relation, nIndex)
            nIndex += 1
        
        self.lines += ['</table>']
        
    def outputRelation(self, strTableName, relation, nIndex):
        strColName = relation.getAttribute('column')
        strFkTable = relation.getAttribute('table')
        strFkCol = relation.getAttribute('fk')
        
        if len(strFkCol) == 0:
            strFkCol = strColName
        
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        
        self.lines += ['<td class="def" id="full_%s.%s">' % (strTableName, strColName)]
        self.lines += [ '<a href="#%s.%s">%s</a></td>' % (strTableName, strColName, strColName) ]
        self.lines += ['<td>%s</td>' % (strFkTable) ]
        self.lines += ['<td><a href="#%s.%s">%s</a></td>' % (strFkTable, strFkCol, strFkCol) ]
        self.lines += ['</tr>']

        
    def outputIndexes(self, table):
        indexsNode = table.getElementsByTagName('indexes')
        if not indexsNode:
            return
        
        self.lines += ['<h3>Indexes</h3>']
        
        strTableName = table.getAttribute('name')
        indexs = indexsNode[0].getElementsByTagName('index')
        self.lines += ['<table class="schema">']
        
        self.lines += ['<tr>']
        self.lines += ['<th>Index Name</th>']
        self.lines += ['<th>Columns</th>']
        self.lines += ['</tr>']
        
        nIndex = 0
        for index in indexs:
            self.outputIndex(strTableName, index, nIndex)
            nIndex += 1
        
        self.lines += ['</table>']
        
    def outputIndex(self, strTableName, index, nIndex):
        strIndexName = index.getAttribute('name')
        strColumns = index.getAttribute('columns')
        
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        self.lines += ['<td>%s</td>' % (strIndexName) ]
        self.lines += ['<td>%s</td>' % (strColumns) ]
        self.lines += ['</tr>']
        
    def outputViews(self):
        views = self.xml.getElementsByTagName('view')
        if len(views) == 0:
            return
        
        self.lines += ['<h3>Views</h3>']
        
        self.lines += ['<table class="schema">']
        for nIndex, view in enumerate(views):
            self.outputView(view, nIndex)
        
        self.lines += ['</table>']
            
    def outputView(self, view, nIndex):
        """ I think I'll just output the metadata instead of the actual view for now """
        
        strName = view.getAttribute('name')
        strFull = view.getAttribute('fullname')
        strDesc = view.getAttribute('desc')
        
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        self.lines += ['<td>%s</td>' % (strName) ]
        self.lines += ['<td>%s</td>' % (strFull) ]
        self.lines += ['<td>%s</td>' % (strDesc) ]
        self.lines += ['</tr>']
        
    def outputFunctions(self):
        funcs = self.xml.getElementsByTagName('function')
        if len(funcs) == 0:
            return
        
        self.lines += ['<h3>Functions</h3>']
        
        self.lines += ['<table class="schema">']
        for nIndex, func in enumerate(funcs):
            self.outputFunction(func, nIndex)
        
        self.lines += ['</table>']
            
    def outputFunction(self, function, nIndex):
        """ Output the function """
        
        strName = function.getAttribute('name')
        strFull = function.getAttribute('fullname')
        strDesc = function.getAttribute('desc')
        strArgs = function.getAttribute('arguments')
        strReturns = function.getAttribute('returns')
        
        self.lines += ['<tr class="%s">' % (evenOdd(nIndex)) ]
        self.lines += ['<td>%s</td>' % (strName) ]
        self.lines += ['<td>%s</td>' % (strFull) ]
        self.lines += ['<td>%s</td>' % (strDesc) ]
        self.lines += ['</tr>']
        
    def outputHtml(self, xml):
        self.xml = xml
        self.lines = []
        
        self.addHeader()
        self.tableToc()
        self.outTables()
        self.outputViews()
        self.outputFunctions()
        self.addTrailer()
        
        return self.lines

def parseCommandLine():
    import optparse
    
    usage = "usage: %prog [options] <filename>"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")

    (options, args) = parser.parse_args()

    x2h = Xml2Html()
    
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    strFilename = args[0]
    xml = xml2ddl.readMergeDict(strFilename)
    lines = x2h.outputHtml(xml)
    if options.filename:
        strOutfile = options.filename
    else:
        strOutfile = "outschema.html"
        
    of = open(strOutfile, "w")
    for line in lines:
        of.write("%s\n" % (line))
        
    of.close()

if __name__ == "__main__":
    parseCommandLine()
