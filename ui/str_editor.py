"""
/***************************************************************************
Name                 : Social Tenure Relationship Editor
Description          : Dialog for creating/updating STR information.
Date                 : 25/September/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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
from PyQt4.QtGui import (
    QDialog,
    QApplication,
    QFileDialog,
    QMessageBox
)

from stdm.data import (
    MapperMixin,
    SAVE,
    UPDATE
)

from .notification import NotificationBar
from .sourcedocument import (
    STR_DOC_TYPE_MAPPING,
    SourceDocumentManager,
    source_document_location,
    set_source_document_location
)
from .ui_str_editor import Ui_frmSTREditor

__all__ = ["SocialTenureEditor"]

def property_deed_filter(documents):
    """
    Extract photos of PROPERTY_DEED type from the documents collection. For use in the source document value handler.
    :param documents: Collection of supporting documents in the SourceDocumentManager control.
    :type documents: dict
    :return: Property deed documents in the control.
    :rtype: list
    """
    if PROPERTY_DEED in documents:
        return documents[PROPERTY_DEED]

    return []

def registered_deed_filter(documents):
    """
    Extract photos of REGISTERED_PROPERTY_DEED type from the documents collection. For use in the source document value handler.
    :param documents: Collection of supporting documents in the SourceDocumentManager control.
    :type documents: dict
    :return: Registered property deed documents in the control.
    :rtype: list
    """
    if REGISTERED_PROPERTY_DEED in documents:
        return documents[REGISTERED_PROPERTY_DEED]

    return []

def written_contract_filter(documents):
    """
    Extract photos of REGISTERED_PROPERTY_DEED type from the documents collection. For use in the source document value handler.
    :param documents: Collection of supporting documents in the SourceDocumentManager control.
    :type documents: dict
    :return: Registered property deed documents in the control.
    :rtype: list
    """
    if W_TENANCY_CONTRACT in documents:
        return documents[W_TENANCY_CONTRACT]

    return []

def oral_contract_filter(documents):
    """
    Extract photos of O_TENANCY_CONTRACT type from the documents collection. For use in the source document value handler.
    :param documents: Collection of supporting documents in the SourceDocumentManager control.
    :type documents: dict
    :return: Oral contract documents in the control.
    :rtype: list
    """
    if O_TENANCY_CONTRACT in documents:
        return documents[O_TENANCY_CONTRACT]

    return []

def general_str_filter(documents):
    """
    Extract photos of OTHER_STR_DOCUMENT type from the documents collection. For use in the source document value handler.
    :param documents: Collection of supporting documents in the SourceDocumentManager control.
    :type documents: dict
    :return: Other STR documents in the control.
    :rtype: list
    """
    if OTHER_STR_DOCUMENT in documents:
        return documents[OTHER_STR_DOCUMENT]

    return []

class SocialTenureEditor(QDialog, Ui_frmSTREditor, MapperMixin):
    """
    Dialog for creating/updating STR information.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        MapperMixin.__init__(self, data_model)

        self._notifBar = NotificationBar(self.vlNotification)

        #STR document manager
        self.doc_manager = SourceDocumentManager(self)
        self.doc_manager.registerContainer(self.vl_property_deed, PROPERTY_DEED)
        self.doc_manager.registerContainer(self.vl_registered_property, REGISTERED_PROPERTY_DEED)
        self.doc_manager.registerContainer(self.vl_tenancy_contract, W_TENANCY_CONTRACT)
        self.doc_manager.registerContainer(self.vl_oral_tenancy_contract, O_TENANCY_CONTRACT)
        self.doc_manager.registerContainer(self.vl_doc_other, OTHER_STR_DOCUMENT)

        self._curr_doc_type = None

        #Load STR document types
        self._load_str_doc_types()

        self._configure_foreign_key_mappers()
        self._configure_yes_no_selectors()

        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        self.cbo_str_type.combo_box().currentIndexChanged.connect(self._on_str_changed)
        self.gb_conflict.toggled.connect(self._on_conflict_selected)
        self.cbo_doc_type.currentIndexChanged.connect(self._on_document_type_changed)
        self.btn_add_doc.clicked.connect(self.load_str_document_selector)

        self.addMapping("type", self.cbo_str_type.combo_box(), True,
                        pseudoname = QApplication.translate("SocialTenureEditor",
                                                            "Social Tenure Relationship Type"))
        self.addMapping("other_type", self.cbo_str_type.line_edit())
        self.addMapping("pay_land_taxes", self.chk_land_taxes)
        self.addMapping("has_conflict", self.gb_conflict)
        self.addMapping("conflict_party", self.txt_conflict_party)
        self.addMapping("conflict_description", self.txt_conflict_description)
        self.addMapping("paid", self.chk_paid)
        self.addMapping("tenure_support", self.txt_tenure_support)
        self.addMapping("general_docs", self.doc_manager, get_func=general_str_filter)
        self.addMapping("oral_tenancy_docs", self.doc_manager, get_func=oral_contract_filter)
        self.addMapping("reg_property_docs", self.doc_manager, get_func=registered_deed_filter)
        self.addMapping("written_tenancy_docs", self.doc_manager, get_func=written_contract_filter)
        self.addMapping("property_docs", self.doc_manager, get_func=property_deed_filter)

    def _on_str_changed(self, index):
        str_type = self.cbo_str_type.combo_box().currentText()

        #Land taxes condition
        if str_type == SocialTenureRelationshipType.ownership.description or \
            str_type == SocialTenureRelationshipType.possession.description or \
            str_type == SocialTenureRelationshipType.usufruct.description:
            self.chk_land_taxes.setEnabled(True)

        else:
            self.chk_land_taxes.setEnabled(False)
            self.chk_land_taxes.set_state(False)

        #Paid condition
        if str_type == SocialTenureRelationshipType.ownership.description:
            self.chk_paid.setEnabled(True)

        else:
            #QMessageBox.information(self,"Info", str_type)
            self.chk_paid.setEnabled(False)
            self.chk_paid.set_state(False)

        #Plot owner condition
        if str_type == SocialTenureRelationshipType.possession.description or \
            str_type == SocialTenureRelationshipType.usufruct.description:
            self.txt_plot_owner.setEnabled(True)

        else:
            self.txt_plot_owner.setEnabled(False)
            self.txt_plot_owner.clear()

    def _load_str_doc_types(self):
        self.cbo_doc_type.addItem("")

        for doc_type, display in STR_DOC_TYPE_MAPPING.iteritems():
            self.cbo_doc_type.addItem(display, doc_type)

    def _configure_foreign_key_mappers(self):
        #TODO: Do away with inline imports.
        from .entity_browser import (
            HouseUnitEntityBrowser,
            HouseholdEntityBrowser
        )

        #Houseunit
        self.fk_house_unit.set_database_model(HouseUnit)
        self.fk_house_unit.setEntitySelector(HouseUnitEntityBrowser)
        self.fk_house_unit.setSupportsList(False)
        self.fk_house_unit.setCellFormatters(house_unit_formatters())
        self.fk_house_unit.set_notification_bar(self._notifBar)
        self.fk_house_unit.initialize()
        self.addMapping("houseunit", self.fk_house_unit, True,
                        pseudoname = QApplication.translate("SocialTenureEditor", "Houseunit"))

        #Household
        self.fk_household.set_database_model(Household)
        self.fk_household.setEntitySelector(HouseholdEntityBrowser)
        self.fk_household.setSupportsList(False)
        self.fk_household.setCellFormatters(household_formatters())
        self.fk_household.set_notification_bar(self._notifBar)
        self.fk_household.initialize()
        self.addMapping("household", self.fk_household, True,
                        pseudoname = QApplication.translate("SocialTenureEditor", "Household"))

    def _configure_yes_no_selectors(self):
        self.chk_land_taxes.set_info(QApplication.translate("SocialTenureEditor",
                                                            "Land taxes paid?"))
        self.chk_paid.set_info(QApplication.translate("SocialTenureEditor",
                                                            "Paid?"))

    def _on_conflict_selected(self, state):
        if not state:
            self.txt_conflict_party.clear()
            self.txt_conflict_description.clear()

    def _on_document_type_changed(self, index):
        doc_type = self.cbo_doc_type.itemData(index)

        self.txt_tenure_support.clear()

        #Enable/disable support to tenure
        if doc_type == OTHER_STR_DOCUMENT:
            self.txt_tenure_support.setEnabled(True)
            self.txt_tenure_support.setFocus()

        else:
            self.txt_tenure_support.setEnabled(False)
            self.txt_tenure_support.setText(self.cbo_doc_type.currentText())

        if not doc_type:
            self._curr_doc_type = None

        else:
            self._curr_doc_type = doc_type

    def preSaveUpdate(self):
        """
        Assert if a social tenure relationship has been defined for the
        selected household.
        :returns: The selected household has an existing social tenure
        relationship already defined.
        :rtype: bool
        """
        sel_household = self.fk_household.entities()

        if sel_household is None:
            '''
            Let superclass run through the mandatory fields and return
            appropriate notifications
            '''
            return True

        st_relation = sel_household.social_tenure

        if len(st_relation) == 0:
            return True

        else:
            if self.saveMode() == UPDATE and self.model().id == st_relation[0].id:
                return True

            self._notifBar.clear()
            msg = QApplication.translate("SocialTenureEditor",
                                         "Conflict. A social tenure relationship"
                                         " already exists for the selected household.")
            self._notifBar.insertErrorNotification(msg)

            return False

    def load_str_document_selector(self):
        """
        Slot to show file selection dialog for selecting an STR document.
        """
        if self._curr_doc_type is None:
            self._notifBar.clear()
            msg = QApplication.translate("SocialTenureEditor",
                                         "Please specify the document type")
            self._notifBar.insertWarningNotification(msg)

            return

        title = STR_DOC_TYPE_MAPPING[self._curr_doc_type]

        docs = QFileDialog.getOpenFileNames(self, title, source_document_location(),\
                                              "STR Documents (*.pdf *.png *.jpg *.bmp)")

        #Write path of supporting documents to registry
        if len(docs) > 0:
            set_source_document_location(docs[0])

        for doc in docs:
            self.doc_manager.insertDocumentFromFile(doc, self._curr_doc_type)

