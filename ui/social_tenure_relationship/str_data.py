from collections import OrderedDict
from PyQt4.QtGui import (
QApplication,
QMessageBox,
QProgressDialog
)


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
            self,
            data_store,
            str_model,
            str_edit_obj=None
    ):
        self.str_model = str_model
        self.data_store = data_store

        self.str_edit_obj = str_edit_obj

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
            # get all model objects
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
            #progress.setValue(index)
        _str_obj.saveMany(str_objs)

    def save_str(self):

        for i, str_store in self.data_store.iteritems():
            self.on_add_str(str_store)


    def on_edit_str(self, progress):
        """
         Adds edits a selected STR record
         with a supporting document record, if uploaded.
         :param progress: The progressbar
         :type progress: QProgressDialog
         :return: None
         :rtype: NoneType
         """
        _str_obj = self.str_model()

        progress.setValue(3)

        str_edit_obj = _str_obj.queryObject().filter(
            self.str_model.id == self.str_edit_obj.id
        ).first()

        str_edit_obj.party_id = self.sel_party[0].id,
        str_edit_obj.spatial_unit_id = self.sel_spatial_unit[0].id,
        str_edit_obj.tenure_type = self.sel_str_type[0]

        progress.setValue(5)
        added_doc_objs = self.source_doc_manager.model_objects()

        self.str_doc_edit_obj = [obj for obj in sum(self.str_doc_edit_obj.values(), [])]

        new_doc_objs = list(set(added_doc_objs) - set(self.str_doc_edit_obj))

        self.updated_str_obj = str_edit_obj
        # Insert Supporting Document if a new
        # supporting document is uploaded.
        if len(new_doc_objs) > 0:

            # looping though newly added objects list
            for doc_obj in new_doc_objs:
                # append into the str edit obj
                str_edit_obj.documents.append(
                    doc_obj
                )
        progress.setValue(7)

        str_edit_obj.update()

        self.updated_str_obj = str_edit_obj

        progress.setValue(10)

        progress.hide()

    def commit_str(self):
        """
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        :return: None
        :rtype: NoneType
        """
        isValid = True
        # Create a progress dialog
        prog_dialog = QProgressDialog(self)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "newSTRWiz",
                "Creating New STR"
            )
        )

        try:

            if self.str_edit_obj is None:
                prog_dialog.setRange(0, 4 + len(self.sel_party))
                prog_dialog.show()
                self.on_add_str(prog_dialog)
            else:
                prog_dialog.setRange(0, 10)
                prog_dialog.show()
                self.on_edit_str(prog_dialog)

            mode = 'created'
            if self.str_edit_obj is not None:
                mode = 'updated'
            strMsg = unicode(QApplication.translate(
                "newSTRWiz",
                "The social tenure relationship has "
                "been successfully {}!".format(mode)
            ))
            QMessageBox.information(
                self, QApplication.translate(
                    "newSTRWiz", "Social Tenure Relationship"
                ),
                strMsg
            )

        except sqlalchemy.exc.OperationalError as oe:
            errMsg = oe.message
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz", "Unexpected Error"
                ),
                errMsg
            )
            prog_dialog.hide()
            isValid = False

        except sqlalchemy.exc.IntegrityError as ie:
            errMsg = ie.message
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz",
                    "Duplicate Relationship Error"
                ),
                errMsg
            )
            prog_dialog.hide()
            isValid = False

        except Exception as e:
            errMsg = unicode(e)
            QMessageBox.critical(
                self,
                QApplication.translate(
                    'newSTRWiz', 'Unexpected Error'
                ),
                errMsg
            )

            isValid = False
        finally:
            STDMDb.instance().session.rollback()
            prog_dialog.hide()

        return isValid