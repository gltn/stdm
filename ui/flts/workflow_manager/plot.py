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

    def set_file_path(self, fpath):
        """
        Sets plot import file absolute path
        :param fpath: Plot import file absolute path
        :rtype fpath: String
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
    #
    # @staticmethod
    # def delimiters():
    #     """
    #     Returns delimiters
    #     :return: Delimiters
    #     :rtype: List
    #     """
    #     return OrderedDict({"Tab": "\t", "Comma": ",", "Semicolon": ";"})

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

    def get_row_data(self):
        """
        File properties method wrapper
        :return: Plot import file data properties
        :rtype: List
        """
        return self._file_properties(self._fpath)

    def _file_properties(self, fpath):
        """
        Returns plot import file data properties
        :param fpath: Plot import file absolute path
        :rtype fpath: String
        :return results: Plot import file data properties
        :return results: List
        """
        results = []
        properties = {}
        try:
            file_extension = QFileInfo(fpath).completeSuffix()
            delimiter = self._get_delimiter(fpath)
            for n, prop in enumerate(self._data_service.columns):
                if prop.name == "Name":
                    properties[n] = QFileInfo(fpath).fileName()
                elif prop.name == "Import as":
                    properties[n] = unicode(self._get_import_type(fpath))
                elif prop.name == "Delimiter":
                    properties[n] = unicode(delimiter)
                elif prop.name == "Header row":
                    properties[n] = float(1) if file_extension != "pdf" else ""
                elif prop.name == "Geometry field":
                    # Get possible header row
                    properties[n] = unicode("Test")
                else:
                    properties[n] = unicode("")
        except (csv.Error, Exception) as e:
            raise e
        results.append(properties)
        return results

    @staticmethod
    def _get_delimiter(fpath):
        """
        Returns default plain text common delimiter
        :param fpath: Plot import file absolute path
        :rtype fpath: String
        :return: Default common delimiter
        :rtype: Unicode
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension not in ("csv", "txt"):
            return ""
        try:
            with open(fpath, 'r') as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.readline(4096))
                delimiter = dialect.delimiter
                options = {"\t": "Tab", ",": "Comma", ";": "Semicolon"}
                if delimiter in options.keys():
                    return options[delimiter]
                return delimiter
        except (csv.Error, Exception) as e:
            raise e

    @staticmethod
    def _get_import_type(fpath):
        """
        Returns default import type based on file extension
        :param fpath: Plot import file absolute path
        :rtype fpath: String
        :return: Default import type
        :rtype: String
        """
        file_extension = QFileInfo(fpath).completeSuffix()
        if file_extension == "pdf":
            return "Field Book"
        return "Plots"

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns


