"""
/***************************************************************************
Name                 : Social Tenure Domain Model
Description          : QGIS Entry Point for Social Tenure Domain Model 
Date                 : 23/May/13
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import sys
import os

third_party_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),"third_party"))
font_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),"third_party/fontTools"))

if not third_party_dir in sys.path:
    sys.path.append(third_party_dir)
    sys.path.append(font_dir)

def classFactory(iface): 
    from stdm import STDMQGISLoader 
    return STDMQGISLoader(iface)
