"""
/***************************************************************************
Name                 : New STR Wizard  
Description          : Wizard that enables users to define a new social tenure
                       relationship.
Date                 : 3/July/2013 
copyright            : (C) 2013 by John Gitau
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
import logging
from collections import OrderedDict

from stdm.data.qtmodels import BaseSTDMTableModel
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sqlalchemy

from notification import NotificationBar,ERROR,INFO, WARNING
from sourcedocument import *

from stdm.data.database import (
    STDMDb,
    Base
)
from stdm.settings import (
    current_profile
)
from stdm.utils.util import (
    format_column,
    entity_display_columns,
    model_display_data
)
from stdm.data.configuration import entity_model

from stdm.navigation import (
    TreeSummaryLoader,
    WebSpatialLoader,
    GMAP_SATELLITE,
    OSM
)
from stdm.utils import *
from stdm.utils.util import (
lookup_id_to_value
)
from ui_new_str import Ui_frmNewSTR

LOGGER = logging.getLogger('stdm')

class newSTRWiz(QWizard, Ui_frmNewSTR):
    '''
    This class handles the listing of locality information
    '''
    def __init__(self, plugin):
        QWizard.__init__(self, plugin.iface.mainWindow())
        ## TODO when forms are done check if db insert
        ## TODO is ordered as shown
        ## TODO in party and str_type pages and each
        ## TODO party and str_type matches.
        ## TODO Use OrderDict if mismatch found
        self.setupUi(self)
        #STR Variables
        self.sel_party = []
        self.sel_spatial_unit = []
        self.sel_str_type = []
        self.row = 0 # number of party rows
        # Current profile instance and properties
        self.curr_profile = current_profile()

        self.prefix = self.curr_profile.prefix

        self.party = self.curr_profile.social_tenure.party

        self.spatial_unit = self.curr_profile.social_tenure.spatial_unit

        self.str_type = self.curr_profile.social_tenure.tenure_type_collection

        self.init_party()
        self.party_header = []
        self.init_spatial_unit()
        self.init_document_type()
        self.initSourceDocument()
        #Connect signal when the finish button is clicked
        btnFinish = self.button(QWizard.FinishButton)

    def init_party(self):
        '''
        Initialize person config
        '''
        self.notifPerson = NotificationBar(self.vlPersonNotif)

        #Init summary tree loaders
        self.personTreeLoader = TreeSummaryLoader(
            self.tvPersonInfo,
            QApplication.translate(
                "newSTRWiz",
                "Party Information"
            )
        )
        party_data = []
        vertical_layout = QVBoxLayout(
            self.tvPersonInfo
        )
        party_table = self.create_table(
            self.tvPersonInfo, vertical_layout
        )

        self.add_table_headers(
            self.party, party_data, party_table
        )

        self.AddPartybtn.clicked.connect(
            lambda: self.add_record(
                party_table, self.party, party_data
            )
        )

        self.AddPartybtn.clicked.connect(
            self.init_str_type
        )

        self.RemovePartybtn.clicked.connect(
            lambda: self.remove_row(
                party_table, self.notifPerson
            )
        )

    def init_spatial_unit(self):
        '''
        Initialize property config
        '''
        self.notifProp = NotificationBar(
            self.vlPropNotif
        )
        self.gpOLTitle = self.gpOpenLayers.title()
        
        # Flag for checking whether
        # OpenLayers basemaps have been loaded
        self.olLoaded = False

        spatial_unit_data = []
        vertical_layout = QVBoxLayout(self.tvPropInfo)
        spatial_unit_table = self.create_table(
            self.tvPropInfo,
            vertical_layout
        )
        self.add_table_headers(
            self.spatial_unit,
            spatial_unit_data,
            spatial_unit_table
        )
        self.AddSpatialUnitbtn.clicked.connect(
            lambda: self.add_record(
                spatial_unit_table,
                self.spatial_unit,
                spatial_unit_data
            )
        )
        self.RemoveSpatialUnitbtn.clicked.connect(
            lambda: self.remove_row(
                spatial_unit_table, self.notifPerson
            )
        )
        #Connect signals
        QObject.connect(
            self.gpOpenLayers,
            SIGNAL("toggled(bool)"),
            self._onEnableOLGroupbox
        )
        QObject.connect(
            self.zoomSlider,
            SIGNAL("sliderReleased()"),
            self._onZoomChanged
        )
        QObject.connect(
            self.btnResetMap,
            SIGNAL("clicked()"),
            self._onResetMap
        )
        
        #Start background thread
        self.propBrowser = WebSpatialLoader(
            self.propWebView, self
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadError(QString)"),
            self._onPropertyBrowserError
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadProgress(int)"),
            self._onPropertyBrowserLoading
        )
        self.connect(
            self.propBrowser,
            SIGNAL("loadFinished(bool)"),
            self._onPropertyBrowserFinished
        )
        self.connect(
            self.propBrowser,
            SIGNAL("zoomChanged(int)"),
            self.onMapZoomLevelChanged
        )

        #Connect signals
        QObject.connect(
            self.rbGMaps,
            SIGNAL("toggled(bool)"),
            self.onLoadGMaps
        )
        QObject.connect(
            self.rbOSM,
            SIGNAL("toggled(bool)"),
            self.onLoadOSM
        )

    def remove_row(self, table_view, notification):

        if len(table_view.selectedIndexes()) > 0:
            row_index = table_view.selectedIndexes()[0]
            table_view.model().removeRow(
                row_index.row(), row_index
            )
            table_view.model().layoutChanged.emit()
            if notification == self.notifPerson:
                self.remove_str_type(row_index.row())

        else:
            msg = QApplication.translate(
                        "newSTRWiz",
                        "Please select a row you"
                        " would like to remove. "
            )
            notification.clear()
            notification.insertNotification(msg, ERROR)


    def remove_str_type(self, row_position):
        # As there are two tableviews for each party row,
        # we have to multiply by 2 to get the correct
        # position of matching FreezeTableWidget
        matching_table = row_position * 2
        for position, item in enumerate(
                self.frmWizSTRType.findChildren(QTableView)
        ):
            if item.__class__.__name__ == 'FreezeTableWidget':
                if position == matching_table:
                    self.verticalLayout_11.removeWidget(item)
                    item.deleteLater()


    def initializePage(self, id):
        '''
        Initialize summary page based on user selections.
        '''
        if id == 5:
            self.buildSummary()

    def create_table(self, parent, container):
        table_view = QTableView()

        table_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        table_view.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        table_view.setAlternatingRowColors(True)

        container.setSpacing(4)
        container.setMargin(5)
        grid_layout = QGridLayout(parent)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)
        container.addLayout(grid_layout)
        container.addWidget(table_view)
        # For reduce the height for spatial unit
        if parent == self.tvPropInfo:
            table_view.setMinimumSize(QSize(55, 30))
            table_view.setMaximumSize(QSize(5550, 75))
        return table_view

    def create_str_type_table(
            self, parent, container, table_data, headers
    ):
        table_view = FreezeTableWidget(
            table_data, headers, parent
        )
        table_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        table_view.SelectionMode(
            QAbstractItemView.NoSelection
        )
        container.setSpacing(4)
        container.setMargin(5)
        grid_layout = QGridLayout(parent)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)
        container.addLayout(grid_layout)
        container.addWidget(table_view)

        return table_view

    def update_table_view(self, table_view, str_type):
        # show grid
        table_view.setShowGrid(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        table_view.resizeRowsToContents()
        # enable sorting
        table_view.setSortingEnabled(False)
        if str_type:
            table_view.hideColumn(1)
        else:
            table_view.hideColumn(0)

    def prepare_table_model(
            self, tableview, table_data, headers, parent
    ):
        table_model = BaseSTDMTableModel(
            table_data, headers, parent
        )
        tableview.setModel(table_model)

        tableview.horizontalHeader().setResizeMode(
            QHeaderView.Interactive
        )
        tableview.verticalHeader().setVisible(True)

    def add_table_headers(
            self, entity, table_data, tableview, str_type=False
    ):
        """
        Adds headers from model columns.
        Returns: None
        """
        db_model = entity_model(entity, True)
        headers = []
        #Load headers
        if db_model is not None:
            entity_display_columns(self.party)
            # Append str type if the method is used for str_type
            if str_type:
                #First (ID) column will always be hidden
                headers.append('Social Tenure Type')

            for col in entity_display_columns(entity):
                headers.append(format_column(col))
            if not str_type:
                self.prepare_table_model(
                    tableview, table_data, headers, self
                )
        if entity == self.party:
            self.party_header = headers

        if str_type:
            return headers
        else:
            self.update_table_view(tableview, str_type)

    def add_record(
            self, table_view, entity, table_data, str_type=False
    ):

        data = OrderedDict()
        db_model = entity_model(entity, True)
        db_obj = db_model()

        if str_type:
            data['social_tenure_type'] = None

        for col in entity_display_columns(entity):
            attr = getattr(db_model, col)

            value = db_obj.queryObject([attr]).all()[0][0]
            # change id to value if lookup, else return the same value
            value = lookup_id_to_value(
                self.curr_profile, col, value
            )
            data[col] = value
        if entity == self.spatial_unit:
            if table_view.model().rowCount() > 0:
                table_view.model().rowCount(0)
                table_view.model().removeRow(0)

        table_data.append(data.values())
        if entity == self.spatial_unit:
            spatial_unit_id = self.get_spatial_unit_data()
            self.set_record_to_model(
                self.spatial_unit, spatial_unit_id
            )
        table_view.model().layoutChanged.emit()
        self.update_table_view(table_view, str_type)


    def get_table_data(self, table_view, str_type=True):
        model = table_view.model()
        table_data = []
        if str_type:
            str_type_idx = model.index(0, 0)
            party_id_idx = model.index(0, 1)
            table_data.append(model.data(
                party_id_idx, Qt.DisplayRole
            ))
            table_data.append(model.data(
                str_type_idx, Qt.DisplayRole
            ))
        else:
            spatial_unit_idx = model.index(0, 0)
            table_data.append(model.data(
                spatial_unit_idx, Qt.DisplayRole
            ))
            #print table_data
        return table_data

    def get_party_str_type_data(self):
         str_types = []
         party_ids = []
         for item in self.frmWizSTRType.findChildren(QTableView):
             if item.__class__.__name__ == 'FreezeTableWidget' and \
                             item is not None:
                party_id, str_type = self.get_table_data(item)
                party_ids.append(party_id)
                str_types.append(str_type)
         return party_ids, str_types

    def get_spatial_unit_data(self):
        spatial_unit_id = None
        for item in self.tvPropInfo.findChildren(QTableView):
            if item is not None:
                spatial_unit_id = self.get_table_data(item, False)
                break

        return spatial_unit_id

    def set_record_to_model(self, entity, sel_attr):
        db_model = entity_model(entity, True)
        db_obj = db_model()
        if entity == self.party:
            self.sel_party = []
            for sel_id in sel_attr:
                party_query = db_obj.queryObject(
                    entity_display_columns(entity)
                ).filter(
                db_model.id == sel_id
                ).first()
                self.sel_party.append(party_query)

        if entity == self.spatial_unit:
            self.sel_spatial_unit = []
            spatial_unit_query = db_obj.queryObject().filter(
            db_model.id == sel_attr[0]
            ).first()
            self.sel_spatial_unit.append(spatial_unit_query)

        if entity == self.str_type:
            self.sel_str_type = []
            for sel_value in sel_attr:
                str_query = db_obj.queryObject().filter(
                    db_model.value == sel_value
                ).all()

                sel_str_type_id = getattr(
                    str_query[0],
                    'id',
                    None
                )
                self.sel_str_type.append(sel_str_type_id)

    def init_str_type(self):
        '''
        Initialize 'Social Tenure Relationship' GUI controls
        '''
        party_data = []
        headers = self.add_table_headers(
            self.party,
            party_data,
            None,
            True
        )
        party_table = self.create_str_type_table(
            self.STRTypeWidget,
            self.verticalLayout_11,
            party_data,
            headers
        )

        self.add_record(
            party_table,
            self.party,
            party_data,
            True
        )

        self.notifSTR = NotificationBar(
            self.vlSTRTypeNotif
        )


    def init_document_type(self):
        '''
        Initialize 'Right of Enjoyment' GUI controls
        '''
        doc_entity = self.curr_profile.entity_by_name(
            unicode(self.prefix+'_check_document_type')
        )
        doc_type_model = entity_model(doc_entity)

        Docs = doc_type_model()
        doc_type_list = Docs.queryObject().all()
        doc_types = [doc.value for doc in doc_type_list]
        doc_types.insert(0," ")
        self.cboDocType.insertItems(0, doc_types)
        self.cboDocType.setCurrentIndex(-1)
        self.vlSourceDocNotif = NotificationBar(
            self.vlSourceDocNotif
        )
        
    def initSourceDocument(self):
        '''
        Initialize source document page
        '''
        #Set currency regular expression and currency prefix
        rx = QRegExp("^\\d{1,12}(([.]\\d{2})*),(\\d{2})$")
        rxValidator = QRegExpValidator(rx,self)
        '''
        '''
        self.notifSourceDoc = NotificationBar(
            self.vlSourceDocNotif
        )
        #Set source document manager
        self.sourceDocManager = SourceDocumentManager()
        self.sourceDocManager.registerContainer(
            self.vlDocTitleDeed, DEFAULT_DOCUMENT
        )
        self.connect(
            self.btnAddTitleDeed,
            SIGNAL("clicked()"),
            self.onUploadTitleDeed
        )

    def buildSummary(self):
        '''
        Display summary information in the tree view.
        '''
        summaryTreeLoader = TreeSummaryLoader(self.twSTRSummary)

        sel_party, sel_str_types = self.get_party_str_type_data()
        # Add each str type next to each party.
        for q_obj, item in zip(self.sel_party, sel_str_types):
            party_mapping = model_display_data(
                q_obj, self.party, self.curr_profile
            )

            summaryTreeLoader.addCollection(
                party_mapping,
                QApplication.translate(
                    "newSTRWiz","Party Information"),
                ":/plugins/stdm/images/icons/user.png"
            )

            str_mapping = self.map_str_type(item)
            summaryTreeLoader.addCollection(
                str_mapping,
                QApplication.translate(
                    "newSTRWiz",
                    "Social Tenure Relationship Information"),
                ":/plugins/stdm/images/icons/social_tenure.png"
            )

        for q_obj in self.sel_spatial_unit:
            spatial_unit_mapping = model_display_data(
                q_obj, self.spatial_unit, self.curr_profile
            )

            summaryTreeLoader.addCollection(
                spatial_unit_mapping,
                QApplication.translate(
                    "newSTRWiz", "Spatial Unit Information"),
                ":/plugins/stdm/images/icons/property.png"
            )


        #Check the source documents based on the type of property
        srcDocMapping = self.sourceDocManager.attributeMapping()

        summaryTreeLoader.addCollection(
            srcDocMapping,
            QApplication.translate(
                "newSTRWiz","Source Documents"),
            ":/plugins/stdm/images/icons/attachment.png"
        )
      
        summaryTreeLoader.display()  

    def validateCurrentPage(self):
        '''
        Validate the current page before proceeding to the next one
        '''
        isValid = True
        currPageIndex = self.currentId()       
        
        #Validate person information
        if currPageIndex == 1:
            party_ids, str_type = self.get_party_str_type_data()
            self.set_record_to_model(self.party, party_ids)

            if len(self.sel_party) == 0:
                msg = QApplication.translate(
                    "newSTRWiz",
                    "Please choose a person for whom you are "
                    "defining the social tenure relationship for."
                )
                self.notifPerson.clear()
                self.notifPerson.insertNotification(msg, ERROR)
                isValid = False
        
        #Validate property information
        if currPageIndex == 2:

            if len(self.sel_spatial_unit) == 0:
                msg = QApplication.translate(
                    "newSTRWiz",
                    "Please specify the spatial unit to reference. "
                    "Use the filter capability below.")
                self.notifProp.clear()
                self.notifProp.insertNotification(msg, ERROR)
                isValid = False
        #Validate STR Type
        if currPageIndex == 3:
            #Get current selected index
            party_ids, str_types = self.get_party_str_type_data()
            self.set_record_to_model(self.str_type, str_types)
            if None in str_types or ' ' in str_types:
                msg = QApplication.translate(
                    'newSTRWiz',
                    'Please select an item in the drop down '
                    'menu under each Social Tenure Type column.'
                )
                self.notifSTR.clear()
                self.notifSTR.insertErrorNotification(msg)
                isValid = False

        #Validate source document    
        if currPageIndex == 4:
            currIndex = self.cboDocType.currentIndex()
            if currIndex ==-1:
                msg = QApplication.translate(
                    "newSTRWiz",
                    "Please select document type from the list"
                )
                self.notifSourceDoc.clear()
                self.notifSourceDoc.insertErrorNotification(msg)

        if currPageIndex == 5:
            isValid = self.onCreateSTR()
        return isValid
    
    def onCreateSTR(self):
        '''
        Slot raised when the user clicks on Finish
        button in order to create a new STR entry.
        '''
        isValid = True

        #Create a progress dialog
        prog_dialog = QProgressDialog(self)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "newSTRWiz",
                "Creating New STR"
            )
        )


        str_supp_doc_model = entity_model(
            self.curr_profile.social_tenure.supporting_doc,
            True
        )
        str_supp_doc_model_obj = str_supp_doc_model()

        str_model = entity_model(
            self.curr_profile.social_tenure
        )
        str_model_obj = str_model()
        prog_dialog.setRange(0, len(self.sel_party)-1)
        prog_dialog.show()
        try:

            objects = []
            for i, (sel_party, str_type_id) in enumerate(
                    zip(self.sel_party, self.sel_str_type)
            ):


                # Save new STR relations and supporting documentation
                # if self.curr_profile.social_tenure.supports_documents:
                #     model_objs = self.sourceDocManager.model_objects()
                #     if len(model_objs) > 0:
                #         for model_obj in model_objs:
                #             # print model_obj
                #             model_obj.save()
                #             str_supp_doc_model_obj.\
                #                 social_tenure_relationship_id = str_model_obj.id
                #             setattr(
                #                 str_supp_doc_model_obj,
                #                 self.prefix+'_supporting_doc_id',
                #                 model_obj.id)
                #             str_supp_doc_model_obj.save()
                # else:
                #     self.groupBox_3.setEnabled(False)
                query = str_model(
                    party_id = sel_party.id,
                    spatial_unit_id = self.sel_spatial_unit[0].id,
                    tenure_type = str_type_id
                )

                objects.append(query)
                prog_dialog.setValue(i)
            str_model.saveMany(str_model_obj, objects)

            strMsg = unicode(QApplication.translate(
                "newSTRWiz",
                "The social tenure relationship has "
                "been successfully created!"
            ))
            QMessageBox.information(
                self, QApplication.translate(
                    "newSTRWiz", "STR Creation"
                ),
                strMsg
            )

        except sqlalchemy.exc.OperationalError as oe:
            errMsg = oe.message
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz",
                    "Unexpected Error"
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
            errMsg = str(e)
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "newSTRWiz",
                    "Unexpected Error"
                ),
                errMsg
            )

            isValid = False
        finally:
            STDMDb.instance().session.rollback()
            prog_dialog.hide()

        return isValid
        
    def _onPropertyBrowserError(self,err):
        '''
        Slot raised when an error occurs when
        loading items in the property browser
        '''
        self.notifProp.clear()
        self.notifProp.insertNotification(err, ERROR)
        
    def _onPropertyBrowserLoading(self,progress):
        '''
        Slot raised when the property browser is loading.
        Displays the progress of the page loading as a percentage.
        '''
        if progress <= 0 or progress >= 100:
            self.gpOpenLayers.setTitle(self.gpOLTitle)
        else:
            self.gpOpenLayers.setTitle(
                "%s (Loading...%s%%)"%(
                    str(self.gpOLTitle),
                    str(progress)
                )
            )
            
    def _onPropertyBrowserFinished(self,status):
        '''
        Slot raised when the property browser
        finishes loading the content
        '''
        if status:
            self.olLoaded = True
            self.overlayProperty()
        else:
            self.notifProp.clear()
            msg = QApplication.translate(
                "newSTRWiz",
                "Error - The property map cannot be loaded."
            )
            self.notifProp.insertErrorNotification(msg)
        
    def _onEnableOLGroupbox(self,state):
        '''
        Slot raised when a user chooses to select
        the group box for enabling/disabling to view
        the property in OpenLayers.
        '''
        if state:

            if len(self.sel_spatial_unit) < 1:
                self.notifProp.clear()
                msg = QApplication.translate(
                    "newSTRWiz",
                    "You have to add a spatial unit record "
                    "in order to be able to preview it."
                )
                self.notifProp.insertWarningNotification(msg)                
                self.gpOpenLayers.setChecked(False)
                return  
            
            #Load property overlay
            if not self.olLoaded:                
                self.propBrowser.load()            
                   
        else:
            #Remove overlay
            self.propBrowser.removeOverlay()     
            
    def _onZoomChanged(self):
        '''
        Slot raised when the zoom value in the slider changes.
        This is only raised once the user
        releases the slider with the mouse.
        '''
        zoom = self.zoomSlider.value()        
        self.propBrowser.zoom_to_level(zoom)


    def map_str_type(self, item):
        str_mapping = OrderedDict()
        str_mapping[
            QApplication.translate(
                "newSTRWiz","Tenure Type")
        ] = item
        return str_mapping

    def onLoadGMaps(self,state):
        '''
        Slot raised when a user clicks to set
        Google Maps Satellite as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(
                GMAP_SATELLITE
            )
        
    def onLoadOSM(self,state):
        '''
        Slot raised when a user clicks to set
        OSM as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(OSM)
            
    def onMapZoomLevelChanged(self,level):
        '''
        Slot which is raised when the zoom
        level of the map changes.
        '''
        self.zoomSlider.setValue(level)
       
    def _onResetMap(self):
        '''
        Slot raised when the user clicks
        to reset the property
        location in the map.
        '''
        self.propBrowser.zoom_to_extents()
       
    def overlayProperty(self):
        '''
        Overlay property boundaries on
        the basemap imagery
        '''
        geometry_col_name = [c.name for c in
            self.spatial_unit.columns.values()
            if c.TYPE_INFO == 'GEOMETRY'
        ]
        for geom in geometry_col_name:
            self.propBrowser.add_overlay(
                self.sel_spatial_unit[0], geom
            )

    def onUploadTitleDeed(self):
        '''
        Slot raised when the user clicks
        to upload a title deed
        '''
        titleStr = QApplication.translate(
            "newSTRWiz",
            "Specify the Document File Location"
        )
        titles = self.selectSourceDocumentDialog(titleStr)

        for title in titles:
            self.sourceDocManager.insertDocumentFromFile(
                title,
                DEFAULT_DOCUMENT
            )


    def selectSourceDocumentDialog(self,title):
        '''
        Displays a file dialog for a user
        to specify a source document
        '''
        files = QFileDialog.getOpenFileNames(
            self, title,"/home","Source "
            "Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)"
        )
        return files
        
    def uploadDocument(self,path,containerid):
        '''
        Upload source document
        '''
        self.sourceDocManager.insertDocumentFromFile(
            path, containerid
        )

class ComboBoxDelegate(QItemDelegate):
    def __init__(self, parent = None):

        QItemDelegate.__init__(self, parent)
        self.row = 0
        self.curr_profile = current_profile()

    def str_type_combo (self):
        """
        A slot raised to add new str type
        matched with the party.
        :return: None
        """
        str_type_cbo = QComboBox()
        str_type_cbo.setObjectName(
            'STRTypeCbo'+str(self.row+1)
        )
        self.row = self.row + 1
        return str_type_cbo

    def str_type_set_data(self):
        str_lookup_obj = self.curr_profile.social_tenure.\
            tenure_type_collection
        str_types = entity_model(str_lookup_obj, True)
        str_type_obj = str_types()
        self.str_type_data = str_type_obj.queryObject().all()
        strType = [ids.value for ids in self.str_type_data]
        strType.insert(0, " ")
        return strType

    def createEditor(self, parent, option, index):
        str_combo = QComboBox(parent)
        str_combo.insertItems(
            0, self.str_type_set_data()
        )
        return str_combo

    def setEditorData( self, comboBox, index ):
        list_item_index = index.model().data(
            index, Qt.DisplayRole
        )
        if list_item_index is not None and \
                not isinstance(list_item_index, (unicode, int)):
            value = list_item_index.toInt()
            comboBox.setCurrentIndex(value[0])

    def setModelData(self, editor, model, index):
        value = editor.currentIndex()
        model.setData(
            index,
            editor.itemData(
            value, Qt.DisplayRole)
        )

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class FreezeTableWidget(QTableView):
    def __init__(
            self, table_data, headers, parent = None, *args
    ):
        QTableView.__init__(self, parent, *args)
        # set the table model
        table_model = BaseSTDMTableModel(
            table_data, headers, parent
        )
        # set the proxy model
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(table_model)

        # Assign a data model for TableView
        self.setModel(table_model)

        # frozen_table_view - first column
        self.frozen_table_view = QTableView(self)
        # Set the model for the widget, fixed column
        self.frozen_table_view.setModel(table_model)
        # Hide row headers
        self.frozen_table_view.verticalHeader().hide()
        # Widget does not accept focus
        self.frozen_table_view.setFocusPolicy(
            Qt.StrongFocus|Qt.TabFocus|Qt.ClickFocus
        )
        # The user can not resize columns
        self.frozen_table_view.horizontalHeader().\
            setResizeMode(QHeaderView.Fixed)
        # Style frozentable view
        self.frozen_table_view.setStyleSheet(
            '''
            border: none;
            background-color: #eee;
            selection-color: black;
            selection-background-color: #ddd;
            '''
        )
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(2)
        self.shadow.setYOffset(0)
        self.frozen_table_view.setGraphicsEffect(self.shadow)

        # Remove the scroll bar
        self.frozen_table_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.frozen_table_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        # Puts more widgets to the foreground
        self.viewport().stackUnder(self.frozen_table_view)
        # # Log in to edit mode - even with one click
        # Set the properties of the column headings
        hh = self.horizontalHeader()
        # Text alignment centered
        hh.setDefaultAlignment(Qt.AlignCenter)

        # Set the width of columns by content
        self.resizeColumnsToContents()


        # Set the width of columns
        columns_count = table_model.columnCount(self)
        for col in xrange(columns_count):
            if col == 0:
                # Set the size
                self.horizontalHeader().resizeSection(
                    col, 60
                )
                # Fix width
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                # Width of a fixed column - as in the main widget
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            elif col == 1:
                self.horizontalHeader().resizeSection(
                    col, 150
                )
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            else:
                self.horizontalHeader().resizeSection(
                    col, 100
                )
                # Hide unnecessary columns in the widget fixed columns
                self.frozen_table_view.setColumnHidden(
                    col, True
                )

        # Set properties header lines
        vh = self.verticalHeader()
        vh.setDefaultSectionSize(25) # height lines
        vh.setDefaultAlignment(Qt.AlignCenter) # text alignment centered
        vh.setVisible(True)
        # Height of rows - as in the main widget
        self.frozen_table_view.verticalHeader().\
            setDefaultSectionSize(
            vh.defaultSectionSize()
        )

        # Show our optional widget
        self.frozen_table_view.show()
        # Set the size of him like the main
        self.update_frozen_table_geometry()

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.frozen_table_view.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        delegate = ComboBoxDelegate()

        # Set delegate to add combobox under
        # social tenure type column
        self.frozen_table_view.setItemDelegate(
            delegate
        )
        self.frozen_table_view.setItemDelegateForColumn(
            0, delegate
        )
        index = self.frozen_table_view.model().index(
            0, 0, QModelIndex()
        )
        self.frozen_table_view.model().setData(
            index, '', Qt.EditRole
        )

        self.frozen_table_view.setEditTriggers(
            QAbstractItemView.AllEditTriggers
        )
        size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.sizePolicy().hasHeightForWidth()
        )
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QSize(55, 75))
        self.setMaximumSize(QSize(5550, 75))
        self.setGeometry(QRect(0, 0, 619, 75))
        # set column width to fit contents
        self.frozen_table_view.resizeColumnsToContents()
        # set row height
        self.frozen_table_view.resizeRowsToContents()
        # Create a connection

        # Connect the headers and scrollbars of
        # both tableviews together
        self.horizontalHeader().sectionResized.connect(
            self.update_section_width
        )
        self.verticalHeader().sectionResized.connect(
            self.update_section_height
        )
        self.frozen_table_view.verticalScrollBar().\
            valueChanged.connect(
            self.verticalScrollBar().setValue
        )
        self.verticalScrollBar().valueChanged.connect(
            self.frozen_table_view.verticalScrollBar().setValue
        )

    def update_section_width(
            self, logicalIndex, oldSize, newSize
    ):
        if logicalIndex==0 or logicalIndex==1:
            self.frozen_table_view.setColumnWidth(
                logicalIndex, newSize
            )
            self.update_frozen_table_geometry()

    def update_section_height(
            self, logicalIndex, oldSize, newSize
    ):
        self.frozen_table_view.setRowHeight(
            logicalIndex, newSize
        )

    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        try:
            self.update_frozen_table_geometry()
        except Exception as log:
            print log

    def scrollTo(self, index, hint):
        if index.column() > 1:
            QTableView.scrollTo(self, index, hint)

    def update_frozen_table_geometry(self):
        if self.verticalHeader().isVisible():
            self.frozen_table_view.setGeometry(
                self.verticalHeader().width() +
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) +
                self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )
        else:
            self.frozen_table_view.setGeometry(
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) + self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )

    # move_cursor override function for correct
    # left to scroll the keyboard.
    def move_cursor(self, cursor_action, modifiers):
        current = QTableView.move_cursor(
            self, cursor_action, modifiers
        )
        if cursor_action == self.MoveLeft and current.column() > 1 and \
                        self.visualRect(current).topLeft().x() < \
                        (self.frozen_table_view.columnWidth(0) +
                             self.frozen_table_view.columnWidth(1)):
            new_value = self.horizontalScrollBar().value() + \
                       self.visualRect(current).topLeft().x() - \
                       (self.frozen_table_view.columnWidth(0) +
                        self.frozen_table_view.columnWidth(1))
            self.horizontalScrollBar().setValue(new_value)
        return current
