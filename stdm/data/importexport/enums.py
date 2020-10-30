"""
Enums for use in the STDM Import/Export module
"""
__author__ = 'John Gitau'
__license__ = 'GNU Lesser General Public License (LGPL)'
__url__ = 'http://www.unhabitat.org'

try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr

drivers = {
    "shp": "ESRI Shapefile",
    "csv": "CSV",
    "tab": "MapInfo File",
    "gpx": "GPX",
    "dxf": "DXF"
}

ogrTypes = {
    "character varying": ogr.OFTString,
    "bigint": ogr.OFTInteger,
    "bigserial": ogr.OFTInteger,
    "boolean": ogr.OFTString,
    "bytea": ogr.OFTBinary,
    "character": ogr.OFTString,
    "date": ogr.OFTDate,
    "double precision": ogr.OFTReal,
    "integer": ogr.OFTInteger,
    "numeric": ogr.OFTReal,
    "real": ogr.OFTReal,
    "smallint": ogr.OFTInteger,
    "serial": ogr.OFTInteger,
    "text": ogr.OFTString,
    "timestamp without time zone": ogr.OFTDateTime
}

# WKT geometry mappings
wkbTypes = {
    "POINT": ogr.wkbPoint,
    "LINESTRING": ogr.wkbLineString,
    "POLYGON": ogr.wkbPolygon,
    "MULTIPOINT": ogr.wkbMultiPoint,
    "MULTILINESTRING": ogr.wkbMultiLineString,
    "MULTIPOLYGON": ogr.wkbMultiPolygon,
    "GEOMETRYCOLLECTION": ogr.wkbGeometryCollection
}
