"""
/***************************************************************************
Name                 : Work Manager Configuration
Description          : Configuration manager
Date                 : 21/August/2019
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
from collections import namedtuple
from PyQt4.QtCore import Qt

Column = namedtuple("Column", ["name", "flag"])  # TODO: Add types to handle date and time in datetime type
LookUp = namedtuple("LookUp", ["APPROVED", "PENDING", "UNAPPROVED", "CHECK", "STATUS", "SCHEME_NUMBER"])
UpdateColumn = namedtuple("UpdateColumn", ['column', 'index', 'new_value'])

conf = {
    'document_columns': [
        {Column(name='Number of Scheme', flag=False): 'name'},
        {Column(name='Document Type', flag=False): {'cb_check_scheme_document_type': 'value'}},
        {Column(name='Document Size', flag=False): 'document_size'},
        {Column(name='Last Modified', flag=False): 'last_modified'},
        {Column(name='Created By', flag=False): 'created_by'},
        {Column(name='View Document', flag=False): 'View'}
    ],
    'header_view_style': 'QHeaderView::section{'
                         'border-top:0px solid #C4C2BF;'
                         'border-left:0px solid #C4C2BF;'
                         'border-right: 1px solid #C4C2BF;'
                         'border-bottom: 1px solid #A9A5A2;'
                         'padding:4px;'
                         'background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}'
                         'QTableCornerButton::section{'
                         'border-top:0px solid #C4C2BF;'
                         'border-left:0px solid #C4C2BF;'
                         'border-right: 1px solid #C4C2BF;'
                         'border-bottom: 1px solid #A9A5A2;'
                         'background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}',
    'lookups': LookUp(APPROVED=1, PENDING=2, UNAPPROVED=3, CHECK=0, STATUS=2, SCHEME_NUMBER=1),
    'scheme_columns': [
        {Column(name='', flag=Qt.ItemIsUserCheckable): '0'},
        {Column(name='Number of Scheme', flag=False): 'scheme_number'},
        {Column(name='Status', flag=False): {'cb_approval': 'status'}},
        {Column(name='Date of Approval', flag=False): 'date_of_approval'},
        {Column(name='Time', flag=False): {'cb_approval': 'timestamp'}},
        {Column(name='Date of Establishment', flag=False): 'date_of_establishment'},
        {Column(name='Type of Relevant Authority', flag=False): {'cb_check_lht_relevant_authority': 'value'}},
        {Column(name='Land Rights Office', flag=False): {'cb_check_lht_land_rights_office': 'value'}},
        {Column(name='Region', flag=False): {'cb_check_lht_region': 'value'}},
        {Column(name='Township', flag=False): 'township_name'}, 
        {Column(name='Registration Division', flag=False): 'registration_division'},
        {Column(name='Block Area', flag=False): 'area'}
    ],
    'update_columns': {
        'scheme_update': [
            UpdateColumn(column={'cb_approval': 'status'}, index=2, new_value=1)
        ]
    }
}


class Config(object):
    """
    Workflow Manager configuration interface
    """
    def __init__(self):
        self._config = conf

    def get_data(self, option):
        """
        Get configuration data for the given setting
        :param option: Configuration property name
        :return: Configuration data
        :rtype: Multiple types
        """
        return self._config.get(option, None)


class DocumentConfig(Config):
    """
    Scheme supporting documents table
    view configuration interface
    """
    @property
    def columns(self):
        """
        Scheme supporting documents
        table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('document_columns')


class StyleSheet(Config):
    """
    Widget style sheet interface
    """
    @property
    def header_style(self):
        """
        Get header style sheet
        :return: Header style sheet
        :rtype: String
        """
        return self.get_data('header_view_style')


class SchemeConfig(Config):
    """
    Scheme table view configuration interface
    """
    @property
    def columns(self):
        """
        Scheme table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('scheme_columns')

    @property
    def lookups(self):
        """
        Scheme table view lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')

    @property
    def scheme_update_columns(self):
        """
        Scheme table view update column options
        :return: Update column values
        :rtype: List
        """
        return self.get_data('update_columns').\
            get('scheme_update', None)



