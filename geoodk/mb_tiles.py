"""

"""
from osgeo import osr,gdal


def convert_to_mbtiles(input_file, outputfile):
    """
    method to convert gdal file(TIFF) to MBTiles
    :param self:
    :return:file
    """
    return gdal.Translate(input_file, outputfile)

