from collections import OrderedDict
from PyQt4.QtGui import (
QApplication,
QMessageBox,
QProgressDialog
)

from qgis.utils import (
    iface
)

from sqlalchemy import exc
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
        self.supporting_document = []
        self.source_doc_manager = None

    def remove_party_data(self, id):
        del self.party[id]

    def remove_spatial_data(self, id):
        del self.spatial_unit[id]


    def remove_str_type_data(self, party_id):
        del self.str_type[party_id]

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
        :param progress: The progressbar
        :type progress: QProgressDialog
        :return: None
        :rtype: NoneType
        """

        _str_obj = self.str_model()
        str_objs = []

        index = 4
        #progress.setValue(3)
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

            str_obj = self.str_model(
                party_id=party_id,
                spatial_unit_id=str_store.spatial_unit.keys()[0],
                tenure_type=str_type_id
            )
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

    def save_str(self):
        if self.str_edit_obj is None:
            for str_store in self.data_store.values():
                self.on_add_str(str_store)

        else:
            if len(self.data_store) == 1:

                updated_str_obj = self.on_edit_str(
                    self.data_store[1]
                )
                return updated_str_obj
            else:
                return None


    def on_edit_str(self, str_store):
        """
         Adds edits a selected STR record
         with a supporting document record, if uploaded.
         :param progress: The progressbar
         :type progress: QProgressDialog
         :return: None
         :rtype: NoneType
         """
        _str_obj = self.str_model()

        str_edit_obj = _str_obj.queryObject().filter(
            self.str_model.id == self.str_edit_obj.id
        ).first()

        str_edit_obj.party_id = str_store.party.keys()[0],
        str_edit_obj.spatial_unit_id = str_store.spatial_unit.keys()[0],
        str_edit_obj.tenure_type = str_store.str_type.values()[0]

        # get all doc model objects
        added_doc_objs = str_store.supporting_document

        self.str_doc_edit_obj = \
            [obj for obj in sum(self.str_doc_edit_obj.values(), [])]

        new_doc_objs = list(set(added_doc_objs) -
                            set(self.str_doc_edit_obj))

        # Insert Supporting Document if a new
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
        :return: None
        :rtype: NoneType
        """
        isValid = True
        # Create a progress dialog
        try:
            self.progress.setRange(0, len(self.data_store) - 1)
            self.progress.show()
            if self.str_edit_obj is None:
                self.progress.overall_progress(
                    'Creating a STR...',
                )

                for i, str_store in enumerate(self.data_store.values()):
                    self.progress.progress_message(
                        'Saving STR {}'.format(i+1), ''
                    )
                    self.progress.setValue(i)

                    self.on_add_str(str_store)

            else:
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