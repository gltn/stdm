"""
/***************************************************************************
Name                 : MB Tile converter
Description          : class to read and convert a tiff image to mb tiles.
Date                 : 26/May/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from osgeo import osr,gdal


def convert_to_mbtiles(input_file, outputfile):
    """
    method to convert gdal file(TIFF) to MBTiles
    :param self:
    :return:file
    """
    return gdal.Translate(input_file, outputfile)

