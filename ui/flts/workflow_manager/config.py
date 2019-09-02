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

Column = namedtuple("Column", ["name", "flag"])
ColumnIndex = namedtuple("ColumnIndex", ["CHECK", "STATUS"])
Status = namedtuple("Status", ["APPROVED", "PENDING", "UNAPPROVED"])

conf = {
    'scheme_options': [
        {Column(name='', flag=Qt.ItemIsUserCheckable): '0'},
        {Column(name='Number of Scheme', flag=False): 'scheme_number'},
        {Column(name='Approved', flag=False): {'status': 'status'}},
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
    'document_options': [
        {Column(name='Number of Scheme', flag=False): 'name'},
        {Column(name='Document Type', flag=False): {'cb_check_scheme_document_type': 'value'}},
        {Column(name='Document Size', flag=False): 'document_size'},
        {Column(name='Last Modified', flag=False): 'last_modified'},
        {Column(name='Created By', flag=False): 'created_by'},
        {Column(name='View Document', flag=False): 'View'}
    ],
    'column_position': ColumnIndex(CHECK=0, STATUS=2),
    'approval_status': Status(APPROVED=1, PENDING=2, UNAPPROVED=3),
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
                         '}'
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


class SchemeConfig(Config):
    """
    Scheme table view configuration interface
    """
    @property
    def field_option(self):
        """
        Scheme table view field option
        :return: Column and query field options
        :rtype: List
        """
        return self.get_data('scheme_options')


class DocumentConfig(Config):
    """
    Scheme supporting documents table
    view configuration interface
    """
    @property
    def field_option(self):
        """
        Scheme supporting documents
        table view field option
        :return: Column and query field options
        :rtype: List
        """
        return self.get_data('document_options')


class ColumnPosition(Config):
    """
    Column position interface
    """
    @property
    def position(self):
        """
        Return column position
        :return: Column position
        :rtype: ColumnIndex
        """
        return self.get_data('column_position')


class ApprovalStatus(Config):
    """
    Approval status interface
    """
    @property
    def status(self):
        """
        Return approval status
        :return: Approval status
        :rtype: Status
        """
        return self.get_data('approval_status')


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
