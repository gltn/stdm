#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import re, os
from xml.dom.minidom import parse, parseString
from DdlCommonInterface import DdlCommonInterface, g_dbTypes
from OracleInterface import DdlOracle
from PostgreSQLInterface import DdlPostgres
from MySqlInterface import DdlMySql
from FirebirdInterface import DdlFirebird

__author__ = "Scott Kirkwood (scott_kirkwood at berlios.com)"
__keywords__ = ['XML', 'DML', 'SQL', 'Databases', 'Agile DB', 'ALTER', 'CREATE TABLE', 'GPL']
__licence__ = "GNU Public License (GPL)"
__url__ = 'http://xml2dml.berlios.de'
__version__ = "$Revision: 0.2 $"


def attribsToDict(node):
    dict = {}
    attribs = node.attributes
    for nIndex in range(attribs.length):
        dict[attribs.item(nIndex).name] = attribs.item(nIndex).value
    
    return dict

def createDdlInterface(strDbms):
    """ Here we use the letter/envelope paradymn to create the class of the right
    type. """ 
    if strDbms.lower() not in g_dbTypes:
        print "Unknown dbms %s" % (strDbms)
    
    if strDbms.startswith('postgres'):
        return DdlPostgres(strDbms)
    elif strDbms.startswith('mysql'):
        return DdlMySql()
    elif strDbms.startswith('firebird'):
        return DdlFirebird()
    elif strDbms.startswith('oracle'):
        return DdlOracle(strDbms)
    else:
        assert(False)
        
if __name__ == "__main__":
    import os, sys
    sys.path += ['../tests']
    from diffXml2DdlTest import doTests
    
    os.chdir('../tests')
    doTests()
