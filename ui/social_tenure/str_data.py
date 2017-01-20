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


class STRDataStore():
    def __init__(self):
        self.party = OrderedDict()
        self.spatial_unit = OrderedDict()
        self.str_type = OrderedDict()
        self.share = OrderedDict()
        self.validity_period = OrderedDict()
        self.validity_period['from_date'] = None
        self.validity_period['to_date'] = None
        self.supporting_document = []
        self.source_doc_manager = None

class STRDBHandler():
    def __init__(
            self, data_store, str_model, str_edit_node=None
    ):
        self.str_model = str_model
        self.data_store = data_store
        self.str_edit_obj = None
        self.progress = STDMProgressDialog(iface.mainWindow())

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

        party_name = str_store.party.values()[0].__table__.name
        index = 4
        # Social tenure and supporting document insertion
        # The code below is have a workaround to enable
        # batch supporting documents without affecting single
        # party upload. The reason a hack was needed is,
        # whenever a document is inserted in a normal way,
        # duplicate entry is added to the database.
        no_of_party = len(str_store.party)

        for j, (party_id, str_type_id) in \
                enumerate(str_store.str_type.iteritems()):
            # get all doc model objects
            doc_objs = str_store.supporting_document
            # get the number of unique documents.
            number_of_docs = len(doc_objs) / no_of_party

            party_entity_id = '{}_id'.format(party_name[3:])
            start_date = str_store.validity_period['from_date']
            end_date = str_store.validity_period['to_date']

            str_args = {
                party_entity_id: party_id,
                'spatial_unit_id': str_store.spatial_unit.keys()[0],
                'tenure_type': str_type_id,
                'validity_start': start_date.toPyDate(),
                'validity_end': end_date.toPyDate(),
                'tenure_share': str_store.share[party_id]
            }
            str_obj = self.str_model(**str_args)
            # Insert Supporting Document if a
            # supporting document is uploaded.
            if len(doc_objs) > 0:
                # # loop through each document objects
                # loop per each number of documents
                for k in range(number_of_docs):
                    # The number of jumps (to avoid duplication) when
                    # looping though document objects in multiple party
                    loop_increment = (k * no_of_party) + j
                    # append into the str obj
                    str_obj.documents.append(
                        doc_objs[loop_increment]
                    )

            str_objs.append(str_obj)
            index = index + 1
        _str_obj.saveMany(str_objs)

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

        start_date = str_store.validity_period['from_date']
        end_date = str_store.validity_period['to_date']
        if isinstance(start_date, QDate):
            start_date = start_date.toPyDate()
        if isinstance(end_date, QDate):
            end_date = end_date.toPyDate()

        str_edit_obj.spatial_unit_id = str_store.spatial_unit.keys()[0],
        str_edit_obj.tenure_type = str_store.str_type.values()[0],
        str_edit_obj.validity_start = start_date,
        str_edit_obj.validity_end = end_date,
        str_edit_obj.tenure_share = str_store.share[
            str_store.party.keys()[0]
        ]

        # get all doc model objects
        added_doc_objs = str_store.supporting_document

        self.str_doc_edit_obj = \
            [obj for obj in sum(self.str_doc_edit_obj.values(), [])]

        new_doc_objs = list(set(added_doc_objs) -
                            set(self.str_doc_edit_obj))

        # Insert supporting document if a new
        # supporting document is uploaded.
        if len(new_doc_objs) > 0:

            # looping though newly added objects list
            for doc_obj in new_doc_objs:
                # append into the str edit obj
                str_edit_obj.documents.append(
                    doc_obj
                )

        str_edit_obj.update()

        return str_edit_obj

    def commit_str(self):
        """
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        """
        isValid = True
        # Create a progress dialog
        try:

            self.progress.show()
            if self.str_edit_obj is None:
                self.progress.setRange(0, len(self.data_store) - 1)
                self.progress.overall_progress(
                    'Creating a STR...',
                )

                for i, str_store in enumerate(
                        self.data_store.values()
                ):
                    self.progress.progress_message(
                        'Saving STR {}'.format(i+1), ''
                    )
                    self.progress.setValue(i)

                    self.on_add_str(str_store)

            else:
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
                return updated_str_obj
            self.progress.hide()
            mode = 'created'
            if self.str_edit_obj is not None:
                mode = 'updated'
            strMsg = QApplication.translate(
                "STRDBHandler",
                "The social tenure relationship has "
                "been successfully {}!".format(mode)
            )
            QMessageBox.information(
                iface.mainWindow(), QApplication.translate(
                    "STRDBHandler", "Social Tenure Relationship"
                ),
                strMsg
            )

        except exc.OperationalError as oe:
            errMsg = oe.message
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

        except exc.IntegrityError as ie:
            errMsg = ie.message
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

        except exc.InternalError:

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
            self.progress.hide()
            isValid = False
            STDMDb.instance().session.rollback()
        except Exception as e:
            errMsg = unicode(e)
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    'STRDBHandler', 'Unexpected Error'
                ),
                errMsg
            )

            isValid = False
            STDMDb.instance().session.rollback()
            self.progress.hide()
        finally:

            STDMDb.instance().session.rollback()
            self.progress.hide()

        return isValid