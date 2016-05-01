"""
/***************************************************************************
Name                 : ConfigurationException
Description          : ConfigurationException
Date                 : 22/December/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
class ConfigurationException(Exception):
    """
    Raised when there is an error in StdmConfiguration
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)