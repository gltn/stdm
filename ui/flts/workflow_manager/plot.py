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
    Qt,
    QFile,
    QFileInfo,
    QIODevice
)
from qgis.core import QgsGeometry

NAME, IMPORT_AS, DELIMITER, HEADER_ROW, CRS_ID, \
GEOM_FIELD, GEOM_TYPE = range(7)

# PARCEL_NUM, UPI_NUM, GEOMETRY, AREA = range(4)
PARCEL_NUM, AREA = range(2)


class Item:
    """
    Items associated properties
    """
    def __init__(self, flags=None, tootltip=None, icon_id=None):
        self.flags = flags if flags else []
        self.tooltip = tootltip
        self.icon_id = icon_id


class Plot(object):
    """
    Plot associated methods
    """
    def __init__(self):
        self._reg_exes = {
            "type_str": re.compile(r'^\s*([\w\s]+)\s*\(\s*(.*)\s*\)\s*$'),
        }

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
        :return: Geometry type
        :rtype: String
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
                        geom_type, geom = self._geometry(value)
                        if geom_type:
                            if geom_type not in match_count:
                                match_count[geom_type] = 0
                                continue
                            match_count[geom_type] += 1
                return self._default_geometry_type(match_count)
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
        :return geom_type: Geometry type
        :rtype geom_type: String
        :return geom: Geometry
        :rtype geom: QgsGeometry
        """
        geom_type = geom = None
        matches = self._reg_exes["type_str"].match(wkt)
        if matches:
            geom_type, coordinates = matches.groups()
            geom = QgsGeometry.fromWkt(wkt.strip())
            if geom_type:
                geom_type = geom_type.strip()
                geom_type = geom_type.lower().capitalize()
        return geom_type, geom

    @staticmethod
    def _default_geometry_type(type_count):
        """
        Returns default plot import file geometry type
        :param type_count: Geometry type count
        :type type_count: Dictionary
        :return geom_type: Default geometry type
        :rtype geom_type: String
        """
        geom_type = None
        if type_count:
            geom_type = max(
                type_count.iterkeys(),
                key=lambda k: type_count[k]
            )
        return geom_type

    @property
    def _geometry_types(self):
        """
        Returns a map of expected geometry types
        :return: Geometry types
        :rtype: OrderedDict
        """
        return OrderedDict({
            "Point": "Point", "Linestring": "Line", "Polygon": "Polygon"
        })

    @staticmethod
    def _decoration_tooltip(tip):
        """
        Returns decoration role tooltip item
        :param tip: Tooltip message
        :type tip: String
        :return: Decoration tooltip item
        :return: Item
        """
        return Item([Qt.DecorationRole, Qt.ToolTipRole], unicode(tip))


class PlotPreview(Plot):
    """
    Manages preview of plot import data file contents
    """
    def __init__(self, data_service, file_settings):
        """
        :param data_service: Plot preview data model service
        :type data_service: PlotImportFileDataService
        :param file_settings: Plot import file data settings
        :type file_settings: Dictionary
        """
        super(PlotPreview, self).__init__()
        self._data_service = data_service
        self._items = None
        self._num_errors = 0
        self._header_row = file_settings.get(HEADER_ROW) - 1
        self._delimiter = self._get_delimiter(file_settings.get(DELIMITER))
        self._geom_type = file_settings.get(GEOM_TYPE)
        self._fpath = file_settings.get("fpath")
        self._file_fields = file_settings.get("fields")

    @staticmethod
    def _get_delimiter(name):
        """
        Returns a delimiter
        :param name: Delimiter name
        :param name: Unicode
        :return: Delimiter
        :rtype: String
        """
        delimiter = str(name.split(" ")[0]).strip()
        if delimiter == "t":
            delimiter = "\t"
        return delimiter

    def num_errors(self):
        """
        Returns number of errors encountered on preview
        :return: Number of errors on preview
        :return: Integer
        """
        return self._num_errors

    def load(self):
        """
        Loads plot import file contents
        :return: Plot import file data settings
        :rtype: List
        """
        try:
            qfile = QFile(self._fpath)
            if not qfile.open(QIODevice.ReadOnly):
                raise IOError(unicode(qfile.errorString()))
            return self._file_contents(self._fpath)
        except(IOError, OSError, csv.Error, NotImplementedError, Exception) as e:
            raise e

    def _file_contents(self, fpath):
        """
        Returns plot import file contents
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file contents
        :rtype results: List
        """
        results = []
        self._num_errors = 0
        try:
            with open(fpath, 'r') as csv_file:
                clean_line = self._filter_whitespace(csv_file, self._header_row)
                csv_reader = csv.DictReader(
                    clean_line,
                    fieldnames=self._file_fields,
                    delimiter=self._delimiter
                )
                self._geom_type = self._geometry_type()
                for row, data in enumerate(csv_reader):
                    contents = {}
                    self._items = {}
                    value = self._get_value(
                        data, ("parcel", "parcel number", "id"), PARCEL_NUM
                    )
                    contents[PARCEL_NUM] = unicode(value)
                    # Generate UPI Number
                    # Geometry
                    value = self._get_value(data, ("area",), AREA)
                    contents[AREA] = self._to_float(value, AREA)
                    contents["items"] = self._items
                    results.append(contents)
        except (csv.Error, Exception) as e:
            raise e
        return results

    @staticmethod
    def _filter_whitespace(in_file, hrow):
        """
        Returns non-whitespace line of data
        :param in_file: Input file
        :param in_file: TextIOWrapper
        :param hrow: Header row number
        :type hrow: Integer
        :return line: Non-whitespace line
        :return line: generator
        """
        for row, line in enumerate(in_file):
            if row == hrow:
                continue
            if not line.isspace():
                yield line

    def _geometry_type(self):
        """
        Returns dominant geometry type of
        loaded plot import file
        :return _geom_type: Dominant geometry type
        :rtype _geom_type: String
        """
        if self._geom_type not in self._geometry_types.values():
            self._geom_type = self.geometry_type(
                self._fpath, self._header_row, self._delimiter
            )
        return self._geom_type

    def _get_value(self, data, field_names, column):
        """
        Returns plot import file value given field names
        :param data: Plot import file contents
        :type data: generator
        :param field_names: Plot import file field names
        :type field_names: Tuple/List
        :param column: Table view column position
        :type column: Integer
        :return value: Plot import
        :return value: Object
        """
        value = self._field_value(data, field_names)
        if not str(value) or not str(value).strip():
            value = "Warning"
            self._items[column] = self._decoration_tooltip("Missing value")
            self._num_errors += 1
        return value

    @staticmethod
    def _field_value(data, field_names):
        """
        Returns plot import file field value given field names
        :param data: Plot import file contents
        :type data: generator
        :param field_names: Plot import file field names
        :type field_names: Tuple/List
        :return value: Plot import file field value
        :rtype value: Object
        """
        fields = {name.lower(): name for name in data.keys()}
        for name in field_names:
            name = name.lower()
            if name in fields:
                return data.get(fields[name])

    def _to_float(self, value, column):
        """
        Casts value to float
        :param value: Value object
        :type value: Object
        :param column: Table view column position
        :type column: Integer
        :return value: Float or other object types
        :return value: Object
        """
        if self._is_number(value):
            value = float(value)
        else:
            if value != "Warning":
                self._items[column] = \
                    self._display_tooltip("Value is not a number", "Warning")
                self._num_errors += 1
        return value

    @staticmethod
    def _is_number(value):
        """
        Checks if value is a number
        :param value: Input value
        :type value: Object
        :return: True if number otherwise return False
        :rtype: Boolean
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError, Exception):
            return False

    @staticmethod
    def _display_tooltip(tip, icon_id):
        """
        Returns display and decoration role tooltip item
        :param tip: Tooltip message
        :type tip: String
        :param icon_id: Icon identifier
        :type icon_id: String
        :return: Decoration tooltip item
        :return: Item
        """
        return Item(
            [Qt.DisplayRole, Qt.DecorationRole, Qt.ToolTipRole],
            unicode(tip),
            icon_id
        )

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns


class PlotFile(Plot):
    """
    Manages plot import data file settings
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
        super(PlotFile, self).__init__()

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

    @property
    def file_paths(self):
        """
        Returns plot import file absolute paths
        :return _fpaths: Plot import file absolute paths
        :rtype _fpaths: List
        """
        return self._fpaths

    def remove_filepath(self, item):
        """
        Removes stored file path
        :param item: Item to be removed
        :type item: Object
        """
        if item in self._fpaths:
            self._fpaths.remove(item)

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
    def geometry_options(self):
        """
        Returns a map of expected geometry
        type options for the 'Type' column
        :return geom_options: Geometry type options
        :rtype geom_options: OrderedDict
        """
        geom_options = OrderedDict({"Detect": "Detect"})
        geom_options.update(self._geometry_types)
        return geom_options

    def load(self):
        """
        Loads plot import file data settings
        :return: Plot import file data settings
        :rtype: List
        """
        try:
            qfile = QFile(self._fpath)
            if not qfile.open(QIODevice.ReadOnly):
                raise IOError(unicode(qfile.errorString()))
            self.remove_filepath(self._fpath)
            if not self.is_pdf(self._fpath) and self._is_wkt(self._fpath):
                return self._file_settings(self._fpath)
            return self._file_settings(self._fpath)
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
                        geom_type, geom = self._geometry(value)
                        if geom:
                            count += 1
                total_rows = self.row_count(fpath)
                if self._calc_ratio(total_rows, sample_size, count) < 0.5:
                    raise NotImplementedError(
                        'Most of the lines in "{}" file are invalid'.format(fname)
                    )
        except (IOError, csv.Error, NotImplementedError, Exception) as e:
            raise e
        else:
            return True

    def _file_settings(self, fpath):
        """
        Returns plot import file data settings
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file data settings
        :rtype results: List
        """
        settings = {}
        items = {}
        try:
            header_row = 1
            row = header_row - 1
            delimiter = self._get_csv_delimiter(fpath)
            for pos, column in enumerate(self._data_service.columns):
                if pos == NAME:
                    settings[pos] = QFileInfo(fpath).fileName()
                elif pos == IMPORT_AS:
                    settings[pos] = unicode(self._get_import_type(fpath))
                elif pos == DELIMITER:
                    settings[pos] = unicode(self._delimiter_name(delimiter))
                elif pos == HEADER_ROW:
                    settings[pos] = header_row \
                        if not self.is_pdf(fpath) else unicode("")
                elif pos == GEOM_FIELD:
                    fields = self.get_csv_fields(fpath, row, delimiter)
                    settings["fields"] = fields
                    if fields:
                        fields = self.geometry_field(fpath, fields, row, delimiter)
                    else:
                        fields = ""
                    settings[pos] = unicode(fields)
                elif pos == GEOM_TYPE:
                    geom_type = self.geometry_type(fpath, row, delimiter)
                    if geom_type and not self._geometry_types.get(geom_type):
                        geom_type = "Detect"
                    elif not geom_type:
                        geom_type = ""
                    settings[pos] = unicode(geom_type)
                elif pos == CRS_ID:
                    if not self.is_pdf(fpath):
                        settings[pos] = unicode("Warning")
                        tip = "Missing Coordinate Reference System (CRS)"
                        items[pos] = self._decoration_tooltip(tip)
                settings["items"] = items
                settings["fpath"] = unicode(fpath)
        except (csv.Error, Exception) as e:
            raise e
        self._fpaths.append(fpath)
        results = [settings]
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

    @staticmethod
    def _calc_ratio(rows, sample, count):
        """
        Returns ratio of valid WKT lines to total or sample rows
        :param rows: Total rows/lines in a WKT file
        :type rows: Integer
        :param sample: Sampled rows/lines
        :type sample: Integer
        :param count: Number of valid rows
        :type count: Integer
        :return ratio: Ratio of valid WKT lines/rows
        :rtype ratio: Float
        """
        if sample <= rows:
            ratio = float(count) / float(sample)
        else:
            ratio = float(count) / float(rows)
        return ratio

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

