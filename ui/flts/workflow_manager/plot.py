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


class PlotFile:
    """
    Manages plot import data file properties
    """
    formats = ["csv", "txt", "pdf"]
    reg_exes = {
        "type_str": re.compile(r'^\s*([\w\s]+)\s*\(\s*(.*)\s*\)\s*$'),
    }

    def __init__(self, data_service):
        """
        :param data_service: Plot import file data model service
        :type data_service: PlotImportFileDataService
        """
        self._data_service = data_service
        self._fpath = None
        self._fpaths = []

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
        extension = ["*" + fmt for fmt in self.formats]
        return extension

    # @staticmethod
    # def import_as():
    #     """
    #     Returns import types
    #     :return: Import types
    #     :rtype: List
    #     """
    #     return ["Plots", "Beacons", "Servitudes", "Field Book"]

    @property
    def delimiters(self):
        """
        Returns delimiters
        :return: Delimiters
        :rtype: Dictionary
        """
        return OrderedDict({",": "Comma", ";": "Semicolon", "\t": "Tab"})

    def get_row_data(self):
        """
        File properties method wrapper
        :return: Plot import file data properties
        :rtype: List
        """
        return self._file_properties(self._fpath)

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
            return self._file_properties(self._fpath)
        except(IOError, OSError, Exception) as e:
            raise e

    def _file_properties(self, fpath):
        """
        Returns plot import file data properties
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file data properties
        :return results: List
        """
        results = []
        properties = {}
        try:
            header_row = 1
            file_extension = QFileInfo(fpath).completeSuffix()
            delimiter = self._get_csv_delimiter(fpath)
            for n, prop in enumerate(self._data_service.columns):
                if prop.name == "Name":
                    properties[n] = QFileInfo(fpath).fileName()
                elif prop.name == "Import as":
                    properties[n] = unicode(self._get_import_type(fpath))
                elif prop.name == "Delimiter":
                    properties[n] = unicode(self._delimiter_name(delimiter))
                elif prop.name == "Header row":
                    properties[n] = float(header_row) \
                        if file_extension != self.formats[-1] else unicode("")
                elif prop.name == "Geometry field":
                    row = header_row - 1
                    fields = self.get_csv_fields(fpath, row, delimiter)
                    if fields:
                        fields = self.geometry_field(fpath, fields, row, delimiter)
                    else:
                        fields = ""
                    properties[n] = unicode(fields)
                else:
                    properties[n] = unicode("")
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
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in self.formats[:-1]:
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
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension == self.formats[-1]:
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
        if delimiter not in self.delimiters.keys():
            return "{0} {1}".format("Custom", delimiter)
        return "{0} {1}".format(self.delimiters[delimiter], delimiter)

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
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in self.formats[:-1]:
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                fields = next(
                    (line for row, line in enumerate(csv_reader) if row == hrow), []
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
        :return goemetry_field: CSV field names
        :rtype goemetry_field: List
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in self.formats[:-1]:
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
                        matches = self.reg_exes["type_str"].match(value)
                        if matches:
                            match_count[field] += 1
                        else:
                            continue
                return max(
                    match_count.iterkeys(),
                    key=lambda k: match_count[k]
                )
        except (csv.Error, Exception) as e:
            raise e

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns

