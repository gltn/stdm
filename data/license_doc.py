# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : STDM license file
Description          : - ??
Date                 : 28/May/2013 
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.data import FilePaths 

class LicenseDocument(object):
    def __init__(self):
        self.file = None
        self.filehandler = FilePaths()
        
    def open_license_file(self):
        '''get the path to the license file'''
        self.file = self.filehandler.stdm_license_doc()
    
    def read_license_info(self):
        '''read license information for user '''
        try:
            self.open_license_file()
            with open(self.file, 'r')as inf:
                lic_data = inf.read()
            return lic_data
        except IOError as ex:
            raise ex
        
    def text_font(self):
        '''set document font'''
        doc_font=QFont('Helvetica [Cronyx]',10,QFont.Bold)
        return doc_font
