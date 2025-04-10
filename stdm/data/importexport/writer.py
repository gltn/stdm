"""
begin:            26th March 2012
copyright:        (c) 2012 by John Gitau
email:            gkahiu@gmail.com
about:            Wrapper class for writing PostgreSQL/PostGIS tables to user-defined OGR formats
"""

import datetime

from qgis.PyQt.QtCore import (
    QFileInfo,
    Qt
)
from qgis.PyQt.QtWidgets import (
    QProgressDialog,
    QApplication
)

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

from stdm.exceptions import DummyException
from stdm.data.pg_utils import (
    columnType,
    geometryType
)
from stdm.settings import (
    current_profile
)
from stdm.data.importexport.enums import (
    ogrTypes,
    wkbTypes,
    drivers
)


class OGRWriter():
    OGR_STRING_TYPE = 4
    OGR_DATE_TYPE = 9

    def __init__(self, targetFile):
        self._ds = None
        self._targetFile = targetFile

    def reset(self):
        # Destroy
        self._ds = None

    def getDriverName(self):
        # Return the name of the driver derived from the file extension
        fi = QFileInfo(self._targetFile)
        fileExt = str(fi.suffix())

        return drivers[fileExt]

    def getLayerName(self):
        # Simply derived from the file name
        fi = QFileInfo(self._targetFile)

        return str(fi.baseName())

    def createField(self, table, field):
        # Creates an OGR field

        colType = columnType(table, field)
        # Get OGR type
        ogrType = ogrTypes[colType]

        # OGR date handling is broken! handle all dates as strings
        if ogrType == OGRWriter.OGR_DATE_TYPE:
            ogrType = OGRWriter.OGR_STRING_TYPE

        field_defn = ogr.FieldDefn(field, ogrType)

        return field_defn

    def db2Feat(self, parent, table, results, columns, geom=""):
        # Execute the export process
        # Create driver
        drv = ogr.GetDriverByName(self.getDriverName())
        if drv is None:
            raise Exception("{0} driver not available.".format(self.getDriverName()))

        # Create data source
        self._ds = drv.CreateDataSource(self._targetFile)
        if self._ds is None:
            msg = f"Creation of output file: \n {self._targetFile} failed! \n\n Check if the file is opened."
            raise Exception(msg)

        dest_crs = None
        # Create layer
        if geom != "":
            pgGeomType, srid = geometryType(table, geom)
            geomType = wkbTypes[pgGeomType]
            try:
                dest_crs = ogr.osr.SpatialReference()
            except AttributeError:
                dest_crs = osr.SpatialReference()
            dest_crs.ImportFromEPSG(srid)

        else:
            geomType = ogr.wkbNone
        layer_name = self.getLayerName()

        lyr = self._ds.CreateLayer(layer_name, dest_crs, geomType)

        if lyr is None:
            raise Exception("Layer creation failed")

        # Create fields
        for c in columns:

            field_defn = self.createField(table, c)

            if lyr.CreateField(field_defn) != 0:
                raise Exception("Creating %s field failed" % (c))

        # Add Geometry column to list for referencing in the result set
        if geom != "":
            columns.append(geom)

        featGeom = None

        # Configure progress dialog
        initVal = 0
        numFeat = results.rowcount
        progress = QProgressDialog("", "&Cancel", initVal, numFeat, parent)
        progress.setWindowModality(Qt.WindowModal)
        lblMsgTemp = QApplication.translate(
            'OGRWriter', 'Writing {0} of {1} to file...')

        entity = current_profile().entity_by_name(table)
        # Iterate the result set
        for r in results:
            # Progress dialog
            progress.setValue(initVal)
            progressMsg = lblMsgTemp.format(str(initVal + 1), str(numFeat))
            progress.setLabelText(progressMsg)

            if progress.wasCanceled():
                break

            # Create OGR Feature
            feat = ogr.Feature(lyr.GetLayerDefn())

            for i in range(len(columns)):
                colName = columns[i]

                # Check if its the geometry column in the iteration
                if colName == geom:
                    if r[i] is not None:
                        featGeom = ogr.CreateGeometryFromWkt(r[i])
                    else:
                        featGeom = ogr.CreateGeometryFromWkt("")

                    feat.SetGeometry(featGeom)

                else:
                    field_value = r[i]
                    feat.SetField(i, str(field_value))

            if lyr.CreateFeature(feat) != 0:
                progress.close()
                progress.deleteLater()
                del progress
                raise Exception(
                    "Failed to create feature in %s" % (self._targetFile)
                )

            if featGeom is not None:
                featGeom.Destroy()

            feat.Destroy()
            initVal += 1

        progress.setValue(numFeat)
        progress.deleteLater()
        del progress

    @staticmethod
    def is_date(string):
        return True if isinstance(string, datetime.date) else False

        # try:
        # date = datetime.datetime.strptime(string, "%Y-%m-%d").date()

        # return True
        # except Exception:
        # return False

    def is_decimal(self, number):
        try:
            n = round(number)

            return True
        except DummyException:
            return False
