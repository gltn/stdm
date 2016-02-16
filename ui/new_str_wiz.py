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
from collections import OrderedDict
from decimal import Decimal
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import sqlalchemy
from sqlalchemy import Table

from notification import NotificationBar,ERROR,INFO, WARNING
from sourcedocument import *

from stdm.data.database import (
    STDMDb,
    Base
)
from stdm.data.config_utils import (
    UserData,
    table_searchable_cols,
    tableCols
)
from stdm.navigation import TreeSummaryLoader,WebSpatialLoader, GMAP_SATELLITE, OSM
from stdm.utils import *
from .stdmdialog import  DeclareMapping

from ui_new_str import Ui_frmNewSTR

class newSTRWiz(QWizard, Ui_frmNewSTR):
    '''
    This class handles the listing of locality information
    '''
    def __init__(self,plugin):
        QWizard.__init__(self,plugin.iface.mainWindow())
        self.setupUi(self)
        
        #STR Variables
        self.selPerson = None
        self.selProperty = None
        self.enjoymentRight = None
        self.conflict = None
        
        #Initialize GUI wizard pages
        self.mapping=DeclareMapping.instance()
        self.initPerson()
        
        self.initProperty()
        
        self.initSTRType()
       
        self.init_document_type()
        
        self.initSourceDocument()
        
        #self.initConflict()
        
        #Connect signal when the finish button is clicked
        btnFinish = self.button(QWizard.FinishButton)
        
    def initPerson(self):
        '''
        Initialize person config
        '''
        self.notifPerson = NotificationBar(self.vlPersonNotif)
        
        self._initPersonFilter()
        
        #Initialize person worker thread for fetching person objects
        self.personWorker = PersonWorker(self)
        self.connect(self.personWorker, SIGNAL("retrieved(PyQt_PyObject)"),self._loadPersonInfo)
        
        #Init summary tree loaders
        self.personTreeLoader = TreeSummaryLoader(self.tvPersonInfo,QApplication.translate("newSTRWiz","Party Information"))
                
        #Connect signals
        QObject.connect(self.cboPersonFilterCols, SIGNAL("currentIndexChanged(int)"),self._updatePersonCompleter)
        
        #QObject.connect(self.cboPersonFilterCols, SIGNAL("currentIndexChanged(int)"),self.dataReceieved)
        
        #Start background thread
        self.personWorker.start()
        
    def initProperty(self):
        '''
        Initialize property config
        '''
        self.notifProp = NotificationBar(self.vlPropNotif)
        self.gpOLTitle = self.gpOpenLayers.title()
        
        #Flag for checking whether OpenLayers basemaps have been loaded
        self.olLoaded = False
        
        #Initialize lookup for properties
        propertyWorker = PropertyWorker(self)
        self.connect(propertyWorker, SIGNAL("retrieved(PyQt_PyObject)"), self._onPropertiesLoaded)
        
        #Connect signals
        QObject.connect(self.gpOpenLayers, SIGNAL("toggled(bool)"), self._onEnableOLGroupbox)             
        QObject.connect(self.zoomSlider, SIGNAL("sliderReleased()"), self._onZoomChanged)
        QObject.connect(self.btnResetMap , SIGNAL("clicked()"), self._onResetMap)
        
        #Start background thread
        propertyWorker.start()   
        
        self.propBrowser = WebSpatialLoader(self.propWebView,self)
        self.connect(self.propBrowser,SIGNAL("loadError(QString)"),self._onPropertyBrowserError)
        self.connect(self.propBrowser,SIGNAL("loadProgress(int)"),self._onPropertyBrowserLoading)
        self.connect(self.propBrowser,SIGNAL("loadFinished(bool)"),self._onPropertyBrowserFinished)
        self.connect(self.propBrowser,SIGNAL("zoomChanged(int)"),self.onMapZoomLevelChanged)
            
        #Connect signals
        QObject.connect(self.rbGMaps, SIGNAL("toggled(bool)"),self.onLoadGMaps)
        QObject.connect(self.rbOSM, SIGNAL("toggled(bool)"),self.onLoadOSM)                               
            
    def initializePage(self, id):
        '''
        Initialize summary page based on user selections.
        '''
        if id == 5:
            self.buildSummary()
            
    def initSTRType(self):
        '''
        Initialize 'Social Tenure Relationship' GUI controls
        '''
        person = self.mapping.tableMapping('check_social_tenure_type')
        Person = person()
        strTypeFormatter =Person.queryObject().all()
        strType=[ids.value for ids in strTypeFormatter]
        strType.insert(0, " ")
        self.cboSTRType.insertItems(0,strType)

        self.cboSTRType.setCurrentIndex(-1)
        
        self.notifSTR = NotificationBar(self.vlSTRTypeNotif)
        
        #Register STR selection field
        self.frmWizSTRType.registerField("STR_Type",self.cboSTRType)
    
    def init_document_type(self):
        '''
        Initialize 'Right of Enjoyment' GUI controls
        '''
        doc_type_model = self.mapping.tableMapping('check_document_type')
        Docs = doc_type_model()
        doc_type_list = Docs.queryObject().all()
        doc_types = [doc.value for doc in doc_type_list]
        doc_types.insert(0," ")
        self.cboDocType.insertItems(0,doc_types)
        self.cboDocType.setCurrentIndex(-1)

        self.vlSourceDocNotif = NotificationBar(self.vlSourceDocNotif)
        
    def initSourceDocument(self):
        '''
        Initialize source document page
        '''
        #Set currency regular expression and currency prefix
        rx = QRegExp("^\\d{1,12}(([.]\\d{2})*),(\\d{2})$")
        rxValidator = QRegExpValidator(rx,self)
        '''
        '''
        self.notifSourceDoc = NotificationBar(self.vlSourceDocNotif)
        
        #Set source document manager
        self.sourceDocManager = SourceDocumentManager()
        self.sourceDocManager.registerContainer(self.vlDocTitleDeed, DEFAULT_DOCUMENT)
        self.connect(self.btnAddTitleDeed, SIGNAL("clicked()"),self.onUploadTitleDeed)

    def initConflict(self):
        '''
        Initialize 'Conflict' GUI controls
        '''
        #loadComboSelections(self.cboConflictOccurrence, CheckConflictState) 
        
        self.notifConflict = NotificationBar(self.vlConflictNotif,3000)
        
    def buildSummary(self):
        '''
        Display summary information.
        '''
        personMapping = self._mapPersonAttributes(self.selPerson)
        propertyMapping = self._mapPropertyAttributes(self.selProperty)
        STRMapping = self._mapSTRTypeSelection()
        
        #Load summary information in the tree view
        summaryTreeLoader = TreeSummaryLoader(self.twSTRSummary)
        summaryTreeLoader.addCollection(personMapping, QApplication.translate("newSTRWiz","Party Information"),
                                             ":/plugins/stdm/images/icons/user.png")    
        
        summaryTreeLoader.addCollection(propertyMapping, QApplication.translate("newSTRWiz","Spatial Unit Information"),
                                             ":/plugins/stdm/images/icons/property.png")
                                             
        summaryTreeLoader.addCollection(STRMapping, QApplication.translate("newSTRWiz","Social Tenure Relationship Information"), 
                                             ":/plugins/stdm/images/icons/social_tenure.png")    

        #Check the source documents based on the type of property
        srcDocMapping = self.sourceDocManager.attributeMapping()

        summaryTreeLoader.addCollection(srcDocMapping, QApplication.translate("newSTRWiz","Source Documents"), 
                                             ":/plugins/stdm/images/icons/attachment.png") 
      
        summaryTreeLoader.display()  
    
    def validateCurrentPage(self):
        '''
        Validate the current page before proceeding to the next one
        '''
        isValid = True
        currPageIndex = self.currentId()       
        
        #Validate person information
        if currPageIndex == 1:
            if self.selPerson == None:
                msg = QApplication.translate("newSTRWiz", 
                                             "Please choose a person for whom you are defining the social tenure relationship for.")
                self.notifPerson.clear()
                self.notifPerson.insertNotification(msg, ERROR)
                isValid = False
        
        #Validate property information
        if currPageIndex == 2:
            if self.selProperty == None:
                    msg = QApplication.translate("newSTRWiz", 
                                                 "Please specify the property to reference. Use the filter capability below.")
                    self.notifProp.clear()
                    self.notifProp.insertNotification(msg, ERROR)
                    isValid = False
        
        #Validate STR   
        if currPageIndex == 3:
            #Get current selected index
            currIndex = self.cboSTRType.currentIndex()
            if currIndex ==-1:
                msg = QApplication.translate("newSTRWiz", 
                                                 "Please specify the social tenure relationship type.")     
                self.notifSTR.clear()
                self.notifSTR.insertErrorNotification(msg)
                isValid = False

        #Validate source document    
        if currPageIndex == 4:
            currIndex = self.cboDocType.currentIndex()
            if currIndex ==-1:
                msg = QApplication.translate("newSTRWiz",
                                                 "Please select document type from the list")
                self.notifSourceDoc.clear()
                self.notifSourceDoc.insertErrorNotification(msg)

        if currPageIndex == 5:
            isValid = self.onCreateSTR()
        return isValid
    
    def onCreateSTR(self):
        '''
        Slot raised when the user clicks on Finish button in order to create a new STR entry.
        '''
        isValid = True
        
        #Create a progress dialog
        progDialog = QProgressDialog(self)
        progDialog.setWindowTitle(QApplication.translate("newSTRWiz", "Creating New STR"))
        progDialog.setRange(0, 7)
        progDialog.show()

        socialTenureRel = self.mapping.tableMapping('social_tenure_relationship')
        str_relation_table = self.mapping.tableMapping('str_relations')
        STR_relation = str_relation_table()

        try:
            progDialog.setValue(1)
            socialTenure = socialTenureRel()
            socialTenure.party = self.selPerson.id
            progDialog.setValue(2)
            socialTenure.spatial_unit = self.selProperty.id
            progDialog.setValue(3)
            
            socialTenure.social_tenure_type = unicode(self.cboSTRType.currentText())
            progDialog.setValue(6)

            """
            Save new STR relations and supporting documentation
            """
            socialTenure.save()
            model_objs = self.sourceDocManager.model_objects()

            if len(model_objs) > 0:
                for model_obj in model_objs:
                    model_obj.save()
                    STR_relation.social_tenure_id = socialTenure.id
                    STR_relation.source_doc_id = model_obj.id
                    STR_relation.save()

            progDialog.setValue(7)

            strMsg = unicode(QApplication.translate("newSTRWiz",
                                            "The social tenure relationship has been successfully created!"))
            QMessageBox.information(self, QApplication.translate("newSTRWiz", "STR Creation"),
                                    strMsg)

        except sqlalchemy.exc.OperationalError as oe:
            errMsg = oe.message
            QMessageBox.critical(self, QApplication.translate("newSTRWiz", "Unexpected Error"),
                                 errMsg)
            progDialog.hide()
            isValid = False

        except sqlalchemy.exc.IntegrityError as ie:
            errMsg = ie.message
            QMessageBox.critical(self, QApplication.translate("newSTRWiz", "Duplicate Relationship Error"),errMsg)
            progDialog.hide()
            isValid = False
            
        except Exception as e:
            errMsg = str(e)
            QMessageBox.critical(self, QApplication.translate("newSTRWiz", "Unexpected Error"),errMsg)
            
            isValid = False
        finally:
            STDMDb.instance().session.rollback()
            progDialog.hide()

        return isValid
            
    def _loadPersonInfo(self,persons):
        '''
        Load person objects
        '''
        self.persons = persons 
        self._updatePersonCompleter(0)
        
    def _onPropertiesLoaded(self,propids):
        '''
        Slot raised once the property worker has finished retrieving the property IDs.
        Creates a completer and populates it with the property IDs.
        '''
        #Get the items in a tuple and put them in a list
        
        propertyIds = [str(pid[0]) for pid in propids]
       
        #Configure completer   
        propCompleter = QCompleter(propertyIds,self)         
        propCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        propCompleter.setCompletionMode(QCompleter.PopupCompletion)
        self.txtPropID.setCompleter(propCompleter)  
        
        #Connect 'activated' slot for the completer to load property information
        self.connect(propCompleter, SIGNAL("activated(const QString&)"),self._updatePropertySummary)      
        
    def _onPropertyBrowserError(self,err):
        '''
        Slot raised when an error occurs when loading items in the property browser
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
            self.gpOpenLayers.setTitle("%s (Loading...%s%%)"%(str(self.gpOLTitle),str(progress)))
            
    def _onPropertyBrowserFinished(self,status):
        '''
        Slot raised when the property browser finishes loading the content
        '''
        if status:
            self.olLoaded = True
            self.overlayProperty()
        else:
            self.notifProp.clear()
            msg = QApplication.translate("newSTRWiz", "Error - The property map cannot be loaded.")   
            self.notifProp.insertErrorNotification(msg)
        
    def _onEnableOLGroupbox(self,state):
        '''
        Slot raised when a user chooses to select the group box for enabling/disabling to view
        the property in OpenLayers.
        '''
        if state:
            if self.selProperty is None:
                self.notifProp.clear()
                msg = QApplication.translate("newSTRWiz", "You need to specify a property in order to be able to preview it.")   
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
        This is only raised once the user releases the slider with the mouse.
        '''
        zoom = self.zoomSlider.value()        
        self.propBrowser.zoom_to_level(zoom)
            
    def _initPersonFilter(self):
        '''
        Initializes person filter settings
        '''

        cols=table_searchable_cols('party')
        if len(cols)>0:
            for col in cols:
                self.cboPersonFilterCols.addItem(str(QApplication.translate("newSTRWiz",col.replace('_',' ').title())), col)
        
    def _updatePersonCompleter(self,index):
        '''
        Updates the person completer based on the person attribute item that the user has selected
        '''
        #Clear dependent controls
        #self.txtFilterPattern.clear()
        self.cboFilterPattern.clear()
        self.tvPersonInfo.clear()
        try:
            field_name = self.cboPersonFilterCols.currentText().replace(" ","_").lower()
            data_list =[getattr(array,field_name) for array in self.persons if getattr(array,field_name)!=None]
            model =QCompleter(data_list)
            model.setCompletionMode(QCompleter.PopupCompletion)
            model.setCaseSensitivity(Qt.CaseInsensitive)
            self.cboFilterPattern.setCompleter(model)
            self.cboFilterPattern.showPopup()
        except Exception as ex:
            msg =ex.message
            QMessageBox.critical(self,QApplication.translate("SocialTenureRelationship", u"Error Loading values"),
                                 QApplication.translate("SocialTenureRelationship",
                                 u"The was an error in sorting the data with the given column, try another %s"%msg))
            return
        self.currPersonAttr = str(self.cboPersonFilterCols.itemData(index))            
        
        #Create standard model which will always contain the id of the person row then the attribute for use in the completer
        self.cboFilterPattern.addItem("")
        for p in self.persons:
            pVal = getattr(p,self.currPersonAttr)
            if pVal != "" or pVal != None:
                self.cboFilterPattern.addItem(pVal,p.id)

        self.cboFilterPattern.activated.connect(self._updatePersonSummary)
         #self.connect(self.cboFilterPattern, SIGNAL("currentIndexChanged(int)"),self._updatePersonSummary)
                
    def _updatePersonSummary(self,index):
        '''
        Slot for updating the person information into the tree widget based on the user-selected value
        '''
        Person=self.mapping.tableMapping('party')
        person=Person()
        #Get the id from the model then the value of the ID model index



        index =self.cboFilterPattern.currentIndex()
        personId = self.cboFilterPattern.itemData(index)
        #QMessageBox.information(None,'index',str(data))
        # personId = pData
        if personId is not None:
        #Get person info
            p = person.queryObject().filter(Person.id == str(personId)).first()
            if p:
                self.selPerson = p
                personInfoMapping = self._mapPersonAttributes(p)
                personTreeLoader = TreeSummaryLoader(self.tvPersonInfo)
                personTreeLoader.addCollection(personInfoMapping, QApplication.translate("newSTRWiz","Party Information"),
                                               ":/plugins/stdm/images/icons/user.png")
                personTreeLoader.display()
            
    def _mapPersonAttributes(self,person):
        '''
        Maps the attributes of a person to a more friendly user representation 
        '''   
        #Setup formatters        
        pmapper=self.mapping.tableMapping('party')
        colMapping = pmapper.displayMapping()
        colMapping.pop('id')
        pMapping=OrderedDict()
        try:
            for attrib,label in colMapping.iteritems():
                pMapping[label] = getattr(person,attrib)
        except:
            pass
#                             
        return pMapping  
    
    def _updatePropertySummary(self,propid):
        '''
        Update the summary information for the selected property
        '''
        property = self.mapping.tableMapping('spatial_unit')
        Property =property()
        #propty=Table('spatial_unit',Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
        #session=STDMDb.instance().session
        prop =Property.queryObject().filter(property.code == unicode(propid)).first()
        if prop:
            propMapping = self._mapPropertyAttributes(prop)
            
            #Load information in the tree view
            propertyTreeLoader = TreeSummaryLoader(self.tvPropInfo)
            propertyTreeLoader.addCollection(propMapping, QApplication.translate("newSTRWiz","Spatial Unit Information"),
                                             ":/plugins/stdm/images/icons/property.png")       
            propertyTreeLoader.display()  
            
            self.selProperty = prop
            
            #Show property in OpenLayers
            if self.gpOpenLayers.isChecked():
                if self.olLoaded:
                    self.overlayProperty()                      
    
    def _mapPropertyAttributes(self,prop):
            #Configure formatters
            spMapper = self.mapping.tableMapping('spatial_unit')
            colMapping = spMapper.displayMapping()
            colMapping.pop('id')
            propMapping=OrderedDict()
            for attrib,label in colMapping.iteritems():
                propMapping[label] = getattr(prop,attrib)
            return propMapping
        
    def _mapSTRTypeSelection(self):
        #strTypeFormatter = LookupFormatter(CheckSocialTenureRelationship)
        #self.cboSTRType.clear()
        
        strTypeSelection=self.cboSTRType.currentText()
        
        strMapping = OrderedDict()
        strMapping[str(QApplication.translate("newSTRWiz","STR Type"))] = str(strTypeSelection)

        return strMapping
    
    def _mapEnjoyRightSelection(self,enjoyRight):
        deadAliveFormatter = LookupFormatter(CheckDeadAlive)
        inheritanceFormatter = LookupFormatter(CheckInheritanceType)
                
        enjoyRightMapping = OrderedDict()
        enjoyRightMapping[str(QApplication.translate("newSTRWiz","Inheritance From"))] = str(inheritanceFormatter.setDisplay(enjoyRight.InheritanceType).toString())
        enjoyRightMapping[str(QApplication.translate("newSTRWiz","State"))] = str(deadAliveFormatter.setDisplay(enjoyRight.State).toString())
        enjoyRightMapping[str(QApplication.translate("newSTRWiz","Receiving Date"))] = str(enjoyRight.ReceivingDate.year)
        
        return enjoyRightMapping
    
    def _mapPrivatePropertyTax(self):
        privateTaxMapping = OrderedDict()
        
        privateTaxMapping[str(QApplication.translate("newSTRWiz","CFPB Payment Year"))] = str(self.dtLastYearCFBP.date().toPyDate().year)
        
        taxDec = Decimal(str(self.txtCFBPAmount.text()))
        taxFormatted = moneyfmt(taxDec,curr = CURRENCY_CODE)
        privateTaxMapping[str(QApplication.translate("newSTRWiz","CFPB Amount"))] = taxFormatted
        
        return privateTaxMapping
    
    def _mapStatePropertyTax(self):
        stateTaxMapping = OrderedDict()
        
        stateTaxMapping[str(QApplication.translate("newSTRWiz","Latest Receipt Date"))] = str(self.dtStateReceiptDate.date().toPyDate())
        
        taxDec = Decimal(str(self.txtStateReceiptAmount.text()))
        taxFormatted = moneyfmt(taxDec,curr = CURRENCY_CODE)
        stateTaxMapping[str(QApplication.translate("newSTRWiz","Amount"))] = taxFormatted
        stateTaxMapping[str(QApplication.translate("newSTRWiz","Lease Starting Year"))] = str(self.dtStateLeaseYear.date().toPyDate().year)
        stateTaxMapping[str(QApplication.translate("newSTRWiz","Tax Office"))] = str(self.txtStateTaxOffice.text())
        
        return stateTaxMapping
    
    def _mapConflict(self,conflict):
        conflictFormatter = LookupFormatter(CheckConflictState)
        conflictMapping = OrderedDict()
        
        if conflict == None:
            return conflictMapping
        
        conflictMapping[str(QApplication.translate("newSTRWiz","Status"))] = str(conflictFormatter.setDisplay(conflict.StateID).toString())
        
        if conflict.Description:
            conflictMapping[str(QApplication.translate("newSTRWiz","Description"))] = conflict.Description
            
        if conflict.Solution:
            conflictMapping[str(QApplication.translate("newSTRWiz","Solution"))] = conflict.Solution
         
        return conflictMapping
    
    def onLoadGMaps(self,state):
        '''
        Slot raised when a user clicks to set Google Maps Satellite
        as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(GMAP_SATELLITE)
        
    def onLoadOSM(self,state):
        '''
        Slot raised when a user clicks to set OSM as the base layer
        '''
        if state:                     
            self.propBrowser.setBaseLayer(OSM)
            
    def onMapZoomLevelChanged(self,level):
        '''
        Slot which is raised when the zoom level of the map changes.
        '''
        self.zoomSlider.setValue(level)
       
    def _onResetMap(self):
        '''
        Slot raised when the user clicks to reset the property
        location in the map.
        '''
        self.propBrowser.zoom_to_extents()
       
    def overlayProperty(self):
        '''
        Overlay property boundaries on the basemap imagery
        '''                    
        self.propBrowser.add_overlay(self.selProperty,'geom_polygon')
        
    def validateEnjoymentRight(self): 
        '''
        Validate whether the user has specified all the required information
        '''
        self.notifEnjoyment.clear()
        
        if self.cboDeadAlive.currentIndex() == 0:
            msg = QApplication.translate("newSTRWiz", 
                                             "Please specify whether the person is 'Dead' or 'Alive'.")
            self.notifEnjoyment.insertErrorNotification(msg)
            return False
        
        if self.cboInheritanceType.currentIndex() == 0:
            msg = QApplication.translate("newSTRWiz", 
                                             "Please specify the Inheritance Type.")
            self.notifEnjoyment.insertErrorNotification(msg)
            return False
        
        #Set the right of enjoyment details if both inheritance type and state have been defined
        if self.cboInheritanceType.currentIndex() != 0 and self.cboDeadAlive.currentIndex() != 0:
            eRight = EnjoymentRight()
            #Set the properties
            setModelAttrFromCombo(eRight,"InheritanceType",self.cboInheritanceType)
            setModelAttrFromCombo(eRight,"State",self.cboDeadAlive)
            eRight.ReceivingDate = self.dtReceivingDate.date().toPyDate()
            
            self.enjoymentRight = eRight
            
            return True
        
    def validateSourceDocuments(self):
        '''
        Basically validates the entry of tax information.
        '''
        isValid = True
        
        if self.rbPrivateProperty.isChecked():
            if self.gpPrivateTaxInfo.isChecked():
                self.notifSourceDoc.clear()
                if str(self.txtCFBPAmount.text()) == "": 
                    self.txtCFBPAmount.setFocus()
                    msg1 = QApplication.translate("newSTRWiz", 
                                             "Please enter the tax amount.")
                    self.notifSourceDoc.insertErrorNotification(msg1)
                    isValid = False
                    
        elif self.rbStateland.isChecked():
            self.notifSourceDoc.clear()
            if str(self.txtStateReceiptAmount.text()) == "": 
                    self.txtStateReceiptAmount.setFocus()
                    msg2 = QApplication.translate("newSTRWiz", 
                                             "Please enter the tax amount.")
                    self.notifSourceDoc.insertErrorNotification(msg2)
                    isValid = False
            if str(self.txtStateTaxOffice.text()) == "": 
                    self.txtStateTaxOffice.setFocus()
                    msg3 = QApplication.translate("newSTRWiz", 
                                             "Please specify the tax office.")
                    self.notifSourceDoc.insertErrorNotification(msg3)
                    isValid = False
   
        return isValid
    
    def validateConflict(self): 
        '''
        Check if the user has selected that there is a conflict and validate whether the description 
        and solution have been specified.
        '''
        isValid = True
        
        nonConflict = QApplication.translate("Lookup","No Conflict")
        nonConflictIndex = self.cboConflictOccurrence.findText(nonConflict)
        conflictOccurrence = QApplication.translate("Lookup","Conflict Present")
        occIndex = self.cboConflictOccurrence.findText(conflictOccurrence)
        
        if self.cboConflictOccurrence.currentIndex() == occIndex:
            self.notifConflict.clear()
            if str(self.txtConflictDescription.toPlainText()) == "":
                msg1 = QApplication.translate("newSTRWiz", 
                                             "Please provide a brief description of the conflict.")
                self.notifConflict.insertErrorNotification(msg1)
                isValid = False
            if str(self.txtConflictSolution.toPlainText()) == "":
                msg2 = QApplication.translate("newSTRWiz", 
                                             "Please provide a proposed solution for the specified conflict.")
                self.notifConflict.insertErrorNotification(msg2)
                isValid = False
                
            if str(self.txtConflictSolution.toPlainText()) != "" and str(self.txtConflictDescription.toPlainText()) != "":
                self.conflict = Conflict()
                stateId,ok = self.cboConflictOccurrence.itemData(occIndex).toInt()
                self.conflict.StateID = stateId
                self.conflict.Description = str(self.txtConflictDescription.toPlainText())
                self.conflict.Solution = str(self.txtConflictSolution.toPlainText())
                
        #Set conflict object properties
        if self.cboConflictOccurrence.currentIndex() == nonConflictIndex:
            self.conflict = Conflict()
            stateId,ok = self.cboConflictOccurrence.itemData(nonConflictIndex).toInt()
            self.conflict.StateID = stateId
   
        return isValid
    
    def onSelectPrivateProperty(self,state):
        '''
        Slot raised when the user clicks to load source document page for private property
        '''
        if state:
            self.stkSrcDocList.setCurrentIndex(0)
        
    def onSelectStateland(self,state):
        '''
        Slot raised when the user clicks to load source document page for private property
        '''
        if state:
            self.stkSrcDocList.setCurrentIndex(1)
            
    def onUploadTitleDeed(self):
        '''
        Slot raised when the user clicks to upload a title deed
        '''
        titleStr = QApplication.translate("newSTRWiz", 
                                             "Specify the Document File Location")
        titles = self.selectSourceDocumentDialog(titleStr)
        
        for title in titles:
            self.sourceDocManager.insertDocumentFromFile(title,DEFAULT_DOCUMENT)
            
    def onUploadStatutoryRefPaper(self):
        '''
        Slot raised when the user clicks to upload a statutory reference paper
        '''
        statStr = QApplication.translate("newSTRWiz", 
                                             "Specify Statutory Reference Paper File Location")
        stats = self.selectSourceDocumentDialog(statStr)
        
        for stat in stats:
            self.sourceDocManager.insertDocumentFromFile(stat,STATUTORY_REF_PAPER)
            
    def onUploadSurveyorRef(self):
        '''
        Slot raised when the user clicks to upload a surveyor reference
        '''
        surveyorStr = QApplication.translate("newSTRWiz", 
                                             "Specify Surveyor Reference File Location")
        surveyorRefs = self.selectSourceDocumentDialog(surveyorStr)
        
        for surveyorRef in surveyorRefs:
            self.sourceDocManager.insertDocumentFromFile(surveyorRef,SURVEYOR_REF)
            
    def onUploadNotaryRef(self):
        '''
        Slot raised when the user clicks to upload a notary reference
        '''
        notaryStr = QApplication.translate("newSTRWiz", 
                                             "Specify Notary Reference File Location")
        notaryRefs = self.selectSourceDocumentDialog(notaryStr)
        
        for notaryRef in notaryRefs:
            self.sourceDocManager.insertDocumentFromFile(notaryRef,NOTARY_REF)

    def validateReceiptScanInsertion(self,documentmanager,scan,containerid):
        '''
        Checks and ensures that only one document exists in the specified container.
        '''
        container = documentmanager.container(containerid)
        if container.count() > 0:
            msg = QApplication.translate("newSTRWiz", "Only one receipt scan can be uploaded.\nWould you like to replace " \
                                         "the existing one?")
            result = QMessageBox.warning(self,QApplication.translate("newSTRWiz","Replace Receipt Scan"),msg, QMessageBox.Yes|
                                         QMessageBox.No)
            if result == QMessageBox.Yes:
                docWidget = container.itemAt(0).widget()
                docWidget.removeDocument()
                documentmanager.insertDocumentFromFile(scan,containerid)
            else:
                return
        else:
            documentmanager.insertDocumentFromFile(scan,containerid)
        
    def selectSourceDocumentDialog(self,title):
        '''
        Displays a file dialog for a user to specify a source document
        '''
        files = QFileDialog.getOpenFileNames(self,title,"/home","Source "
                                                                "Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)")
        return files
        
    def uploadDocument(self,path,containerid):
        '''
        Upload source document
        '''
        self.sourceDocManager.insertDocumentFromFile(path, containerid)
            
class PersonWorker(QThread):
    '''
    Worker thread for loading person objects into a list
    '''
    def __init__(self,parent = None):
        QThread.__init__(self,parent)
        
    def run(self):
        '''
        Fetch person objects from the database
        '''        
        self.mapping=DeclareMapping.instance()
        Person=self.mapping.tableMapping('party')
        p = Person()
        persons = p.queryObject().all()
        self.emit(SIGNAL("retrieved(PyQt_PyObject)"),persons)
        
class PropertyWorker(QThread):
    '''
    Thread for loading property IDs for use in the completer
    '''
    def __init__(self,parent = None):
        QThread.__init__(self,parent)
        
    def run(self):
        '''
        Fetch property IDs from the database
        '''
        pty=Table('spatial_unit',Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
        session=STDMDb.instance().session
        properties =session.query(pty.c.code).all()
        #pty = Property()

        #properties = pty.queryObject([Property.spatial_unit_id]).all()      
        self.emit(SIGNAL("retrieved(PyQt_PyObject)"), properties)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
