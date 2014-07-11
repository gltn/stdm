"""
/***************************************************************************
Name                 : STDM Data Models and SQLAlchemy Database Configuration 
Description          : -Contains STDM data models
                       -Manages SQLAlchemy core objects for connecting to the 
                        database using the singleton pattern
Date                 : 28/May/2013 
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
from datetime import date
from collections import OrderedDict

from PyQt4.QtGui import QApplication

from sqlalchemy import create_engine, ForeignKey,Table ,event,func, MetaData
from sqlalchemy import Column, Date, Integer, String ,Numeric,Text,Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Sequence
from geoalchemy2 import Geometry

import stdm.data

metadata=MetaData()
Base = declarative_base(metadata=metadata)


class Singleton(object):
    '''
    Singleton class
    '''
    def __init__(self,decorated):
        self.__decorated = decorated
        
    def instance(self,*args,**kwargs):
        '''
        Returns an instance of the decorated object or creates 
        one if it does not exist
        '''
        try:
            return self._instance
        #Catch null property exception and create a new instance of the class
        except AttributeError:
            self._instance = self.__decorated(*args,**kwargs)
            return self._instance
        
    def __call__(self,*args,**kwargs):
        raise TypeError('Singleton must be accessed through the instance method')
    
    def cleanUp(self):
        '''
        Remove the instance of the referenced singleton class
        '''
        del self._instance        
    
@Singleton
class STDMDb(object):
    
    '''
    This class will exist only once hence the reason it has a singleton attribute.
    It will contain the session for managing the unit of work for each class.        
    '''
    engine = None
    session = None
    
    def __init__(self):
        #Initialize database engine
        self.engine = create_engine(stdm.data.app_dbconn.toAlchemyConnection(), echo = False)       
        Session = sessionmaker(bind = self.engine)
        self.session = Session() 
        Base.metadata.create_all(self.engine)
        #Base.metadata=metadata
        #metadata.reflect(bind=self.engine)
        
    def createMetadata(self):
        '''
        Creates STDM database schema
        '''
        Base.metadata.create_all(self.engine)
            
    def instance(self,*args,**kwargs):
        '''
        Dummy method. Eclipse IDE cannot handle the Singleton decorator in Python
        '''
        pass
        
class Model(object):
    '''
    Base class that handles all basic database operations.
    All STDM entities that need to be persisted in the database
    will inherit from this class.
    '''
    attrTranslations = OrderedDict()
    
    def save(self):            
        db = STDMDb.instance()
        db.session.add(self)
        db.session.commit()
            
    def saveMany(self,objects = []):
        '''
        Save multiple objects of the same type in one go.
        '''
        db = STDMDb.instance()
        db.session.add_all(objects)
        db.session.commit()
            
    def update(self):
        db = STDMDb.instance()
        db.session.commit()
            
    def delete(self):
        db = STDMDb.instance()
        db.session.delete(self)
        db.session.commit()
        
    def queryObject(self,args=[]):
        '''
        The 'args' specifies the attributes/columns that will be returned in the query in a tuple;
        Else, the full model object will be returned.
        '''
        db = STDMDb.instance()
        #raise NameError(str(self.__class__))
        if len(args) == 0:            
            return db.session.query(self.__class__)
        
        else:
            return db.session.query(*args)
    
    @classmethod  
    def tr(cls,propname):
        '''
        Returns a user-friendly name for the given property name.
        :param propname: Property name.
        '''
        if propname in cls.attrTranslations:
            return cls.attrTranslations[propname]
        else:
            return None
    
    @staticmethod
    def displayMapping():
        '''
        Returns the dictionary containing the translation mapping for the attributes.
        Base classes need to implement this method.
        
        if len(Model.attrTranslations) == 0:
            raise NotImplementedError
        else:
        '''
        return Model.attrTranslations
    
class LookupBase(object):
    '''
    Base class for all lookup objects.
    '''
    id  = Column(Integer,primary_key = True)
    name = Column(String(50))


                        
class Content(Model,Base):
    '''
    Abstract class which is implemented by contents items that need to be registered based
    on the scope of the particular instance of STDM customization.    
    '''
    __tablename__ = "content_base"
    id = Column(Integer,primary_key = True)
    name = Column(String(100), unique = True)
    code = Column(String(100),unique = True) 
    roles = relationship("Role", secondary = "content_roles", backref = "contents")  
    
class Role(Model,Base):
    '''
    Model for the database-wide system roles. These are manually synced with the roles in the
    system catalog.
    '''
    __tablename__ = "role"
    id = Column(Integer,primary_key =True)
    name = Column(String(100), unique = True)
    description = Column(String)

#Table for mapping the many-to-many association of content item to system roles  
content_roles_table = Table("content_roles", Base.metadata,
                            Column('content_base_id',Integer, ForeignKey('content_base.id'), primary_key = True),
                            Column('role_id',Integer, ForeignKey('role.id'), primary_key = True)
                            )

class AdminSpatialUnitSet(Model,Base):
    '''
    Hierarchy of administrative units.
    '''
    __tablename__ = "admin_spatial_unit_set"
    id = Column(Integer,primary_key=True)
    ParentID = Column("parent_id",Integer,ForeignKey("admin_spatial_unit_set.id"))
    Name = Column("name",String(50))
    Code = Column("code",String(10))
    Children = relationship("AdminSpatialUnitSet",backref=backref("Parent",remote_side=[id]),
                            cascade = "all, delete-orphan")
    
    def __init__(self,name="",code="",parent=None):
        self.Name = name
        self.Code = code
        self.Parent = parent
        
    def hierarchyCode(self,separator = "/"):
        '''
        Returns a string constituted of codes aggregated from the class instance, prior to which
        there are codes of the parent administrative units in the hierarchy.
        '''
        codeList = []
        codeList.append(self.Code)
        
        parent = self.Parent        
        while parent != None:
            codeList.append(parent.Code)
            parent = parent.Parent
            
        #Reverse the items so that the last item added becomes the prefix of the hierarchy code
        reverseCode = list(reversed(codeList))
            
        return separator.join(reverseCode)

        
class Enumerator(Model,Base):
    '''
    Enumerator model configuration.
    No additional attributes from the ones in person base class.
    '''
    __tablename__ = "enumerator"
    id = Column(Integer,primary_key = True)
    Surveys = relationship("Survey",backref="Enumerator")  
    
class Witness(Model,Base):
    '''
    Questionnaire respondent witness.
    '''
    __tablename__ = "witness"
    id = Column(Integer,primary_key = True)
    RelationshipID = Column("relationship_id",Integer)
    OtherRelationship = Column("other_relationship",String(50))
    SurveyID = Column("survey_id",Integer,ForeignKey('survey.id'))
    
    @staticmethod
    def displayMapping():
        '''
        Base class override.
        Returns the dictionary containing the translation mapping for the attributes.
        '''
        #baseAttrTranslations = BasePersonMixin.displayMapping()
        baseAttrTranslations["RelationshipID"] = QApplication.translate("DatabaseMapping","Relationship") 
        baseAttrTranslations["OtherRelationship"] = QApplication.translate("DatabaseMapping","Other Relationship") 
        
        return baseAttrTranslations
    
class Survey(Model,Base):
    '''
    Metadata about the questionnaire interview process.
    '''
    __tablename__ = "survey"
    id = Column(Integer,primary_key = True)
    Code = Column("code",String(20))
    EnumerationDate = Column("enumeration_date",Date)  
    EnumeratorID = Column("enumerator_id",Integer,ForeignKey('enumerator.id'))
    Witnesses = relationship("Witness",backref="Survey",cascade="all, delete-orphan")
    #RespondentID = Column("respondent_id",Integer,ForeignKey('respondent.id'))
    #Respondent = relationship("Respondent",uselist = False,single_parent = True,cascade = "all, delete-orphan")
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["Code"] = QApplication.translate("DatabaseMapping","Code") 
        attrTranslations["EnumerationDate"] = QApplication.translate("DatabaseMapping","Enumeration Date")
        attrTranslations["EnumeratorID"] = QApplication.translate("DatabaseMapping","Enumerator")
        #attrTranslations["RespondentID"] = QApplication.translate("DatabaseMapping","Respondent")
        
        return attrTranslations
   
class SupportsRankingMixin(object):
    '''
    Mixin item for classes that supporting ranking of items for a farmer. 
    '''
    id = Column(Integer,primary_key=True)
    Rank = Column("rank",Integer)
    OtherItem = Column("other_item",String(30))
#     
#     @declared_attr
#     def FarmerID(cls):
#         return Column("farmer_id",Integer,ForeignKey("farmer.id"))
#     
class Priority(SupportsRankingMixin,Model,Base):
    '''
    Priority tools and services as identified by a farmer.
    '''
    __tablename__ = "priority"
    itemID = Column("item_id",Integer)
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["itemID"] = QApplication.translate("DatabaseMapping","Priority Service") 
        attrTranslations["OtherItem"] = QApplication.translate("DatabaseMapping","Other Service")
        attrTranslations["Rank"] = QApplication.translate("DatabaseMapping","Rank")
        
        return attrTranslations

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


            
            
            
            
            
            
        
        
        
        
        
