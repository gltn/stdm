"""
/***************************************************************************
Name                 : Plot
Description          : Module for managing importing of a scheme plot.
Date                 : 24/December/2019
copyright            : (C) 2019
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
import re
import itertools
from collections import OrderedDict
import csv
from PyQt4.QtCore import (
    QFile,
    QFileInfo,
    QIODevice
)
from qgis.core import QgsGeometry

NAME, IMPORT_AS, DELIMITER, HEADER_ROW, \
GEOM_FIELD, GEOM_TYPE, CRS_ID = range(7)


class PlotFile:
    """
    Manages plot import data file properties
    """
    def __init__(self, data_service):
        """
        :param data_service: Plot import file data model service
        :type data_service: PlotImportFileDataService
        """
        self._data_service = data_service
        self._fpath = None
        self._fpaths = []
        self._formats = ["csv", "txt", "pdf"]
        self._reg_exes = {
            "type_str": re.compile(r'^\s*([\w\s]+)\s*\(\s*(.*)\s*\)\s*$'),
        }

    def set_file_path(self, fpath):
        """
        Sets plot import file absolute path
        :param fpath: Plot import file absolute path
        :type fpath: String
        """
        self._fpath = fpath

    @property
    def file_path(self):
        """
        Returns plot import file absolute path
        :return _fpath: Plot import file absolute path
        :rtype _fpath: String
        """
        return self._fpath

    def file_paths(self):
        """
        Returns plot import file absolute paths
        :return _fpaths: Plot import file absolute paths
        :rtype _fpaths: List
        """
        return self._fpaths

    def file_extensions(self):
        """
        Returns plot import file extensions
        :return extension: Plot import file extensions
        :rtype extension: List
        """
        extension = ["*." + fmt for fmt in self._formats]
        return extension

    @staticmethod
    def import_as():
        """
        Returns import types
        :return: Import types
        :rtype: List
        """
        return ["Beacons", "Plots", "Servitudes"]

    def delimiter_names(self):
        """
        Returns delimiters full name
        :return names: Delimiters full name
        :rtype names: OrderedDict
        """
        names = OrderedDict()
        for k, d in sorted(self.delimiters.items()):
            name = "{0} {1}".format(k, d)
            if k == "\t":
                k = "t"
                names[k] = "{0} {1}".format(k, d)
            else:
                names[k] = name
        return names

    @property
    def delimiters(self):
        """
        Returns delimiters
        :return: Delimiters
        :rtype: Dictionary
        """
        return OrderedDict({",": "Comma", ";": "Semicolon", "\t": "Tab"})

    @property
    def geometry_types(self):
        """
        Returns list of expected geometry types
        :return: Geometry types
        :rtype: List
        """
        return OrderedDict({
            "Detect": "Detect", "Point": "Point",
            "Linestring": "Line", "Polygon": "Polygon"
        })

    def load(self):
        """
        Loads plot import file data properties
        :return: Plot import file data properties
        :rtype: List
        """
        try:
            qfile = QFile(self._fpath)
            if not qfile.open(QIODevice.ReadOnly):
                raise IOError(unicode(qfile.errorString()))
            if not self.is_pdf(self._fpath) and self._is_wkt(self._fpath):
                return self._file_properties(self._fpath)
            return self._file_properties(self._fpath)
        except(IOError, OSError, csv.Error, NotImplementedError, Exception) as e:
            raise e

    def _is_wkt(self, fpath):
        """
        Checks if the plot import file is a valid WKT
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Returns true if valid
        :rtype: Boolean
        """
        try:
            fname = QFileInfo(fpath).fileName()
            if QFileInfo(fpath).size() == 0:
                raise NotImplementedError(
                    'The file "{}" is empty.'.format(fname)
                )
            delimiter = self._get_csv_delimiter(fpath)
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                sample_size = 5000
                sample = itertools.islice(csv_reader, sample_size)
                count = 0
                for row, data in enumerate(sample):
                    for value in data:
                        if value is None or isinstance(value, list):
                            continue
                        geo_type, geom = self._geometry(value)
                        if geom and geo_type in self.geometry_types:
                            count += 1
                total_rows = self.row_count(fpath)
                if sample_size <= total_rows:
                    ratio = float(count) / float(sample_size)
                else:
                    ratio = float(count) / float(total_rows)
                if ratio < 0.5:
                    raise NotImplementedError(
                        'Most of the lines in "{}" file are invalid'.format(fname)
                    )
        except (IOError, csv.Error, NotImplementedError, Exception) as e:
            raise e
        else:
            return True

    def _file_properties(self, fpath):
        """
        Returns plot import file data properties
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file data properties
        :rtype results: List
        """
        results = []
        properties = {}
        try:
            header_row = 1
            row = header_row - 1
            delimiter = self._get_csv_delimiter(fpath)
            for pos, column in enumerate(self._data_service.columns):
                if pos == NAME:
                    properties[pos] = QFileInfo(fpath).fileName()
                elif pos == IMPORT_AS:
                    properties[pos] = unicode(self._get_import_type(fpath))
                elif pos == DELIMITER:
                    properties[pos] = unicode(self._delimiter_name(delimiter))
                elif pos == HEADER_ROW:
                    properties[pos] = header_row \
                        if not self.is_pdf(fpath) else unicode("")
                elif pos == GEOM_FIELD:
                    fields = self.get_csv_fields(fpath, row, delimiter)
                    if fields:
                        fields = self.geometry_field(fpath, fields, row, delimiter)
                    else:
                        fields = ""
                    properties[pos] = unicode(fields)
                elif pos == GEOM_TYPE:
                    geo_type = self.geometry_type(fpath, row, delimiter)
                    properties[pos] = unicode(geo_type) if geo_type else ""
                else:
                    properties[pos] = unicode("")
                properties["fpath"] = unicode(fpath)
        except (csv.Error, Exception) as e:
            raise e
        self._fpaths.append(fpath)
        results.append(properties)
        return results

    def _get_csv_delimiter(self, fpath):
        """
        Returns default plain text common delimiter
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default common delimiter
        :rtype: Unicode
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.readline(4096))
                return dialect.delimiter
        except (csv.Error, Exception) as e:
            raise e

    def _get_import_type(self, fpath):
        """
        Returns default import type based on file extension
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default import type
        :rtype: String
        """
        if self.is_pdf(fpath):
            return "Field Book"
        return "Plots"

    def _delimiter_name(self, delimiter):
        """
        Returns delimiter full name
        :param delimiter: Delimiter
        :type delimiter: String
        :return: Delimiter full name
        :return: String
        """
        if not delimiter:
            return ""
        elif delimiter not in self.delimiters.keys():
            return "{0} {1}".format(delimiter, "Custom")
        elif delimiter == "\t":
            return "{0} {1}".format("t", self.delimiters[delimiter])
        else:
            return "{0} {1}".format(delimiter, self.delimiters[delimiter])

    def get_csv_fields(self, fpath, hrow=0, delimiter=None):
        """
        Returns plain text field names
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return fields: CSV field names
        :rtype fields: List
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                fields = next(
                    (data for row, data in enumerate(csv_reader) if row == hrow), []
                )
                return fields
        except (csv.Error, Exception) as e:
            raise e

    def geometry_field(self, fpath, fields, hrow=0, delimiter=None):
        """
        Returns possible geometry field from
        list of fields given a plain text file
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param fields: CSV field names
        :type fields: List
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return: Geometry field
        :rtype: String
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.DictReader(
                    csv_file, fieldnames=fields, delimiter=delimiter
                )
                match_count = {field: 0 for field in fields}
                sample = itertools.islice(csv_reader, 5000)
                for row, data in enumerate(sample):
                    if row == hrow:
                        continue
                    for field, value in data.items():
                        if value is None or isinstance(value, list):
                            continue
                        matches = self._reg_exes["type_str"].match(value)
                        if matches:
                            match_count[field] += 1
                return max(
                    match_count.iterkeys(),
                    key=lambda k: match_count[k]
                )
        except (csv.Error, Exception) as e:
            raise e

    def geometry_type(self, fpath, hrow=0, delimiter=None):
        """
        Returns dominant geometry type of
        loaded plot import file - CSV/txt
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return geo_type: Geometry type
        :rtype geo_type: String
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                sample = itertools.islice(csv_reader, 5000)
                match_count = {}
                for row, data in enumerate(sample):
                    if row == hrow:
                        continue
                    for value in data:
                        if value is None or isinstance(value, list):
                            continue
                        geo_type, geom = self._geometry(value)
                        if geo_type:
                            if geo_type not in match_count:
                                match_count[geo_type] = 0
                                continue
                            match_count[geo_type] += 1
                geo_type = None
                if match_count:
                    geo_type = max(
                        match_count.iterkeys(),
                        key=lambda k: match_count[k]
                    )
                    geo_type = self.geometry_types.get(geo_type)
                geo_type = geo_type if geo_type else "Detect"
                return geo_type
        except (csv.Error, Exception) as e:
            raise e

    @staticmethod
    def is_pdf(fpath):
        """
        Checks if the file extension is PDF
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return True: Returns true if the file extension is PDF
        :rtype True: Boolean
        """

        file_extension = QFileInfo(fpath).suffix()
        if file_extension == "pdf":
            return True

    def _geometry(self, wkt):
        """
        Returns geometry and geometry type given WKT data
        :param wkt: WKT data
        :type wkt: String
        :return geo_type: Geometry type
        :rtype geo_type: String
        :return geom: Geometry
        :rtype geom: QgsGeometry
        """
        geo_type = geom = None
        matches = self._reg_exes["type_str"].match(wkt)
        if matches:
            geo_type, coordinates = matches.groups()
            geom = QgsGeometry.fromWkt(wkt.strip())
            if geo_type:
                geo_type = geo_type.strip()
                geo_type = geo_type.lower().capitalize()
        return geo_type, geom

    def row_count(self, fpath):
        """
        Returns total number of rows/lines in a CSV/txt file
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Total number of rows/lines
        :rtype: Integer
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, "r") as csv_file:
                return sum(1 for line in csv_file)
        except (csv.Error, Exception) as e:
            raise e

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns

