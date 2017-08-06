# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : STR Data Handler
Description          : A data handler for Social tenure editor.
Date                 : 10/November/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
import logging
from collections import OrderedDict

from PyQt4.QtCore import QDate
from PyQt4.QtGui import (
    QApplication,
    QMessageBox
)

from qgis.utils import (
    iface
)

from sqlalchemy import exc, inspect
from stdm.data.database import (
    STDMDb,
    Base
)

from stdm.ui.progress_dialog import STDMProgressDialog

from stdm.settings import current_profile

from stdm.data.configuration import entity_model

LOGGER = logging.getLogger('stdm')

class STRDataStore():
    """
    A data container for STR Editor.
    """
    def __init__(self):
        """
        Initializes the container dictionaries and lists.
        """
        self.party = OrderedDict()
        self.spatial_unit = OrderedDict()
        self.str_type = OrderedDict()
        # key, value - party_id, custom_attr model
        self.custom_tenure = OrderedDict()
        self.share = OrderedDict()
        self.validity_period = OrderedDict()
        self.validity_period['from_date'] = None
        self.validity_period['to_date'] = None
        self.supporting_document = []
        self.source_doc_manager = None
        self.current_spatial_unit = None
        self.current_party = None

class STRDBHandler():
    """
    Handles the saving of data in the STR table.
    """
    def __init__(
            self, data_store, str_model, str_edit_node=None
    ):
        """
        Initializes the saving of STRDBHandler.
        :param data_store: The data store containing STR record.
        :type data_store: Object
        :param str_model: The model of STR
        :type str_model: SQLAlchemy Model
        :param str_edit_node: The STR Edit node data containing STR model and
        supporting document models when in edit mode.
        :type str_edit_node: Tuple or STRNode
        """
        self.str_model = str_model
        self.data_store = data_store
        self.str_edit_obj = None
        self.progress = STDMProgressDialog(iface.mainWindow())
        self.social_tenure = current_profile().social_tenure



        self.str_edit_node = str_edit_node
        if str_edit_node is not None:
            if isinstance(str_edit_node, tuple):
                self.str_edit_obj = str_edit_node[0]
                self.str_doc_edit_obj = str_edit_node[1]
            else:
                self.str_edit_obj = str_edit_node.model()
                self.str_doc_edit_obj = str_edit_node.documents()

    def on_add_str(self, str_store):
        """
        Adds new STR record into the database
        with a supporting document record, if uploaded.
        :param str_store: The data store of str components
        :type str_store: STRDataStore
        """
        _str_obj = self.str_model()

        str_objs = []

        party = str_store.current_party
        spatial_unit = str_store.current_spatial_unit
        custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
            spatial_unit
        )

        # _custom_atr_obj = getattr(self.str_model, custom_attr_entity.name, None)
        # # custom_atr_objs = []
        index = 4
        # Social tenure and supporting document insertion
        # The code below is have a workaround to enable
        # batch supporting documents without affecting single
        # party upload. The reason a hack was needed is,
        # whenever a document is inserted in a normal way,
        # duplicate entry is added to the database.
        no_of_party = len(str_store.party)
        # custom_attr_objs = []
        for j, (party_id, str_type_id) in \
                enumerate(str_store.str_type.iteritems()):
            # get all doc model objects
            doc_objs = str_store.supporting_document
            # get the number of unique documents.
            number_of_docs = len(doc_objs) / no_of_party
            party_short_name = party.short_name
            party_entity_id = '{}_id'.format(
                party_short_name.replace(' ', '_').lower()
            )
            spatial_unit_short_name = spatial_unit.short_name
            spatial_unit_entity_id = '{}_id'.format(
                spatial_unit_short_name.replace(' ', '_').lower()
            )

            tenure_type_col = self.social_tenure.spatial_unit_tenure_column(
                spatial_unit_short_name
            )

            start_date = str_store.validity_period['from_date']
            end_date = str_store.validity_period['to_date']

            if isinstance(start_date, QDate):
                start_date = start_date.toPyDate()
            if isinstance(end_date, QDate):
                end_date = end_date.toPyDate()
            tenure_type = tenure_type_col.name

            str_args = {
                party_entity_id: party_id,
                spatial_unit_entity_id: str_store.spatial_unit.keys()[0],
                tenure_type: str_type_id,
                'validity_start': start_date,
                'validity_end': end_date,
                'tenure_share': str_store.share[party_id]
            }
            str_obj = self.str_model(**str_args)
            # Insert Supporting Document if a
            # supporting document is uploaded.
            if len(doc_objs) > 0:
                # loop through each document objects
                # loop per each number of documents
                for k in range(number_of_docs):
                    # The number of jumps (to avoid duplication) when
                    # looping though document objects in multiple party
                    loop_increment = (k * no_of_party) + j
                    # append into the str obj
                    str_obj.documents.append(
                        doc_objs[loop_increment]
                    )

            # custom_atr_model = str_store.custom_tenure[party_id]

            # str_objs.append(str_store.custom_tenure[party_id])
            str_objs.append(str_obj)
            # custom_atr_objs.append(custom_atr_model)
            # str_objs.append(custom_atr_objs)
            index = index + 1

        _str_obj.saveMany(str_objs)

        custom_attr_model = entity_model(custom_attr_entity)
        custom_attr_obj = custom_attr_model()

        custom_attr_objs = []

        for i, custom_attr_model in enumerate(str_store.custom_tenure.values()):

            # save custom tenure
            for col in custom_attr_entity.columns.values():
                if col.TYPE_INFO == 'FOREIGN_KEY':

                    if col.parent.name == self.social_tenure.name:
                        # print col.name, str_objs[i].id
                        setattr(custom_attr_model, col.name, str_objs[i].id)
                        custom_attr_objs.append(custom_attr_model)

                        break

        custom_attr_obj.saveMany(custom_attr_objs)


    def on_edit_str(self, str_store):
        """
         Updates an STR data with new data.
         :param str_store: The store of edited data
         with existing data.
         :type str_store: STRDataStore
         """
        _str_obj = self.str_model()

        str_edit_obj = _str_obj.queryObject().filter(
            self.str_model.id == self.str_edit_obj.id
        ).first()


        party = str_store.current_party
        spatial_unit = str_store.current_spatial_unit
        # custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
        #     spatial_unit
        # )
        party_short_name = party.short_name
        spatial_unit_short_name = spatial_unit.short_name
        tenure_type_col = self.social_tenure.spatial_unit_tenure_column(
            spatial_unit_short_name
        )

        start_date = str_store.validity_period['from_date']
        end_date = str_store.validity_period['to_date']
        if isinstance(start_date, QDate):
            start_date = start_date.toPyDate()
        if isinstance(end_date, QDate):
            end_date = end_date.toPyDate()

        party_entity_id = '{}_id'.format(party_short_name.lower())
        spatial_unit_entity_id = '{}_id'.format(spatial_unit_short_name.lower())
        tenure_type = tenure_type_col.name

        setattr(str_edit_obj, party_entity_id, str_store.party.keys()[0])
        setattr(str_edit_obj, spatial_unit_entity_id, str_store.spatial_unit.keys()[0])
        setattr(str_edit_obj, tenure_type, str_store.str_type.values()[0])

        str_edit_obj.validity_start = start_date
        str_edit_obj.validity_end = end_date
        str_edit_obj.tenure_share = str_store.share[str_store.party.keys()[0]]

        # get all doc model objects
        added_doc_objs = str_store.supporting_document

        self.str_doc_edit_obj = \
            [obj for obj in sum(self.str_doc_edit_obj.values(), [])]

        new_doc_objs = list(set(added_doc_objs) - set(self.str_doc_edit_obj))

        # Insert supporting document if a new
        # supporting document is uploaded.
        if len(new_doc_objs) > 0:

            # looping though newly added objects list
            for doc_obj in new_doc_objs:
                # append into the str edit obj
                str_edit_obj.documents.append(doc_obj)

        updated_str_edit_obj = str_edit_obj
        str_edit_obj.update()

        str_store.custom_tenure.values()[0].update()

        # custom_attr_model = entity_model(self.custom_attr_entity)
        # custom_attr_obj = custom_attr_model()
        #
        # custom_attr_objs = []
        #
        # # save custom tenure
        # for col in self.custom_attr_entity.columns.values():
        #     if col.TYPE_INFO == 'FOREIGN_KEY':
        #         if col.parent.name == self.social_tenure.name:
        #
        #             setattr(custom_attr_model, col.name, str_objs[i].id)
        #             custom_attr_objs.append(custom_attr_model)
        #             break
        #
        # custom_attr_obj = self.custom_attr_entity.values()[0]

        return updated_str_edit_obj

    def commit_str(self):
        """
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        """
        isValid = True
        # Create a progress dialog
        #try:

        self.progress.show()
        if self.str_edit_obj is None:
            QApplication.processEvents()
            self.progress.setRange(0, len(self.data_store))
            self.progress.overall_progress(
                'Creating a STR...',
            )

            for i, str_store in enumerate(self.data_store.values()):
                self.progress.progress_message(
                    'Saving STR {}'.format(i+1), ''
                )
                self.progress.setValue(i + 1)

                self.on_add_str(str_store)

            self.progress.hide()
            strMsg = QApplication.translate(
                "STRDBHandler",
                "The social tenure relationship has "
                "been successfully created!"
            )
            QMessageBox.information(
                iface.mainWindow(), QApplication.translate(
                    "STRDBHandler", "Social Tenure Relationship"
                ),
                strMsg
            )
        else:
            QApplication.processEvents()
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            self.progress.overall_progress(
                'Editing a STR...',
            )

            self.progress.progress_message('Updating STR', '')
            updated_str_obj = self.on_edit_str(
                self.data_store[1]
            )

            self.progress.setValue(1)

            self.progress.hide()

            strMsg = QApplication.translate(
                "STRDBHandler",
                "The social tenure relationship has "
                "been successfully updated!"
            )
            QMessageBox.information(
                iface.mainWindow(), QApplication.translate(
                    "STRDBHandler", "Social Tenure Relationship"
                ),
                strMsg
            )
            return updated_str_obj

        # except exc.OperationalError as oe:
        #     errMsg = oe.message
        #     QMessageBox.critical(
        #         iface.mainWindow(),
        #         QApplication.translate(
        #             "STRDBHandler", "Unexpected Error"
        #         ),
        #         errMsg
        #     )
        #     self.progress.hide()
        #     isValid = False
        #     STDMDb.instance().session.rollback()
        #     LOGGER.debug(str(oe))
        #
        # except exc.IntegrityError as ie:
        #     errMsg = ie.message
        #     QMessageBox.critical(
        #         iface.mainWindow(),
        #         QApplication.translate(
        #             "STRDBHandler",
        #             "Duplicate Relationship Error"
        #         ),
        #         errMsg
        #     )
        #     self.progress.hide()
        #     isValid = False
        #     STDMDb.instance().session.rollback()
        #     LOGGER.debug(str(ie))
        # except exc.InternalError as ie:
        #
        #     QMessageBox.critical(
        #         iface.mainWindow(),
        #         QApplication.translate(
        #             'STRDBHandler',
        #             'InternalError Error'
        #         ),
        #         QApplication.translate(
        #             'STRDBHandler',
        #             'Sorry, there is an internal error. \n'
        #             'Restart QGIS to fix the issue.'
        #         )
        #     )
        #     LOGGER.debug(str(ie))
        #     self.progress.hide()
        #     isValid = False
        #     STDMDb.instance().session.rollback()
        # except Exception as e:
        #     errMsg = unicode(e)
        #     QMessageBox.critical(
        #         iface.mainWindow(),
        #         QApplication.translate(
        #             'STRDBHandler', 'Unexpected Error'
        #         ),
        #         errMsg
        #     )
        #     LOGGER.debug(str(e))
        #     isValid = False
        #     STDMDb.instance().session.rollback()
        #     self.progress.hide()
        # finally:
        #
        #     STDMDb.instance().session.rollback()
        #     self.progress.hide()

        return isValid