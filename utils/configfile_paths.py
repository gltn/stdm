# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
doc="C:/test/stdmConfig.xml"
html="C:/test/stdm_schema.html"
sql="C:/test/stdmConfig.sql"

class FilePaths(object):
    def __init__(self):
        self._file=doc
        self._html=html
        self._sql=sql
        
    def XMLFile(self):
        #this function returns the default xml file with configuration
        return self._file

    def cacheFile(self,path):
        #To implemented to hold the current edits in memory before they are committed
        pass

    def setConfigurationFile(self):
        #To be implemented to write new file with user edits
        pass
    
    def HtmlFile(self):
        #Read the html representation of the schema
        return self._html
    
    def SQLFile(self):
        #Read the html representation of the schema
        return self._sql
    
    