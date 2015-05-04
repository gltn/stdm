"""
/***************************************************************************
Name                 : Social Tenure Domain Model
Description          : QGIS Entry Point for Social Tenure Domain Model
Date                 : 04-01-2015
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
import sys
import os

third_party_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "third_party"))
font_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "third_party/fontTools"))

if third_party_dir not in sys.path:
    sys.path.append(third_party_dir)
    sys.path.append(font_dir)


def classFactory(iface):
    """
    Load STDMQGISLoader class from file stdm
    """

    from stdm import STDMQGISLoader
    return STDMQGISLoader(iface)
