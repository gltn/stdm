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
    QMessageBox,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from PyQt4.QtCore import (
    QFile,
    QFileInfo,
    QSize,
    Qt
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


class ExcelSheetView(QTableWidget):
    """A widget for displaying Excel sheet data."""
    def __init__(self, **kwargs):
        super(QTableWidget, self).__init__(**kwargs)
        self._nrows = 20
        self._ncols = 20
        self._ws = None

        # Default ISO format for the date
        self._date_format = '%Y-%m-%d'

        # Init default view
        self._init_ui()

    @property
    def sheet(self):
        """
        :return: Returns object containing worksheet data.
        :rtype: xlrd.sheet.Sheet
        """
        return self._ws

    def _init_ui(self):
        # Set default options
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._update_view()

    def _update_view(self):
        # Set number of rows and columns, as well as horizontal labels.
        self.setRowCount(self._nrows)
        self.setColumnCount(self._ncols)
        hlabels = uppercase_labels(self._ncols)
        self.setHorizontalHeaderLabels(hlabels)

    def load_worksheet(self, xsheet):
        """
        Loads worksheet data into the table.
        :param xsheet: Object containing worksheet data.
        :type xsheet: xlrd.sheet.Sheet
        """
        if not xsheet:
            QMessageBox.critical(
                self.parentWidget(),
                self.tr('Null Sheet'),
                self.tr('Sheet object is None, cannot be loaded.')
            )
            return

        self._ws = xsheet
        self._ncols = self._ws.ncols
        self._nrows = self._ws.nrows

        # Update view
        self._update_view()

        # Add cell values
        tbi = None
        for r in range(self._nrows):
            for c in range(self._ncols):
                tbi = QTableWidgetItem()
                cell = self._ws.cell(r, c)
                val = cell.value
                # Number
                if cell.ctype == 2:
                    val = str(float(val))

                # Date/time
                elif cell.ctype == 3:
                    try:
                        dt = xldate_as_tuple(val, self._ws.book.datemode)
                        val_dt = datetime(*dt)
                        # Apply formatting for the date/time
                        val = val_dt.strftime(self._date_format)
                    except XLDateError as de:
                        self.format_error_cell(tbi)
                        val = u'DATE ERROR!'

                # Boolean
                elif cell.ctype == 4:
                    val = 'True' if val == 1 else 'False'

                # Error with Excel codes
                elif cell.ctype == 5:
                    self.format_error_cell(tbi)
                    val = u'ERROR - {0}'.format(str(val))

                tbi.setText(val)
                self.setItem(r, c, tbi)

    def format_error_cell(self, tbi):
        """
        Formats error cell by changing text color to red.
        :param tbi: Table widget item to format.
        :type tbi: QTableWidgetItem
        """
        tbi.setTextColor(Qt.red)

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


class ExcelWorkbookView(QWidget):
    """A read-only table view for browsing MS Excel data."""
    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        self._init_ui()

        # Optional args
        self._dt_format = kwargs.pop('date_format', '%Y-%m-%d')

        # Map for sheet widgets
        self._ws_info = {}

        # Reset the view
        self.reset_view()

        # Check availability of XLRD library
        if not XLRD_AVAIL:
            QMessageBox.critical(
                self,
                self.tr('Missing Dependency'),
                self.tr(
                    '\'xlrd\' library is missing.\nExcel data cannot be loaded '
                    'without this library. Please install it and try again.'
                )
            )
            self.setEnabled(False)

            return

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
        def_sheet = ExcelSheetView()
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

    def add_xlrd_sheet(self, xsheet):
        """
        Adds data contained in a sheet object to the view.
        :param xsheet: Object containing worksheet data.
        :type xsheet: xlrd.sheet.Sheet
        """
        worksheet = ExcelSheetView()
        worksheet.date_format = self._dt_format
        name = xsheet.name
        idx = self._tbw.addTab(worksheet, name)
        self._tbw.setTabToolTip(idx, name)

        worksheet.load_worksheet(xsheet)

        # Add worksheet info to collection
        wsi = WorksheetInfo()
        wsi.name = name
        wsi.idx = idx
        wsi.ws_widget = worksheet
        wsi.ws = xsheet

        self._ws_info[wsi.idx] = wsi

    def load_workbook(self, path):
        """
        Loads the workbook contained in the specified file to the view.
        :param path: Path to fil containing workbook data.
        :type path: str
        """
        xfile = QFile(path)
        if not xfile.exists():
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
        xfileinfo = QFileInfo(xfile)
        if not xfileinfo.isReadable():
            QMessageBox.critical(
                self,
                self.tr('Unreadable file'),
                u'{0} {1}'.format(
                    path,
                    self.tr('is not readable.')
                )
            )

            return

        # Clear view
        self.clear_view()

        # Show progress bar
        self._pg_par.setVisible(True)
        pg_val = 0

        # Add sheets
        wb = open_workbook(path)
        self._pg_par.setRange(0, wb.nsheets)
        for s in wb.sheets():
            self.add_xlrd_sheet(s)

            # Update progress bar
            pg_val += 1
            self._pg_par.setValue(pg_val)

        self._pg_par.setVisible(False)
