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
        return "*.csv *.txt"

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
            return self._file_properties(qfile)
        except(IOError, OSError) as e:
            raise e

    def get_row_data(self):
        """
        File properties method wrapper
        :return: Plot import file data properties
        :rtype: List
        """
        return self._file_properties(self._fpath)

    def _file_properties(self, qfile):
        """
        Returns plot import file data properties
        :param qfile: Plot import file absolute path
        :type qfile: QFile
        :return results: Plot import file data properties
        :return results: List
        """
        results = []
        properties = {}
        for n, prop in enumerate(self._data_service.columns):
            if prop.name == "Name":
                properties[n] = unicode(QFileInfo(qfile).fileName())
            elif prop.name == "Header row":
                properties[n] = float(1)
            else:
                properties[n] = unicode("Test")
        results.append(properties)
        return results

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns


