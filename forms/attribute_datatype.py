"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
email                : njoroge.solomon.com
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
from stdm.data import tableColType
class AttributePropretyType(object):
    def __init__(self, model):
        self.model=model
        
    def attributeType(self):
        #Enumerate column and datatype
        typeMapping=tableColType(self.model)
        return typeMapping
    
    def displayMapping(self):
        #user the mapped table properties
        pass
        
    