"""
/***************************************************************************
Name                 : xls_2_qgs_vector_layer
Description          : Module for reading an Excel file and converting it
                       to an QgsVectorLayer object
Date                 : 17/August/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from datetime import datetime
from PyQt4.QtCore import (
    QFileInfo,
    QVariant
)
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsVectorLayer
)

# Flag for checking whether import of xlrd library succeeded
XLRD_AVAIL = True
try:
    from xlrd import (
        open_workbook,
        XL_CELL_EMPTY,
        XL_CELL_TEXT,
        XL_CELL_NUMBER,
        XL_CELL_DATE,
        XL_CELL_BOOLEAN,
        xldate_as_tuple,
        XLDateError
    )
except ImportError as ie:
    XLRD_AVAIL = False

#  XLRD to QGIS field type mapping
xl_2_qgs_field_mapping = {
    XL_CELL_EMPTY: QVariant.String,
    XL_CELL_TEXT: QVariant.String,
    XL_CELL_NUMBER: QVariant.Double,
    XL_CELL_DATE: QVariant.Date,
    XL_CELL_BOOLEAN: QVariant.String
}

DEFAULT_SHEET_NAME = 'Holders Table'
DATE_FORMAT = '%Y-%m-%d'


class XLSException(Exception):
    """
    Container for generic exceptions raised during the conversion of Excel
    data.
    """
    pass


def _append_idx_suffix(items, name):
    # Checks if name exists in items and append an auto-increment number
    if not name in items:
        return name

    if not name:
        return name

    name_parts = name.split('_')
    if len(name_parts) == 1:
        return '{0}_1'.format(name)

    # Get last item and check whether its a digit
    count = len(name_parts)
    last_item = name_parts[count - 1]
    if last_item.isdigit():
        new_idx = int(last_item) + 1
        return '{0}_{1}'.format(name, new_idx)
    else:
        return '{0}1'.format(name)


def _create_qgs_fields(xl_sheet, headers_first_line):
    # Create list of QgsField items based on type of columns in the sheet.
    fields = []
    used_col_names = []
    xl_qgs_col_idx_mapping = {} # cell_index: qgs_feature_index
    qgs_col_idx = 0
    base_col_name = 'col'
    ncols = xl_sheet.ncols

    # Set row index for determining the field type
    type_row_idx = 0
    if headers_first_line:
        type_row_idx = 1

    for i in range(ncols):
        if headers_first_line:
            cell = xl_sheet.cell(0, i)
            val = cell.value
            if cell.ctype == XL_CELL_NUMBER or cell.ctype == XL_CELL_TEXT:
                col_name = str(val)

            else:
                # If not number or text then exclude the column
                continue

            # Format column name
            # Remove spaces and new lines
            col_name = col_name.replace(
                ' ', '_'
            ).replace(
                '\n', '_'
            ).replace(
                '_-_', '_'
            ).strip('_')

        else:
            col_name = '{0)_{1}'.format(base_col_name, str(i+1))

        cell = xl_sheet.cell(type_row_idx, i)

        # If column name already exists then append '_n' suffix
        col_name = _append_idx_suffix(used_col_names, col_name)

        # If cell has an error then exclude the column
        if cell.ctype in xl_2_qgs_field_mapping:
            f_type = xl_2_qgs_field_mapping[cell.ctype]
            field = QgsField(
                col_name,
                f_type
            )

            # Set column index mapping
            xl_qgs_col_idx_mapping[i] = qgs_col_idx
            qgs_col_idx += 1

            # Add column name so that there are no duplicates
            used_col_names.append(col_name)

            # Append field to the collection
            fields.append(field)
        else:
            continue

    return xl_qgs_col_idx_mapping, fields


def _cells_2_features(
        xl_sheet,
        headers_first_line,
        col_idx_mapping,
        vl_fields
):
    # Create a list of QgsFeature from xl_sheet cells
    features = []
    nrows = xl_sheet.nrows
    ncols = xl_sheet.ncols

    for r in range(nrows):
        # If headers_first_line is True then skip the first line
        if headers_first_line and r == 0:
            continue

        feat = QgsFeature(vl_fields)
        for c in range(ncols):
            # Check if the column index had been mapped to a QgsField
            if c in col_idx_mapping:
                qgs_idx = col_idx_mapping[c]
                cell = xl_sheet.cell(r, c)
                cell_val = cell.value
                if cell.ctype == XL_CELL_BOOLEAN:
                    cell_val = 'True' if cell_val == 1 else 'False'
                elif cell.ctype == XL_CELL_DATE:
                    try:
                        dt = xldate_as_tuple(cell_val, xl_sheet.book.datemode)
                        cell_val = datetime(*dt)
                    except XLDateError as de:
                        raise de

                feat.setAttribute(qgs_idx, cell_val)

        features.append(feat)

    return features


def xls_2_qgs_vector_layer(xls_path, headers_first_line=True):
    """
    Reads the Excel file from the given file path and converts it to a
    geometry-less QGIS vector layer.
    The column type (in the QGIS vector layer) will be determined
    automatically based on the type of the type of the column in the first
    row that will be parsed in the Excel file.
    If the workbook contains multiple sheets, then only the first sheet will
    be loaded.
    :param xls_path: File path to Excel file.
    :type xls_path: str
    :param headers_first_line: True if the first line contains the header
    names else the headers will be automatically generated.
    :return: Returns a QGIS memory layer containing the Excel data.
    :rtype: QgsVectorLayer
    """
    if not XLRD_AVAIL:
        msg = '\'xlrd library\' for parsing Excel files is missing.'
        raise XLSException(msg)

    # Check permissions
    xfileinfo = QFileInfo(xls_path)
    if not xfileinfo.isReadable():
        msg = 'The current user does not have read permissions ' \
              'on \'{0}\''.format(xls_path)
        raise XLSException(msg)

    book = open_workbook(xls_path)
    if not book:
        raise XLSException('The workbook could not be loaded.')

    # Get first sheet
    xl_sheet = book.sheet_by_index(0)

    sheet_name = xl_sheet.name
    if not sheet_name:
        sheet_name = DEFAULT_SHEET_NAME

    xls_vl = QgsVectorLayer('None', sheet_name, 'memory')
    dp = xls_vl.dataProvider()

    # Get QgsField items
    col_idx_mapping, fields = _create_qgs_fields(xl_sheet, headers_first_line)

    # Add fields
    dp.addAttributes(fields)
    xls_vl.updateFields()

    fields = xls_vl.pendingFields()

    # Create qgis features items, add them to data provider
    features = _cells_2_features(
        xl_sheet,
        headers_first_line,
        col_idx_mapping,
        fields
    )
    dp.addFeatures(features)

    return xls_vl