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

from qgis.PyQt.QtCore import QDate
from qgis.PyQt.QtWidgets import (
    QApplication,
    QMessageBox
)
from qgis.utils import (
    iface
)
from sqlalchemy import exc

from stdm.data.configuration import entity_model
from stdm.data.database import (
    STDMDb
)
from stdm.settings import current_profile
from stdm.ui.progress_dialog import STDMProgressDialog
from stdm.exceptions import DummyException

LOGGER = logging.getLogger('stdm')


class STRDataStore:
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


class STRDBHandler:
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
        self.progress = STDMProgressDialog(iface.mainWindow())
        self.social_tenure = current_profile().social_tenure
        self.str_edit_node = []

        if str_edit_node is not None:
            if isinstance(str_edit_node, tuple):
                self.str_edit_node.append((str_edit_node[0], str_edit_node[1]))
            elif isinstance(str_edit_node, list):
                self.str_edit_node = str_edit_node
            else:
                self.str_edit_node.append((str_edit_node.model(), str_edit_node.documents()))

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
                enumerate(str_store.str_type.items()):
            # get all doc model objects
            doc_objs = str_store.supporting_document
            # get the number of unique documents.
            number_of_docs = len(doc_objs) // no_of_party
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
                spatial_unit_entity_id: list(str_store.spatial_unit.keys())[0],
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

        if custom_attr_entity is None:
            return
        custom_attr_en_model = entity_model(custom_attr_entity)
        if custom_attr_en_model is None:
            return
        custom_attr_obj = custom_attr_en_model()

        custom_attr_objs = []

        for i, custom_attr_model in enumerate(str_store.custom_tenure.values()):

            # save custom tenure
            for col in custom_attr_entity.columns.values():
                if custom_attr_model is None:
                    custom_attr_model = custom_attr_obj
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    if col.parent.name == self.social_tenure.name:
                        setattr(custom_attr_model, col.name, str_objs[i].id)
                        custom_attr_objs.append(custom_attr_model)

                        break

        if len(custom_attr_objs) > 0:
            custom_attr_obj.saveMany(custom_attr_objs)

    def get_entity_id(self, str_store):
        """
        Gets party and spatial unit column names
        :param str_store: The store of edited data
        :type str_store: STRDataStore
        :return party_col: Party column name
        :rtype party_col: String
        :return spatial_col: Spatial unit column name
        :rtype spatial_col: String
        """
        party_col = '{}_id'.format(str_store.current_party.short_name.lower())
        spatial_col = '{}_id'.format(str_store.current_spatial_unit.short_name.lower())
        return party_col, spatial_col

    def to_pydate(self, q_date):
        """
        Converts QDate to normal python date
        :param q_date: PyQT QDate type
        :type q_date: QDate
        :return: Python date
        :rtype: datetime.date
        """
        return q_date.toPyDate() if isinstance(q_date, QDate) else q_date

    def pair_documents(self, str_type, doc_objs):
        """
        On multiple parties in an STR, pair supporting documents
        :param str_type: STR type
        :type str_type: OrderedDict
        :param doc_objs: STR supporting documents
        :type doc_objs: List
        :return paired_doc: Paired supporting documents
        :rtype paired_doc: List
        """
        paired_doc = []
        if len(str_type) > 1 and not len(doc_objs) % 2:
            count = 0
            while count <= len(doc_objs) - 1:
                paired_doc.append((doc_objs[count], doc_objs[count + 1]))
                count += 2
        return paired_doc

    def on_edit_str(self, str_store):
        """
         Updates an STR data with new data.
         :param str_store: The store of edited data
         with existing data.
         :type str_store: STRDataStore
         """
        party_col, spatial_col = self.get_entity_id(str_store)
        start_date = self.to_pydate(str_store.validity_period['from_date'])
        end_date = self.to_pydate(str_store.validity_period['to_date'])
        str_type = str_store.str_type
        doc_objs = str_store.supporting_document
        paired_doc = self.pair_documents(str_type, doc_objs)
        share = str_store.share
        party_keys = list(str_store.party.keys())
        spatial_keys = list(str_store.spatial_unit.keys())
        str_rec = {model.id: doc for model, doc in self.str_edit_node}
        rows = self.str_model().queryObject().filter(self.str_model.id.in_(list(str_rec.keys()))).all()
        for idx, row in enumerate(rows):
            attr = {c.name: getattr(row, c.name) for c in row.__table__.columns}
            new_party = party_keys[idx]
            party_id, spatial_id = attr[party_col], attr[spatial_col]
            setattr(row, party_col, party_id if party_id in party_keys else new_party)
            setattr(row, spatial_col, spatial_id if spatial_id in spatial_keys else spatial_keys[0])
            row.validity_start = start_date
            row.validity_end = end_date
            row.tenure_type = str_type[party_id] if party_id in list(str_type.keys()) else str_type[new_party]
            row.tenure_share = share[party_id] if party_id in list(share.keys()) else share[new_party]

            # Extract new supporting documents
            str_doc_objs = [obj for obj in sum(list(str_rec[row.id].values()), [])]
            new_doc_objs = list(set(doc_objs) - set(str_doc_objs))
            if paired_doc:
                new_doc_objs = [
                    d[idx] for d in paired_doc
                    if not all(i in str_doc_objs for i in d)
                ]

            # Add new supporting documents
            if len(new_doc_objs) > 0:
                row.documents.extend([doc for doc in new_doc_objs])

            # for r in row.in_check_tenure_type_str_attrs_collection:
            # Update custom tenure information
            if party_id in party_keys:
                attrs_column = str_store.current_party.name[:2] + '_check_tenure_type_str_attrs_collection'
                attrs = getattr(row, attrs_column)
                for r in attrs:
                    custom_tenure = str_store.custom_tenure
                    if custom_tenure:
                        if 'dispute_status' in custom_tenure:
                            r.dispute_status = custom_tenure[party_id].dispute_status
                        if 'dispute_type' in custom_tenure:
                            r.dispute_type = custom_tenure[party_id].dispute_type
                        if 'period_of_stay_in_years' in custom_tenure:
                            r.period_of_stay_in_years = custom_tenure[party_id].period_of_stay_in_years
            row.update()  # Commit updates to DB
        return rows

    def commit_str(self):
        """
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        """
        isValid = True
        # Create a progress dialog
        try:
            self.progress.show()

            if not self.str_edit_node:
                QApplication.processEvents()
                self.progress.setRange(0, len(self.data_store))
                self.progress.overall_progress('Creating a STR...', )

                for i, str_store in enumerate(self.data_store.values()):
                    self.progress.progress_message(
                        'Saving STR {}'.format(i + 1), '')
                    self.progress.setValue(i + 1)

                    self.on_add_str(str_store)  # ==>

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
                self.progress.overall_progress('Editing a STR...', )

                self.progress.progress_message('Updating STR', '')

                updated_str_obj = self.on_edit_str(self.data_store[1])  # ===>

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

        except exc.OperationalError as oe:
            errMsg = str(oe)
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    "STRDBHandler", "Unexpected Error"
                ),
                errMsg
            )
            self.progress.hide()
            isValid = False
            STDMDb.instance().session.rollback()
            LOGGER.debug(str(oe))

        except exc.IntegrityError as ie:
            errMsg = str(ie)
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    "STRDBHandler",
                    "Duplicate Relationship Error"
                ),
                errMsg
            )
            self.progress.hide()
            isValid = False
            STDMDb.instance().session.rollback()
            LOGGER.debug(str(ie))
        except exc.InternalError as ie:

            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    'STRDBHandler',
                    'InternalError Error'
                ),
                QApplication.translate(
                    'STRDBHandler',
                    'Sorry, there is an internal error. \n'
                    'Restart QGIS to fix the issue.'
                )
            )
            LOGGER.debug(str(ie))
            self.progress.hide()
            isValid = False
            STDMDb.instance().session.rollback()
        except DummyException as e:
            errMsg = str(e)
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    'STRDBHandler', 'Unexpected Error'
                ),
                errMsg
            )
            LOGGER.debug(str(e))
            isValid = False
            STDMDb.instance().session.rollback()
            self.progress.hide()
        finally:

            STDMDb.instance().session.rollback()
            self.progress.hide()

        return isValid
