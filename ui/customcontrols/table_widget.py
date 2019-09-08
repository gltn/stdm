"""
/***************************************************************************
Name                 : ExcelTableWidget
Description          : A read-only table view for browsing MS Excel data.
Date                 : 07/July/2019
email                : gkahiu@gmail.com
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

import itertools
import string
from datetime import datetime

from PyQt4.QtGui import (
    QAbstractItemView,
    QIcon,
    QMessageBox,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from PyQt4.QtCore import (
    pyqtSignal,
    QFile,
    QFileInfo,
    QSize,
    Qt,
    QVariant
)

# Flag for checking whether import of xlrd library succeeded
XLRD_AVAIL = True
try:
    from xlrd import (
        open_workbook,
        xldate_as_tuple,
        XLDateError
    )
except ImportError as ie:
    XLRD_AVAIL = False

from stdm.data.flts import (
    holder_readers
)

from stdm.ui.customcontrols import TABLE_STYLE_SHEET


def _ascii_lbl_gen():
    """Generator function for producing Excel like columns i.e. A...Z,
    AA...AZ etc.
    """
    n = 1
    while True:
        for group in itertools.product(string.ascii_uppercase, repeat=n):
            yield ''.join(group)
        n += 1


def uppercase_labels(n):
    """
    Generates a sequential repeating pair of uppercase characters.
    :param n: Number of items to be generated.
    :type n: int
    :return: A list containing a sequential repeating pair of uppercase
    characters.
    :rtype: list
    """
    return list(itertools.islice(_ascii_lbl_gen(), n))


class HoldersSheetView(QTableWidget):
    """A widget for displaying sheet data from a QgsVectorLayer data source."""
    def __init__(self, **kwargs):
        super(QTableWidget, self).__init__(**kwargs)
        self._nrows = 20
        self._ncols = 20
        self._ws = None
        self._vl = None

        # Default ISO format for the date
        self._date_format = '%d-%m-%Y'

        # Init default view
        self._init_ui()

    def _init_ui(self):
        # Set default options
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        # Set stylesheet for horizontal header
        self.setStyleSheet(TABLE_STYLE_SHEET)
        self._update_view()

    def _update_view(self):
        # Set number of rows and columns, as well as horizontal labels.
        self.setRowCount(self._nrows)
        self.setColumnCount(self._ncols)
        if self._vl:
            h_labels = self._vl_columns()
        else:
            h_labels = uppercase_labels(self._ncols)
        self.setHorizontalHeaderLabels(h_labels)

    @property
    def vector_layer(self):
        """
        :return: Returns the data source associated with the sheet view.
        :rtype: QgsVectorLayer
        """
        return self._vl

    def _vl_columns(self):
        # Returns a list containing the field names in the vector layer
        return [f.name() for f in self._vl.fields()]

    def load_qgs_vector_layer(self, vl):
        """
        Loads a QgsVectorLayer (created from Excel or CSV file) into the
        table.
        :param vl: Vector layer containing table information.
        :type vl: QgsVectorLayer
        """
        self._vl = vl
        dp = self._vl.dataProvider()
        self._nrows = dp.featureCount()
        self._ncols = len(dp.fieldNameMap())
        fields = self._vl.fields()

        # Update view
        self._update_view()

        # Add cell values
        tbi = None
        features = self._vl.getFeatures()
        ridx = 0

        for f in features:
            cidx = 0

            # Read attributes
            for fi in fields:
                tbi = QTableWidgetItem()
                attr = f.attribute(fi.name())
                # Correctly represent double values that are actually int
                if fi.type() == QVariant.Double:
                    if attr.is_integer():
                        attr = int(attr)

                # Format string representation
                # Date
                if fi.type() == QVariant.Date:
                    val = attr.strftime(self._date_format)
                else:
                    val = unicode(attr)

                tbi.setText(val)
                self.setItem(ridx, cidx, tbi)

                cidx += 1

            ridx += 1

    def format_error_cell(self, tbi):
        """
        Formats error cell by changing text color to red.
        :param tbi: Table widget item to format.
        :type tbi: QTableWidgetItem
        """
        tbi.setTextColor(Qt.red)

    def highlight_validation_cell(self, validation_result):
        """
        Highlights a cell to show warning or error messages from a
        validation process.
        :param ridx: Row position.
        :type ridx: int
        :param cidx: Column position
        :type cidx: int
        :param messages: Object containing validation messages
        :type messages: list
        """
        ridx = validation_result.ridx
        cidx = validation_result.cidx

        # Get table item
        tbi = self.item(ridx, cidx)
        if not tbi:
            return

        # Set error icon
        tbi.setIcon(
            QIcon(':/plugins/stdm/images/icons/warning.png')
        )

        # Save validation result object in the item user role
        tbi.setData(Qt.UserRole, validation_result)

    @property
    def date_format(self):
        """
        :return: Returns the format used to render the date/time in the
        table. The default formatting will return the date in ISO 8601 format
        i.e. 'YYYY-MM-DD' where the format is '%Y-%m-%d'.
        :rtype: str
        """
        return self._date_format

    @date_format.setter
    def date_format(self, format):
        """
        Sets the format used to render the date/time in the table. The format
        needs to be in a format that is understood by Python's 'strftime()'
        function.
        :param format: Format for rendering date/time
        :type format: str
        """
        self._date_format = format


class WorksheetInfo(object):
    """
    Container for info on Sheet object, container widget, index in tab widget
    and name of the worksheet.
    """
    def __init__(self):
        self.idx = -1
        self.ws_widget = None
        self.name = ''
        self.ws = None


class HoldersTableView(QWidget):
    """A read-only table view for browsing MS Excel or CSV data."""
    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        self._init_ui()

        # Optional args
        self._dt_format = kwargs.pop('date_format', '%d-%m-%Y')

        # Map for sheet widgets
        self._ws_info = {}

        # Reset the view
        self.reset_view()

    @property
    def date_format(self):
        """
        :return: Returns the format used to render the date/time in the
        view. The default formatting will return the date in ISO 8601 format
        i.e. 'YYYY-MM-DD' where the format is '%Y-%m-%d'.
        :rtype: str
        """
        return self._dt_format

    @date_format.setter
    def date_format(self, format):
        """
        Sets the format used to render the date/time in the view. The format
        needs to be in a format that is understood by Python's 'strftime()'
        function.
        :param format: Format for rendering date/time
        :type format: str
        """
        self._dt_format = format

    def worksheet_info(self, idx):
        """
        :param idx:
        :return: Returns a WorksheetInfo object containing references to the
        ExcelWorksheetView, xlrd.sheet.Sheet and name of the sheet, will
        return None if the index does not exist.
        :rtype: WorksheetInfo
        """
        return self._ws_info.get(idx, None)

    @property
    def progress_bar(self):
        """
        :return: Returns the progress bar for showing progress when Excel
        data is being added to the table.
        :rtype: QProgressBar
        """
        return self._pg_par

    def sizeHint(self):
        return QSize(480, 360)

    def clear_view(self):
        # Removes and deletes all sheet widgets and resets the widget registry index.
        self._tbw.clear()
        self._ws_info.clear()

    def reset_view(self):
        # Clears the view and add an empty default sheet.
        self.clear_view()
        self._add_default_sheet()

    def _add_default_sheet(self):
        # Add a default/empty sheet to the view.
        def_sheet = HoldersSheetView()
        self._tbw.addTab(def_sheet, self.tr('Sheet 1'))

    def _init_ui(self):
        # Set up layout and widgets
        self._vl = QVBoxLayout()
        self._tbw = QTabWidget()
        self._tbw.setTabShape(QTabWidget.Triangular)
        self._tbw.setTabPosition(QTabWidget.South)
        self._tbw.setStyleSheet('QTabBar::tab:selected { color: green; }')
        self._vl.addWidget(self._tbw)
        self._pg_par = QProgressBar()
        self._pg_par.setVisible(False)
        self._vl.addWidget(self._pg_par)
        self.setLayout(self._vl)

    def add_vector_layer(self, vl):
        """
        Adds data contained in Qgis vector layer object to the view.
        :param vl: Object containing holders data.
        :type vl: QgsVectorLayer
        """
        holders_sheet = HoldersSheetView()
        holders_sheet.date_format = self._dt_format
        name = vl.name()
        idx = self._tbw.addTab(holders_sheet, name)
        self._tbw.setTabToolTip(idx, name)

        holders_sheet.load_qgs_vector_layer(vl)

        # Add worksheet info to collection
        wsi = WorksheetInfo()
        wsi.name = name
        wsi.idx = idx
        wsi.ws_widget = holders_sheet
        wsi.ws = vl

        self._ws_info[wsi.idx] = wsi

    def current_sheet_view(self):
        """
        Gets the sheet view in the current tab view.
        :return: Sheet view widget.
        :rtype: HoldersSheetView
        """
        return self._tbw.currentWidget()

    def sheet_view(self, idx):
        """
        Gets the sheet view widget with the given index.
        :param idx: Index number.
        :type idx: int
        :return: Sheet view widget.
        :rtype: HoldersSheetView
        """
        return self.worksheet_info(idx).ws_widget

    def load_holders_file(self, path):
        """
        Loads the holders data contained in the specified file to the view.
        :param path: Path to file containing holders data.
        :type path: str
        """
        holders_file = QFile(path)
        if not holders_file.exists():
            QMessageBox.critical(
                self,
                self.tr('Invalid path'),
                u'\'{0}\' {1}'.format(
                    path,
                    self.tr('does not exist.')
                )
            )

            return

        # Check permissions
        holders_fileinfo = QFileInfo(holders_file)
        if not holders_fileinfo.isReadable():
            QMessageBox.critical(
                self,
                self.tr('Unreadable file'),
                u'{0} {1}'.format(
                    path,
                    self.tr('is not readable.')
                )
            )

            return

        # Get file extension
        ext = holders_fileinfo.suffix()

        # Get reader based on suffix
        if ext not in holder_readers:
            msg = 'No reader defined for \'{0}\' file extension'.format(ext)
            QMessageBox.critical(
                self,
                self.tr('Invalid Extension'),
                msg
            )

            return

        reader = holder_readers[ext]

        vl = None

        try:
            # Get vector layer
            vl = reader(path)
        except Exception as ex:
            QMessageBox.critical(
                self,
                self.tr('Error Loading Data Source.'),
                str(ex)
            )

            return

        if not vl:
            QMessageBox.critical(
                self.parentWidget(),
                self.tr('Null Data Source'),
                self.tr('Data source object is None, cannot be loaded.')
            )

            return

        if not vl.isValid():
            err = vl.error()
            if not err.isEmpty():
                err_msg = err.summary()
            else:
                err_msg = 'The holders data source is invalid.'

            QMessageBox.critical(
                self.parentWidget(),
                self.tr('Invalid Data Source'),
                err_msg
            )

            return

        # Clear view
        self.clear_view()

        # Show progress bar
        self._pg_par.setVisible(True)
        pg_val = 0

        # Add vector layer to the view
        self._pg_par.setRange(0, 1)
        self.add_vector_layer(vl)

        self._pg_par.setValue(1)

        self._pg_par.setVisible(False)
