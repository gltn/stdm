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

from sqlalchemy import create_engine, ForeignKey,Table ,event,func
from sqlalchemy import Column, Date, Integer, String ,Numeric,Text,Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Sequence
from geoalchemy2 import Geometry

import stdm.data

Base = declarative_base()

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
        '''
        raise NotImplementedError
    
class LookupBase(object):
    '''
    Base class for all lookup objects.
    '''
    id  = Column(Integer,primary_key = True)
    name = Column(String(50))

class CheckGender(LookupBase,Model,Base):
    '''
    Stores gender information
    '''
    __tablename__ = 'check_gender'
    
class CheckMaritalStatus(LookupBase,Model,Base):
    '''
    Stores marital status information
    '''
    __tablename__ = 'check_marital_status'
    
class CheckRespondentType(LookupBase,Model,Base):
    '''
    Enumeration for the type of the questionnaire respondent.
    '''
    __tablename__ = 'check_respondent_type'
    
class CheckSocialTenureRelationship(LookupBase,Model,Base):
    '''
    Enumeration for the type of social tenure relationship
    '''
    __tablename__ = 'check_social_tenure_relationship'
    
class CheckWitnessRelationship(LookupBase,Model,Base):
    '''
    Witness relationship enumeration.
    '''
    __tablename__ = 'check_witness_relationship'
    
class CheckHouseUseType(LookupBase,Model,Base):
    '''
    House use type enumeration.
    '''
    __tablename__ = 'check_house_use_type'
    
class CheckLandType(LookupBase,Model,Base):
    '''
    Land type enumeration.
    '''
    __tablename__ = 'check_land_type'
    
class CheckHouseType(LookupBase,Model,Base):
    '''
    House type enumeration.
    '''
    __tablename__ = 'check_house_type'
    
class CheckSavingsOption(LookupBase,Model,Base):
    '''
    Household savings enumeration.
    '''
    __tablename__ = 'check_household_savings'
    
class CheckFoodCropCategory(LookupBase,Model,Base):
    '''
    Food crop categories.
    '''
    __tablename__ = 'check_food_crop_category'
    
class CheckInputService(LookupBase,Model,Base):
    '''
    Types of inputs required by farmers.
    '''
    __tablename__ = 'check_input_service'
    
class CheckSocioEconomicImpact(LookupBase,Model,Base):
    '''
    Socio-economic impact types.
    '''
    __tablename__ = 'check_socio_economic_impact'
                        
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

class BasePersonMixin(object):
    '''
    Mixin class for person entity.
    '''
    FirstName = Column("first_name",String(50))
    LastName = Column("last_name",String(50))
    DateofBirth = Column("date_of_birth",Date)
    Cellphone = Column("cellphone",String(20)) 
    
    #Declarative extension definitions.
    @declared_attr
    def GenderID(cls):
        return Column("gender_id",Integer, ForeignKey("check_gender.id"))
    
    @declared_attr
    def MaritalStatusID(cls):
        return Column("marital_status_id",Integer, ForeignKey("check_marital_status.id"))
    
    def age(self,format):
        '''
        Calculate current age of person instance.
        '''
        currDate = date.today()
        age = self.DateofBirth - currDate
        
        return age.days
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["FirstName"] = QApplication.translate("DatabaseMapping","First Name") 
        attrTranslations["LastName"] = QApplication.translate("DatabaseMapping","Last Name")
        attrTranslations["GenderID"] = QApplication.translate("DatabaseMapping","Gender")
        attrTranslations["MaritalStatusID"] = QApplication.translate("DatabaseMapping","Marital Status")
        attrTranslations["Cellphone"] = QApplication.translate("DatabaseMapping","Cellphone") 
        
        return attrTranslations
        
class Enumerator(BasePersonMixin,Model,Base):
    '''
    Enumerator model configuration.
    No additional attributes from the ones in person base class.
    '''
    __tablename__ = "enumerator"
    id = Column(Integer,primary_key = True)
    Surveys = relationship("Survey",backref="Enumerator")
    
class Farmer(BasePersonMixin,Model,Base):
    '''
    Represents the farmer who constitutes the social tenure relationship.
    '''
    __tablename__ = 'farmer' 
    id = Column(Integer,primary_key = True)
    FarmerNumber = Column("farmer_number",String(20)) 
    Priorities = relationship("Priority",cascade="all,delete-orphan")
    Impacts = relationship("Impact",cascade="all,delete-orphan")
    HouseholdID = Column("household_id",Integer,ForeignKey('household.id'))
    Household = relationship("Household",uselist = False,single_parent = True)
    
    @staticmethod
    def displayMapping():
        '''
        Base class override.
        Returns the dictionary containing the translation mapping for the attributes.
        '''
        baseAttrTranslations = BasePersonMixin.displayMapping()
        baseAttrTranslations["FarmerNumber"] = QApplication.translate("DatabaseMapping","Farmer Number") 
        
        return baseAttrTranslations    
    
class Witness(BasePersonMixin,Model,Base):
    '''
    Questionnaire respondent witness.
    '''
    __tablename__ = "witness"
    id = Column(Integer,primary_key = True)
    RelationshipID = Column("relationship_id",Integer,ForeignKey('check_witness_relationship.id'))
    OtherRelationship = Column("other_relationship",String(50))
    SurveyID = Column("survey_id",Integer,ForeignKey('survey.id'))
    
    @staticmethod
    def displayMapping():
        '''
        Base class override.
        Returns the dictionary containing the translation mapping for the attributes.
        '''
        baseAttrTranslations = BasePersonMixin.displayMapping()
        baseAttrTranslations["RelationshipID"] = QApplication.translate("DatabaseMapping","Relationship") 
        baseAttrTranslations["OtherRelationship"] = QApplication.translate("DatabaseMapping","Other Relationship") 
        
        return baseAttrTranslations
    
class Respondent(BasePersonMixin,Model,Base):
    '''
    Questionnaire respondent.
    '''
    __tablename__ = "respondent"
    id = Column(Integer,primary_key = True)
    RoleID = Column("respondent_role_id",Integer,ForeignKey('check_respondent_type.id'))
    OtherRole = Column("other_role",String(50))
    
    @staticmethod
    def displayMapping():
        '''
        Base class override.
        Returns the dictionary containing the translation mapping for the attributes.
        '''
        baseAttrTranslations = BasePersonMixin.displayMapping()
        baseAttrTranslations["RoleID"] = QApplication.translate("DatabaseMapping","Role") 
        baseAttrTranslations["OtherRole"] = QApplication.translate("DatabaseMapping","Other Role") 
        
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
    RespondentID = Column("respondent_id",Integer,ForeignKey('respondent.id'))
    Respondent = relationship("Respondent",uselist = False,single_parent = True,cascade = "all, delete-orphan")
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["Code"] = QApplication.translate("DatabaseMapping","Code") 
        attrTranslations["EnumerationDate"] = QApplication.translate("DatabaseMapping","Enumeration Date")
        attrTranslations["EnumeratorID"] = QApplication.translate("DatabaseMapping","Enumerator")
        attrTranslations["RespondentID"] = QApplication.translate("DatabaseMapping","Respondent")
        
        return attrTranslations
    
class Garden(Model,Base):
    '''
    Farm attributes.
    '''
    __tablename__ = 'garden'
    id = Column(Integer,primary_key = True)
    Identifier = Column("identifier",String(30))
    Geom = Column("geom",Geometry('POLYGON',srid = 4326))
    Acreage = Column("acreage",Numeric(16,2))
    AverageHarvest = Column("average_harvest",Numeric(16,2))
    MonthlyEarning = Column("monthly_earning",Numeric(16,2))
    MonthlyLabor = Column("monthly_labor",Numeric(16,2))
    PlantingYear = Column("planting_year",Date)
    FoodCrops = relationship("FoodCrop",backref="Garden",cascade="all, delete-orphan")
    SurveyPoints = relationship("GardenSurveyPoint",backref="Garden",cascade="all, delete-orphan")
    
    @staticmethod
    def nextVal():
        '''
        Returns the next value of the primary key sequence.
        '''
        sequenceName = "garden_id_seq"
        sequence = Sequence(sequenceName)
        conn = STDMDb.instance().engine.connect() 
        nextId = conn.execute(sequence)
        conn.close()
        
        return nextId
    
class SurveyPointMixin(object):
    '''
    Abstract class for persisting point coordinate information.
    '''
    _SRID = 4326
    EstimatedAccuracy = Column("estimated_accuracy",Numeric(16,2))
    Geom = Column("geom",Geometry('POINT',srid = _SRID))
    PointNumber = Column("point_number",String(20))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["Geom"] = QApplication.translate("DatabaseMapping","Coordinates Pair") 
        
        return attrTranslations
    
    @staticmethod
    def SRID():
        """
        Returns the SRID of the geometry column.
        """
        return SurveyPointMixin._SRID
    
class GardenSurveyPoint(SurveyPointMixin,Model,Base):
    '''
    Survey point for GPS-mapped garden points.
    '''
    __tablename__ = "garden_survey_point"
    id = Column(Integer,primary_key = True)
    GardenID = Column("garden_id",Integer,ForeignKey("garden.id"))
    
class HouseSurveyPoint(SurveyPointMixin,Model,Base):
    '''
    Survey point for farmer's house.
    '''
    __tablename__ = "house_survey_point"
    id = Column(Integer,primary_key = True)
    HouseID  = Column("house_id",Integer,ForeignKey("house.id"))
    
class FoodCrop(Model,Base):
    '''
    Food crops that are grown in the oil palm garden.
    '''
    __tablename__ = "food_crop"
    id = Column(Integer,primary_key = True)
    GardenID = Column("garden_id",Integer,ForeignKey('garden.id'))
    Acreage = Column("acreage",Numeric(16,2))
    CropName = Column("crop_name",String(20))
    CategoryID = Column("food_crop_category_id",Integer,ForeignKey('check_food_crop_category.id'))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["Acreage"] = QApplication.translate("DatabaseMapping","Acreage") 
        attrTranslations["CropName"] = QApplication.translate("DatabaseMapping","CropName")
        attrTranslations["CategoryID"] = QApplication.translate("DatabaseMapping","Category")
        
        return attrTranslations
    
class SocialTenureRelationshipMixin(object):
    '''
    Mixin class for defining social tenure relationship attributes.
    '''
    id = Column(Integer,primary_key = True)
    AgreementAvailable = Column("agreement_available",Boolean)
    AgreementType = Column("agreement_form",String(20))
    OtherLandType = Column("other_land_type",String(20))
    
    #Declarative extension definitions
    @declared_attr
    def LandTypeID(cls):
        return Column("land_type_id",Integer,ForeignKey('check_land_type.id'))
    
    @declared_attr
    def TenureTypeID(cls):
        return Column("tenure_type_id",Integer,ForeignKey('check_social_tenure_relationship.id'))
    
class GardenSocialTenureRelationship(SocialTenureRelationshipMixin,Model,Base):
    '''
    Social tenure relationship that the farmer has with the garden.
    '''
    __tablename__ = "garden_social_tenure_relationship"
    FarmerID = Column("farmer_id",Integer,ForeignKey('farmer.id'))
    Farmer = relationship("Farmer",backref="GardenSTR",uselist = False)
    GardenID = Column("garden_id",Integer,ForeignKey("garden.id"))
    Garden = relationship("Garden",backref="SocialTenure",uselist=False)
    
class House(Model,Base):
    '''
    Farmer's residence.
    '''
    __tablename__ = "house"
    id = Column(Integer,primary_key = True)
    HouseInGarden = Column("house_in_garden",Boolean)
    HouseNumber = Column("house_number",String)
    StructureTypeID = Column("structure_type_id",Integer,ForeignKey("check_house_type.id"))
    UseTypeID = Column("use_type_id",Integer,ForeignKey("check_house_use_type.id"))
    SurveyPoints = relationship("HouseSurveyPoint",backref="House",cascade="all, delete-orphan")
    
class HouseSocialTenureRelationship(SocialTenureRelationshipMixin,Model,Base):
    '''
    Social tenure relationship that the farmer has with the residence.
    '''
    __tablename__ = "house_social_tenure_relationship"
    FarmerID = Column("farmer_id",Integer,ForeignKey('farmer.id'))
    Farmer = relationship("Farmer",backref="HouseSTR",uselist = False)
    HouseID = Column("house_id",Integer,ForeignKey("house.id"))
    House = relationship("House",backref="SocialTenure",uselist=False)
    
class Household(Model,Base):
    '''
    Household to which the farmer belongs to.
    '''
    __tablename__ = "household"
    id = Column(Integer,primary_key=True)
    FemaleNumber = Column("female_number",Integer)
    MaleNumber = Column("male_number",Integer)
    #This is only valid if income sources have not been disaggregated 
    AggregateIncome = Column("aggregate_income",Numeric(16,2))
    IncomeSources = relationship("HouseholdIncome",cascade="all,delete-orphan")
    SavingOptions = relationship("HouseholdSaving",cascade="all,delete-orphan")
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["FemaleNumber"] = QApplication.translate("DatabaseMapping","Female Number") 
        attrTranslations["MaleNumber"] = QApplication.translate("DatabaseMapping","Male Number")
        attrTranslations["AggregateIncome"] = QApplication.translate("DatabaseMapping","Total Income")
        
        return attrTranslations
    
    def totalIncome(self):
        '''
        Returns the overall income of the household from the multiple income sources.
        '''
        tIncome = 0
        for incomeSrc in self.IncomeSources:
            tIncome = incomeSrc.EstimateIncome + tIncome
        
        return tIncome
    
class HouseholdIncome(Model,Base):
    '''
    Represents the source and amount of household income.
    '''
    __tablename__ = "household_income"
    id = Column(Integer,primary_key=True)
    Activity = Column("activity",String(50))
    EstimateIncome = Column("estimate_income",Numeric(16,2))
    HouseHoldID = Column("household_id",Integer,ForeignKey("household.id"))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["Activity"] = QApplication.translate("DatabaseMapping","Activity") 
        attrTranslations["EstimateIncome"] = QApplication.translate("DatabaseMapping","Estimate Income")
        
        return attrTranslations
    
class HouseholdSaving(Model,Base):
    '''
    Household saving options.
    '''
    __tablename__ = "household_saving"
    id = Column(Integer,primary_key=True)
    OptionID = Column("saving_option_id",Integer,ForeignKey("check_household_savings.id"))
    OtherOption = Column(String(20))
    HouseHoldID = Column("household_id",Integer,ForeignKey("household.id"))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["OptionID"] = QApplication.translate("DatabaseMapping","Savings Option") 
        attrTranslations["OtherOption"] = QApplication.translate("DatabaseMapping","Other Option")
        #attrTranslations["AggregateIncome"] = QApplication.translate("DatabaseMapping","Total Income")
        
        return attrTranslations
    
class SupportsRankingMixin(object):
    '''
    Mixin item for classes that supporting ranking of items for a farmer. 
    '''
    id = Column(Integer,primary_key=True)
    Rank = Column("rank",Integer)
    OtherItem = Column("other_item",String(30))
    
    @declared_attr
    def FarmerID(cls):
        return Column("farmer_id",Integer,ForeignKey("farmer.id"))
    
class Priority(SupportsRankingMixin,Model,Base):
    '''
    Priority tools and services as identified by a farmer.
    '''
    __tablename__ = "priority"
    itemID = Column("item_id",Integer,ForeignKey("check_input_service.id"))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["itemID"] = QApplication.translate("DatabaseMapping","Priority Service") 
        attrTranslations["OtherItem"] = QApplication.translate("DatabaseMapping","Other Service")
        attrTranslations["Rank"] = QApplication.translate("DatabaseMapping","Rank")
        
        return attrTranslations
    
class Impact(SupportsRankingMixin,Model,Base):
    '''
    Resulting socio-economic impacts as a result of the VODP.
    '''
    __tablename__ = "impact"
    itemID = Column("item_id",Integer,ForeignKey("check_socio_economic_impact.id"))
    
    @staticmethod
    def displayMapping():
        #Display translation mappings
        attrTranslations = OrderedDict()
        attrTranslations["id"] = "ID" 
        attrTranslations["itemID"] = QApplication.translate("DatabaseMapping","Impact") 
        attrTranslations["OtherItem"] = QApplication.translate("DatabaseMapping","Other Impact")
        attrTranslations["Rank"] = QApplication.translate("DatabaseMapping","Rank")
        
        return attrTranslations

"""
class BaseSourceDocument(object):    
    '''
    Base class for all supporting documents.
    '''
    DocumentID = Column('document_id',String(50),unique = True)
    FileName = Column('filename',String(200))
    Size = Column("doc_size",Integer)
    DocumentType = Column("doctype",Integer)

class SourceDocument(Model,Base,BaseSourceDocument):
    '''
    Source document for social tenure relationships.
    '''
    __tablename__ = 'source_document'
    id = Column(Integer,primary_key = True)
    STRID = Column("str_id",Integer,ForeignKey('social_tenure_relationship.id'))
"""
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


            
            
            
            
            
            
        
        
        
        
        
