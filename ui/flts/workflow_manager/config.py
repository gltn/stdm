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

conf = {
    'field_options': [
        {'Number of Scheme': 'scheme_number'},
        {'Name of Scheme': 'scheme_name'},
        {'Date of Approval': 'date_of_approval'},
        {'Date of Establishment': 'date_of_establishment'},
        {'Type of Relevant Authority': {'cb_check_lht_relevant_authority': 'value'}},
        {'Land Rights Office': {'cb_check_lht_land_rights_office': 'value'}},
        {'Region': {'cb_check_lht_region': 'value'}},
        {'Township': 'township_name'},
        {'Registration Division': 'registration_division'},
        {'Block Area': 'area'}
    ],
    'header_view_style': 'QHeaderView::section{'
                        'border-top:0px solid #D8D8D8;'
                        'border-left:0px solid #D8D8D8;'
                        'border-right: 1px solid #D8D8D8;'
                        'border-bottom: 1px solid #D8D8D8;'
                        'padding:4px;'
                        '}'
                        'QTableCornerButton::section{'
                        'border-top:0px solid #D8D8D8;'
                        'border-left:0px solid #D8D8D8;'
                        'border-right:1px solid #D8D8D8;'
                        'border-bottom: 1px solid #D8D8D8;'
                        'background-color:white;'
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
    Scheme configuration interface
    """
    @property
    def field_option(self):
        """
        Scheme field option
        :return: Column and query field options
        :rtype: List
        """
        return self.get_data('field_options')


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
