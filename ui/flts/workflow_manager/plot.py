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
    def __init__(self, data_service):
        """
        :param data_service: Plot import file data model service
        :type data_service: PlotImportFileDataService
        """
        self._data_service = data_service
        self._fpath = None
        self._fpaths = []
        self._delimiters = {",": "Comma", ";": "Semicolon", "\t": "Tab"}

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

    @staticmethod
    def formats():
        """
        Returns plot import file format types
        :return: Plot import file format types
        :rtype: String
        """
        return "*.csv *.txt *.pdf"

    # @staticmethod
    # def import_as():
    #     """
    #     Returns import types
    #     :return: Import types
    #     :rtype: List
    #     """
    #     return ["Plots", "Beacons", "Servitudes", "Field Book"]

    def delimiters(self):
        """
        Returns delimiters
        :return: Delimiters
        :rtype: Dictionary
        """
        return self._delimiters

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
            self.set_delimiter(delimiter)
            for n, prop in enumerate(self._data_service.columns):
                if prop.name == "Name":
                    properties[n] = QFileInfo(fpath).fileName()
                elif prop.name == "Import as":
                    properties[n] = unicode(self._get_import_type(fpath))
                elif prop.name == "Delimiter":
                    name = "{0} ( {1} )".format(self._delimiters[delimiter], delimiter) if delimiter else ""
                    properties[n] = unicode(name)
                elif prop.name == "Header row":
                    header_row = 1
                    properties[n] = float(header_row) if file_extension != "pdf" else unicode("")
                elif prop.name == "Geometry field":
                    field_names = self.get_csv_fields(
                        fpath, header_row - 1, delimiter
                    )
                    properties[n] = unicode(field_names[0]) if field_names else unicode("")
                else:
                    properties[n] = unicode("")
        except (csv.Error, Exception) as e:
            raise e
        self._fpaths.append(fpath)
        results.append(properties)
        return results

    @staticmethod
    def _get_csv_delimiter(fpath):
        """
        Returns default plain text common delimiter
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default common delimiter
        :rtype: Unicode
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in ("csv", "txt"):
            return
        try:
            with open(fpath, 'r') as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.readline(4096))
                return dialect.delimiter
        except (csv.Error, Exception) as e:
            raise e

    def set_delimiter(self, delimiter):
        """
        Sets custom/new delimiter
        :param delimiter: delimiter
        :type delimiter: String
        """
        if delimiter and delimiter not in self._delimiters.keys():
            self._delimiters[delimiter] = "Custom"

    @staticmethod
    def _get_import_type(fpath):
        """
        Returns default import type based on file extension
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default import type
        :rtype: String
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension == "pdf":
            return "Field Book"
        return "Plots"

    @staticmethod
    def get_csv_fields(fpath, row, delimiter=None):
        """
        Returns plain text field names
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param row: Header row number
        :type row: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return: CSV field names
        :rtype: List
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in ("csv", "txt"):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                csv_reader = list(csv_reader)
                return csv_reader[row]
        except (csv.Error, Exception) as e:
            raise e

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns

