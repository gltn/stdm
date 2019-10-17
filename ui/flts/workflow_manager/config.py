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

from datetime import datetime
from collections import namedtuple
from PyQt4.QtCore import (QSize, Qt,)
from PyQt4.QtGui import (
    QApplication,
    QIcon,
    QMessageBox,
    QPushButton,
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


class ButtonIcons(Config):
    """
    QPushButton icons configuration interface
    """
    def __init__(self):
        super(ButtonIcons, self).__init__()
        self.Icon = namedtuple('Icon', ['icon', 'size'])

    def button_icons(self, config):
        """
        QPushButton icon configuration options
        :param config: QPushButton icon configurations
        :type config: Tuple
        :return: QPushButton icon options
        :rtype: Dictionary
        """

        return {
            button: self.Icon(icon=icon, size=qsize)
            for button, qsize, icon in config
        }


class CommentButtonIcons(ButtonIcons):
    """
    Comment Manager QPushButton icons configuration interface
    """

    def __init__(self, parent=None):
        super(CommentButtonIcons, self).__init__()
        self._parent = parent

    @property
    def buttons(self):
        """
        Comment Manager QPushButton icons options
        :return: Comment Manager QPushButton icon options
        :rtype: Dictionary
        """
        config = self._buttons_config()
        return super(CommentButtonIcons, self).button_icons(config)

    def _buttons_config(self):
        """
        Returns Comment Manager QPushButton icon configurations
        :return: QPushButton icon configurations
        :rtype: Tuple
        """
        return (
            (
                self._parent.submitButton, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_comment_reply.png")
            ),
        )


class CommentConfig(Config):
    """
    Comment Manager widget configuration interface
    """
    @property
    def columns(self):
        """
        Comment Manager widget columns options
        :return: Comment Manager widget columns and query columns options
        :rtype: List
        """
        return self.get_data('comment_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('comment_collections')

    @property
    def load_collections(self):
        """
        Related entity collection names to be used as
        primary load data for the Comment Manager widget
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('comment_load_collections')

    @property
    def lookups(self):
        """
        Comment text edit lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')

    @property
    def comment_save_columns(self):
        """
        Comment text edit save column options
        :return: Save column values
        :rtype: List
        """
        return self.get_data('save_columns').\
            get('comment_save', None)


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

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('document_collections')

    @property
    def lookups(self):
        """
        Scheme supporting documents lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')


class HolderConfig(Config):
    """
    Scheme holders table view configuration interface
    """
    @property
    def columns(self):
        """
        Scheme holders table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('holder_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('holder_collections')

    @property
    def load_collections(self):
        """
        Related entity collection names to be used as
        primary table view load
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('holder_load_collections')


class PaginationButtonIcons(ButtonIcons):
    """
    Pagination QPushButton icons configuration interface
    """

    def __init__(self, parent=None):
        super(PaginationButtonIcons, self).__init__()
        self._parent = parent

    @property
    def buttons(self):
        """
        Pagination QPushButton icons options
        :return: Pagination QPushButton icon options
        :rtype: Dictionary
        """
        config = self._buttons_config()
        return super(PaginationButtonIcons, self).button_icons(config)

    def _buttons_config(self):
        """
        Returns Pagination QPushButton icon configurations
        :return: QPushButton icon configurations
        :rtype: Tuple
        """
        return (
            (
                self._parent.first_button, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_first_record.png")
            ),
            (
                self._parent.previous_button, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_previous_record.png")
            ),
            (
                self._parent.next_button, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_next_record.png")
            ),
            (
                self._parent.last_button, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_last_record.png")
            ),
        )


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


class SchemeButtonIcons(ButtonIcons):
    """
    Scheme QPushButton icons configuration interface
    """
    def __init__(self, parent=None):
        super(SchemeButtonIcons, self).__init__()
        self._parent = parent

    @property
    def buttons(self):
        """
        Scheme QPushButton icons options
        :return: Scheme QPushButton icon options
        :rtype: Dictionary
        """
        config = self._create_config()
        return super(SchemeButtonIcons, self).button_icons(config)

    def _create_config(self):
        configs = self.get_data('scheme_button_icons')
        return [
            (getattr(self._parent, button), size, icon)
            for button, size, icon in configs
            if hasattr(self._parent, button)
        ]


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
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('scheme_collections')

    @property
    def lookups(self):
        """
        Scheme table view lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')

    @property
    def scheme_save_columns(self):
        """
        Scheme table view save column options
        :return: Save column values
        :rtype: List
        """
        return self.get_data('save_columns').\
            get('scheme_save', None)

    @property
    def scheme_update_columns(self):
        """
        Scheme table view update column options
        :return: Update column values
        :rtype: List
        """
        return self.get_data('update_columns').\
            get('scheme_update', None)


class SchemeMessageBox(Config):
    """
    Scheme QMessageBox configuration interface
    """

    @property
    def message_box(self):
        """
        Returns QMessageBox icon configurations
        :return: QMessageBox configuration options
        :rtype: Dictionary
        """
        return self.get_data('message_box')


class TabIcons(Config):
    """
    QTabWidget icons configuration interface
    """
    def __init__(self):
        super(TabIcons, self).__init__()

    @property
    def icons(self):
        """
        QTabWidget icon options
        :return: QTabWidget icon options
        :rtype: Dictionary
        """
        return self.get_data('tab_icons')


class TableModelIcons(Config):
    """
    QAbstractTableModel icons configuration interface
    """
    def __init__(self):
        super(TableModelIcons, self).__init__()

    @property
    def icons(self):
        """
        QAbstractTableModel icon options
        :return: QAbstractTableModel icon options
        :rtype: Dictionary
        """
        return self.get_data('table_model_icons')


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
Icon = namedtuple('Icon', ['icon', 'size'])
LookUp = namedtuple(
    'LookUp',
    [
        'schemeLodgement', 'schemeEstablishment', 'firstExamination',
        'secondExamination', 'thirdExamination', 'APPROVAL_STATUS',
        'WORKFLOW', 'WORKFLOW_COLUMN', 'APPROVAL_COLUMN', 'APPROVED',
        'PENDING', 'DISAPPROVED', 'WITHDRAW', 'CHECK', 'STATUS',
        'SCHEME_COLUMN', 'SCHEME_NUMBER', 'COMMENT_COLUMN', 'VIEW_PDF'
    ]
)
MessageBox = namedtuple(
    'MessageBox', ['name', 'pushButton', 'role', 'icon']
)
SaveColumn = namedtuple('SaveColumn', ['column', 'value', 'entity'])
UpdateColumn = namedtuple('UpdateColumn', ['column', 'value'])

configurations = {
    'comment_columns': [
        {Column(name='Comment', flag=False): 'comment'},
        {
            Column(name='User', flag=False): {
                'cb_user': 'user_name'
            }
        },
        {
            Column(name='First Name', flag=False): {
                'cb_user': 'first_name'
            }
        },
        {
            Column(name='Last Name', flag=False): {
                'cb_user': 'last_name'
            }
        },
        {Column(name='Post Date', flag=False): 'timestamp'}
    ],
    'comment_collections': ['cb_scheme_collection'],
    'comment_load_collections': ['cb_comment_collection'],
    'document_columns': [
        {Column(name='Scheme Number', flag=False): 'name'},
        {Column(name='Document Type', flag=False): {
            'cb_check_scheme_document_type': 'value'
        }},
        {Column(name='Document Size', flag=False): 'document_size'},
        {Column(name='Last Modified', flag=False): 'last_modified'},
        {Column(name='Created By', flag=False): 'created_by'},
        {Column(name='View Document', flag=Qt.DecorationRole): 'View'}
    ],
    'document_collections': ['cb_scheme_supporting_document_collection'],
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
    'holder_columns': [
        {
            Column(name='Scheme Number', flag=False): {
                'scheme_number': 'scheme_number'
            }
        },
        {Column(name='First Name', flag=False): 'first_name'},
        {Column(name='Surname', flag=False): 'surname'},
        {
            Column(name='Gender', flag=False): {
                'cb_check_lht_gender': 'value'
            }
        },
        {Column(name='Holder Identifier', flag=False): 'holder_identifier'},
        {Column(name='Date of Birth', flag=False): 'date_of_birth'},
        {Column(name='Name of Juristic Person', flag=False): 'name_of_juristic_person'},
        {Column(name='Reg. No. of Juristic Person', flag=False): 'reg_no_of_juristic_person'},
        {
            Column(name='Marital Status', flag=False): {
                'cb_check_lht_marital_status': 'value'
            }
        },
        {Column(name='Spouse Surname', flag=False): 'spouse_surname'},
        {Column(name='Spouse First Name', flag=False): 'spouse_first_name'},
        {
            Column(name='Spouse Gender', flag=False): {
                'cb_check_lht_gender': 'value'
            }
        },
        {Column(name='Spouse Identifier', flag=False): 'spouse_identifier'},
        {Column(name='Spouse Date of Birth', flag=False): 'spouse_date_of_birth'},
        {
            Column(name='Disability Status', flag=False): {
                'cb_check_lht_disability': 'value'
            }
        },
        {
            Column(name='Income Level', flag=False): {
                'cb_check_lht_income_level': 'value'
            }
        },
        {
            Column(name='Occupation', flag=False): {
                'cb_check_lht_occupation': 'value'
            }
        },
        {Column(name='Other Dependants', flag=False): 'other_dependants'},
    ],
    'holder_collections': ['cb_scheme_collection'],
    'holder_load_collections': ['cb_holder_collection'],
    'lookups': LookUp(
        APPROVAL_STATUS='check_lht_approval_status',
        WORKFLOW='check_lht_workflow',
        schemeLodgement=EntityRecordId(
            'check_lht_workflow', {'value': 'Lodgement'}
        ),
        schemeEstablishment=EntityRecordId(
            'check_lht_workflow', {'value': 'Establishment'}
        ),
        firstExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'First Assessment'}
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
        WITHDRAW=EntityRecordId(
            'check_lht_approval_status', {'value': 'Withdraw'}
        ),
        WORKFLOW_COLUMN='workflow_id', APPROVAL_COLUMN='approval_id',
        SCHEME_COLUMN='scheme_id', SCHEME_NUMBER=1, CHECK=0, STATUS=2,
        COMMENT_COLUMN='comment', VIEW_PDF=5
    ),
    'scheme_columns': [
        {Column(name='', flag=Qt.ItemIsUserCheckable): '0'},
        {Column(name='Scheme Number', flag=False): 'scheme_number'},
        {
            Column(name='Status', flag=Qt.DecorationRole): {
                'approval_id': 'approval_id'
            }
        },

        # {
        #     Column(name='Scheme ID', flag=False): {
        #         'scheme_id': 'scheme_id'
        #     }
        # },
        # {
        #     Column(name='Workflow', flag=False): {
        #         'workflow_id': 'workflow_id'
        #     }
        # },
        # {
        #     Column(name='Workflow Type', flag=False): {
        #         'cb_check_lht_workflow': 'value'
        #     }
        # },
        {Column(name='Approval Date', flag=False): 'date_of_approval'},
        {Column(name='Establishment Date', flag=False): 'date_of_establishment'},
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
        # {
        #     Column(name='Date/Time', flag=False): {
        #         'timestamp': 'timestamp'
        #     }
        # },
    ],
    'scheme_collections': ['cb_scheme_workflow_collection'],
    'tab_icons': {
        'Holders': QIcon(":/plugins/stdm/images/icons/flts_scheme_holders.png"),
        'Documents': QIcon(":/plugins/stdm/images/icons/flts_scheme_documents.png"),
        'Comments': QIcon(":/plugins/stdm/images/icons/flts_scheme_comment.png"),
        'Withdraw': QIcon(":/plugins/stdm/images/icons/flts_scheme_withdraw.png"),
        'Scheme': QIcon(":/plugins/stdm/images/icons/flts_scheme.png")
    },
    'table_model_icons': {
        1: QIcon(":/plugins/stdm/images/icons/flts_approve.png"),
        2: QIcon(":/plugins/stdm/images/icons/flts_pending.png"),
        3: QIcon(":/plugins/stdm/images/icons/flts_disapprove.png"),
        4: QIcon(":/plugins/stdm/images/icons/flts_withdraw.png"),
        'View': QIcon(":/plugins/stdm/images/icons/flts_document_view.png")
    },
    'scheme_button_icons': [
            (
                "approveButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_approve.png")
            ),
            (
                "disapproveButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_disapprove.png")
            ),
            (
                "withdrawButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_withdraw.png")
            ),
            (
                "holdersButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_holders.png")
            ),
            (
                "documentsButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_documents.png")
            ),
            (
                "commentsButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_scheme_comment.png")
            ),
            (
                "searchButton", QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_search.png")
            ),
    ],
    'message_box': {
        'approveButton': [
            MessageBox(
                name='approveMsgButton',
                pushButton=QPushButton("Approve"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_approve.png"),
            ),
            MessageBox(
                name='commentApproveMsgButton',
                pushButton=QPushButton("Comment && Approve"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_comment_reply_2.png"),
            ),
            MessageBox(
                name=None,
                pushButton=QPushButton("Cancel"),
                role=QMessageBox.RejectRole,
                icon=None,
            )
        ],
        'disapproveButton': [
            MessageBox(
                name='disapproveMsgButton',
                pushButton=QPushButton("Disapprove"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_disapprove.png"),
            ),
            MessageBox(
                name='commentDisapproveMsgButton',
                pushButton=QPushButton("Comment && Disapprove"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_comment_reply_2.png"),
            ),
            MessageBox(
                name=None,
                pushButton=QPushButton("Cancel"),
                role=QMessageBox.RejectRole,
                icon=None,
            )
        ],
        'withdrawButton': [
            MessageBox(
                name='withdrawMsgButton',
                pushButton=QPushButton("Withdraw"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_withdraw.png"),
            ),
            MessageBox(
                name='commentWithdrawMsgButton',
                pushButton=QPushButton("Comment && Withdraw"),
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_comment_reply_2.png"),
            ),
            MessageBox(
                name=None,
                pushButton=QPushButton("Cancel"),
                role=QMessageBox.RejectRole,
                icon=None,
            )
        ]
    },
    'update_columns': {
        'scheme_update': [
            UpdateColumn(column={'approval_id': 'approval_id'}, value=None)
            # UpdateColumn(column={'timestamp': 'timestamp'}, value=datetime.now())
        ]
    },
    'save_columns': {
        'scheme_save': [
            SaveColumn(
                column={'scheme_id': 'scheme_id'}, value=None, entity=None
            ),
            SaveColumn(
                column={'workflow_id': 'workflow_id'}, value=None, entity=None
            ),
            SaveColumn(
                column={'approval_id': 'approval_id'}, value=None, entity=None
            )
        ],
        'comment_save': [
            SaveColumn(
                column='comment', value=None, entity='Comment'
            ),
            SaveColumn(
                column='user_id', value=1, entity='Comment'
            ),
            SaveColumn(
                column='timestamp', value=datetime.now(), entity='Comment'
            )
        ]
    }
}
