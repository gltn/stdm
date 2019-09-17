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
# import datetime
from collections import namedtuple
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QApplication,
    QMessageBox,
)
from sqlalchemy import exc
from stdm.settings import current_profile
from stdm.data.configuration import entity_model

configurations = None


class Config(object):
    """
    Workflow Manager configuration interface
    """
    def __init__(self):
        self._configurations = configurations
        self._parent = None

    def get_data(self, option):
        """
        Get configuration data for the given setting
        :param option: Configuration property name
        :return: Configuration data
        :rtype: Multiple types
        """
        return self._configurations.get(option, None)


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
    def __init__(self, parent=None):
        super(SchemeConfig, self).__init__()
        self._parent = parent

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


class FilterQueryBy:
    """
    Filters query result by a column value
    """
    def __init__(self):
        self._profile = None

    def __call__(self, entity_name, filters):
        """
        Return query object on filter by a column value
        :param entity_name: Entity name
        :type entity_name: String
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            if not self._profile:
                self._profile = current_profile()
            query_obj = self._entity_query_object(entity_name)
            return self._filter_by(query_obj, filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    @staticmethod
    def _filter_by(query_obj, filters):
        """
        Return filter entity query object
        :param query_obj: Entity query object
        :type query_obj: List
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            return query_obj.filter_by(**filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_query_object(self, entity_name):
        """
        Return query object of an entity
        :param entity_name: Entity name
        :type entity_name: String
        :return:Entity query object
        :rtype List
        """
        model = self._entity_model(entity_name)
        entity_object = model()
        try:
            return entity_object.queryObject()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_model(self, name):
        """
        Gets entity model
        :param name: Name of the entity
        :type name: String
        :return model: Entity model;
        :rtype model: DeclarativeMeta
        """
        try:
            entity = self._profile.entity(name)
            model = entity_model(entity)
            return model
        except AttributeError as e:
            raise e


class EntityRecordId(Config):
    """
    Returns entity record ID
    """
    def __init__(self, entity_name, filters):
        super(EntityRecordId, self).__init__()
        self._entity_name = entity_name
        self._filters = filters
        self._results = None

    def __call__(self):
        """
        Return entity record ID filtered by a column value
        :return id: Entity record ID
        :rtype id: Integer
        """
        if not self._results:
            try:
                filter_by = FilterQueryBy()
                self._results = filter_by(
                    self._entity_name, self._filters
                ).first().id
            except (AttributeError, exc.SQLAlchemyError, Exception) as e:
                msg = QApplication.translate(
                    'Workflow Manager',
                    "Failed to get record id: {}".format(e)
                )
                QMessageBox.critical(
                    self._parent,
                    'Workflow Manager',
                    msg
                )
        return self._results


Column = namedtuple('Column', ['name', 'flag'])
LookUp = namedtuple(
    'LookUp',
    [
        'schemeLodgement', 'schemeEstablishment', 'firstExamination',
        'secondExamination', 'thirdExamination', 'WORKFLOW_COLUMN',
        'APPROVED', 'PENDING', 'DISAPPROVED', 'CHECK', 'STATUS',
        'SCHEME_COLUMN', 'SCHEME_NUMBER'
    ]
)
UpdateColumn = namedtuple('UpdateColumn', ['column'])

configurations = {
    'document_columns': [
        {Column(name='Number of Scheme', flag=False): 'name'},
        {Column(name='Document Type', flag=False): {
            'cb_check_scheme_document_type': 'value'
        }},
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
                         'background-color: qlineargradient'
                         '(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}'
                         'QTableCornerButton::section{'
                         'border-top:0px solid #C4C2BF;'
                         'border-left:0px solid #C4C2BF;'
                         'border-right: 1px solid #C4C2BF;'
                         'border-bottom: 1px solid #A9A5A2;'
                         'background-color: qlineargradient'
                         '(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}',
    'lookups': LookUp(
        # TODO: Working. Do not delete until tested
        # schemeEstablishment=EntityRecordId(
        #     'check_lht_workflow', {'value': 'Lodgement'}
        # ),
        # firstExamination=EntityRecordId(
        #     'check_lht_workflow', {'value': 'Establishment'}
        # ),
        # secondExamination=EntityRecordId(
        #     'check_lht_workflow', {'value': 'Fiirst Assessment'}
        # ),
        # thirdExamination=EntityRecordId(
        #     'check_lht_workflow', {'value': 'Second Assessment'}
        # ),
        schemeLodgement=EntityRecordId(
            'check_lht_workflow', {'value': 'Lodgement'}
        ),
        schemeEstablishment=EntityRecordId(
            'check_lht_workflow', {'value': 'Establishment'}
        ),
        firstExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'Fiirst Assessment'}
        ),
        secondExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'Second Assessment'}
        ),
        thirdExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'Third Assessment'}
        ),
        APPROVED=EntityRecordId(
            'check_lht_approval_status', {'value': 'Approved'}
        ),
        PENDING=EntityRecordId(
            'check_lht_approval_status', {'value': 'Pending'}
        ),
        DISAPPROVED=EntityRecordId(
            'check_lht_approval_status', {'value': 'Disapproved'}
        ),
        WORKFLOW_COLUMN='workflow_id', SCHEME_COLUMN='scheme_id',
        SCHEME_NUMBER=1, CHECK=0, STATUS=2
    ),
    'scheme_columns': [
        {Column(name='', flag=Qt.ItemIsUserCheckable): '0'},
        {Column(name='Number of Scheme', flag=False): 'scheme_number'},
        {
            Column(name='Status', flag=False): {
                'approval_id': 'approval_id'
            }
        },
        {
            Column(name='Scheme ID', flag=False): {
                'scheme_id': 'scheme_id'
            }
        },
        {
            Column(name='Workflow', flag=False): {
                'workflow_id': 'workflow_id'
            }
        },
        {
            Column(name='Workflow Type', flag=False): {
                'cb_check_lht_workflow': 'value'
            }
        },
        {
            Column(name='Date of Approval', flag=False): {
                'timestamp': 'timestamp'
            }
        },
        {
            Column(name='Type of Relevant Authority', flag=False): {
                'cb_check_lht_relevant_authority': 'value'
            }
        },
        {
            Column(name='Land Rights Office', flag=False): {
                'cb_check_lht_land_rights_office': 'value'
            }
        },
        {
            Column(name='Region', flag=False): {
                'cb_check_lht_region': 'value'
            }
        },
        {Column(name='Township', flag=False): 'township_name'}, 
        {
            Column(name='Registration Division', flag=False):
                'registration_division'
        },
        {Column(name='Block Area', flag=False): 'area'}
    ],
    'update_columns': {
        'scheme_update': [
            UpdateColumn(column={'approval_id': 'approval_id'}),
            UpdateColumn(column={'workflow_id': 'workflow_id'})
        ]
    }
}
