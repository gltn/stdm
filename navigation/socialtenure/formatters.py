"""
/***************************************************************************
Name                 : STR Formatters
Description          : Module that provides formatters for defining how 
                       social tenure relationship information is represented
                       in the tree view.
                       the 
Date                 : 11/November/2013 
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
from PyQt4.QtGui import QApplication

from nodes import BaseSTRNode, PersonNode, NoSTRNode, STRNode, PropertyNode,\
ConflictNode,TaxationNode

class STRNodeFormatter(object):
    '''
    Base class for all STR formatters.
    '''
    def __init__(self,headers,treeview = None,parentwidget = None):
        self._headers = headers
        self._data = []     
        
        self.rootNode = BaseSTRNode(headers,view = treeview,parentWidget = parentwidget)
        
    def setData(self,data):
        '''
        Set the data to be formatted through the nodes.
        '''
        self._data = data
        
    def headerData(self):
        '''
        Header labels.
        '''
        return self._headers
    
    def setNoSTRDefined(self,parentNode):
        '''
        Sets the child node of the specified node to represent no social tenure relationship defined.
        These (methods for rendering nodes) are helper methods but the calling object is free to use
        custom methods for rendering child nodes.
        '''
        noSTRNode = NoSTRNode(parentNode)
        
        return noSTRNode
    
    def setSTRNodeChild(self,strobj,parentnode):
        '''
        Creates a new STRNode based on the properties of 'strobj' and adds it as a child to the 'parentnode'.
        '''
        strNode = STRNode(strobj,parentnode)
        
        return strNode
    
    def setPropertyNodeChild(self,property,parentnode):
        '''
        Creates a new PropertyNode based on the properties of 'property' and adds it as a child to the 'parentnode'.
        '''
        propNode = PropertyNode(property,parentnode,isChild = True)
        
        return propNode
    
    def setConflictNodeChild(self,conflict,parentnode):
        '''
        Creates a new ConflictNode based on the properties of 'conflict' and adds it as a child to the 'parentnode'.
        '''
        conflictNode = ConflictNode(conflict,parentnode)
        
        return conflictNode
    
    def setTaxationNodeChild(self,taxation,parentnode):
        '''
        Creates a new TaxationNode and adds it as a child to the 'parentnode'.
        '''
        taxNode = TaxationNode(taxation,parentnode)
        
        return taxNode
    
    def isSTRDefined(self,strobject,node,insertNoSTRNode=True):
        '''
        Asserts whether the STR has been defined for the specified object. The method uses the 'backref' sqlalchemy
        relationship of the social tenure relationship entity.
        '''
        noSTRNode = None
        strModel = self.socialTenureModel(strobject)
        
        if strModel is None and insertNoSTRNode:
            noSTRNode = self.setNoSTRDefined(node)     
        
        return strModel,noSTRNode
    
    def socialTenureModel(self,strobject):
        '''
        Return the social tenure relationship object for the participating model. 
        If not then returns 'None'.
        The method uses the 'backref' sqlalchemy relationship of the social tenure relationship entity.
        '''
        relationshipName = "social_tenure"
        
        if hasattr(strobject,relationshipName):
            sModel = getattr(strobject,relationshipName)
            
            #TODO: Fix the config of sqlalchemy so that lists are not used for backrefs when defining relationships
            try:
                return sModel[0]
            except IndexError:
                return None
           
        return None
        
    def root(self):
        '''
        To be implemented by subclasses.
        Should return an object of type 'stdm.navigation.BaseSTRNode'
        '''
        raise NotImplementedError(QApplication.translate("STRFormatterBase",
                                                         "Method can only be referenced by subclasses"))
        
class PersonNodeFormatter(STRNodeFormatter):
    '''
    For rendering person information as the root node of each STR item.
    '''
    def __init__(self,treeview = None,parentwidget = None):
        '''
        Initialize header labels then call base class constructor.
        '''
        headerLabels = [
                        QApplication.translate("STRPersonFormatter","First Name"),
                        QApplication.translate("STRPersonFormatter","Last Name"),
                        QApplication.translate("STRPersonFormatter","ID Number")
                        ]
        
        super(PersonNodeFormatter,self).__init__(headerLabels,treeview,parentwidget)
        
    def root(self):
        '''
        Implementation of base class method.
        '''
        for p in self._data:
            pNode = PersonNode(self._extractPersonInfo(p),self.rootNode)
            
            '''
            Check if an STR relationship has been defined for the person object and set node to indicate NoSTR
            if it has not been defined.
            '''
            strModel,noSTRNode = self.isSTRDefined(p, pNode)
            
            if strModel:
                #Define additional STR nodes that describe the STR in detail
                self.setSTRNodeChild(strModel, pNode)
                self.setPropertyNodeChild(strModel.Property, pNode)
                if isinstance(strModel.Conflict,Conflict):
                    self.setConflictNodeChild(strModel.Conflict, pNode)
                if isinstance(strModel.Taxation,Taxation):
                    self.setTaxationNodeChild(strModel.Taxation, pNode)
            
        return self.rootNode
    
    def _extractPersonInfo(self,person):
        '''
        Extracts the person data in the same order as defined in the header labels.
        '''
        personInfo = []
        personInfo.append(person.firstname)
        personInfo.append(person.lastname)
        personInfo.append(person.identification_number)
        
        return personInfo
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    