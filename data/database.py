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
from collections import (
    defaultdict,
    OrderedDict
)

from PyQt4.QtGui import QApplication

from sqlalchemy import (
    create_engine,
    ForeignKey,
    Table,
    event,
    func,
    MetaData,
    exc
)
from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    Numeric,
    Text,
    Boolean
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr
)
from sqlalchemy.orm import (
    relationship,
    backref,
    mapper as _mapper
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Sequence
from sqlalchemy.exc import (
    NoSuchTableError
)
from sqlalchemy.sql.expression import text
from geoalchemy2 import Geometry

import stdm.data

metadata = MetaData()

#Registry of table names and corresponding mappers
table_registry = defaultdict(set)

def mapper(cls, table=None, *args, **kwargs):
    tb_mapper = _mapper(cls, table, *args, **kwargs)
    table_registry[table.name].add(tb_mapper)

    return tb_mapper

Base = declarative_base(metadata=metadata)

class Singleton(object):
    """
    Singleton class
    """
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

class NoPostGISError(Exception):
    """Raised when the PostGIS extension is not installed in the specified
    STDM database."""
    pass
    
@Singleton
class STDMDb(object):
    """
    This class will exist only once hence the reason it has a singleton attribute.
    It will contain the session for managing the unit of work for each class.
    """
    engine = None
    session = None

    def __init__(self):
        #Initialize database engine
        self.engine = create_engine(stdm.data.app_dbconn.toAlchemyConnection(), echo=False)

        #Check for PostGIS extension
        state = self._check_spatial_extension()

        if not state:
            raise NoPostGISError

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.createMetadata()

    def createMetadata(self):
        """
        Creates STDM database schema
        """
        Base.metadata.create_all(self.engine)

    def instance(self,*args,**kwargs):
        """
        Dummy method. Eclipse IDE cannot handle the Singleton decorator in Python
        """
        pass

    def _check_spatial_extension(self):
        """Check if the PostGIS exists and if so, check if the extension
        has been installed in the specified database and raise an error if
        the extension is not found."""
        spatial_extension_installed = True

        sql = text("SELECT installed_version FROM pg_available_extensions "
                   "WHERE name=:ext_name")

        conn = self.engine.connect()
        result = conn.execute(sql, ext_name='postgis').first()

        if result is None:
            spatial_extension_installed = False

        else:
            installed_version = result[0]

            if installed_version is None:
                spatial_extension_installed = False

        conn.close()

        return spatial_extension_installed

def alchemy_table(table_name):
    """
    Get an SQLAlchemy table object based on the table_name of the table in the table..
    :param table_name: Table Name
    :type table_name: str
    """
    meta = MetaData(bind=STDMDb.instance().engine)

    try:
        return Table(table_name, meta, autoload=True)

    except NoSuchTableError:
        return None

def table_mapper(table_name):
    """
    :param table_name: Name of the database table.
    :type table_name: str
    :return: Mapper for the specified table. None if it does not exist.
    :rtype: object
    """
    mapper_collection = table_registry.get(table_name, None)

    if mapper_collection is None or len(mapper_collection) == 0:
        return None

    return list(mapper_collection)[0]

def alchemy_table_relationships(table_name):
    """
    Returns the relationship items configured for mapper which corresponds
    to the given table name.
    :param table_name: Name of the database table.
    :return: Relationship property objects.
    :rtype: list
    """
    t_mapper = table_mapper(table_name)

    if t_mapper is None:
        return []

    relationships = t_mapper.relationships

    relationship_names = []

    for r in relationships:
        r_names = str(r).split(".", 1)

        relationship_names.append(r_names[1])

    return relationship_names
        
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
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            
    def saveMany(self,objects = []):
        '''
        Save multiple objects of the same type in one go.
        '''
        db = STDMDb.instance()
        db.session.add_all(objects)
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()

    def update(self):
        db = STDMDb.instance()
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            
    def delete(self):
        op_result = True

        db = STDMDb.instance()
        db.session.delete(self)

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            op_result = False
            db.session.rollback()

        return op_result

    def queryObject(self,args=[]):
        '''
        The 'args' specifies the attributes/columns
        that will be returned in the query in a tuple;
        Else, the full model object will be returned.
        '''
        db = STDMDb.instance()
        #raise NameError(str(self.__class__))
        try:
            if len(args) == 0:
                return db.session.query(self.__class__)

            else:
                return db.session.query(*args)
        except exc.SQLAlchemyError:
            db.session.rollback()
    
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

    def hierarchy_names(self, separator="/"):
        """
        Return comma separated names of all administrative units
        :param separator: A symbol used to separate names.
        :type separator: String
        :return: The name of all admin units in a hierarchy
        :rtype: String
        """
        name_list = []
        name_list.append(self.Name)

        parent = self.Parent
        while parent != None:
            name_list.append(parent.Name)
            parent = parent.Parent

        # Reverse the items so that the last item added becomes the prefix of the hierarchy code
        reverse_name = list(reversed(name_list))

        return separator.join(reverse_name)