"""
/***************************************************************************
Name                 : STDM Report Builder Title Dialog
Description          : Title Dialog
Date                 : 07/September/11 
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
from .report_title_base import TitleBase

class Title(TitleBase):     
    #Class constructor  
    def __init__(self,id):         
        TitleBase.__init__(self,id) 
    
    def getSystemField(self):
        #Construct and return the Title System Field
        pass
                
        
