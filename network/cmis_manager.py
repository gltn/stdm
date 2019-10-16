"""
/***************************************************************************
Name                 : CmisManager
Description          : Provides an interface for managing communication with
                       the CMIS server
Date                 : 23/July/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
from mimetypes import guess_type
from uuid import uuid4
from collections import OrderedDict
from cmislib import (
    CmisClient
)
import subprocess
import requests
from requests.exceptions import Timeout

from PyQt4.QtCore import (
    QFileInfo,
    QObject,
    QProcess,
    QUrl,
    pyqtSignal
)
from cmislib.exceptions import (
    CmisException,
    ObjectNotFoundException
)
from stdm.security.auth_config import (
    auth_config_from_id
)
from stdm.settings.registryconfig import (
    cmis_atom_pub_url,
    cmis_auth_config_id
)
from stdm.utils.util import (
    is_chrome_installed
)

CMIS_NAME = 'cmis:name'
CMIS_TITLE = 'cmis:title'
CMIS_VERSION_SERIES_ID = 'cmis:versionSeriesId'
CMIS_CREATED_BY = 'cmis:createdBy'
CMIS_CREATION_DATE = 'cmis:creationDate'
CMIS_CONTENT_STREAM_LENGTH = 'cmis:contentStreamLength'
CMIS_CONTENT_STREAM_ID = 'cmis:contentStreamId'

# PDF Viewer constants
DOC_ID_PROP = 'document_id'


class CmisManager(object):
    """
    Provides an interface for STDM modules to communicate with the CMIS
    server. Currently, only the Atom Pub service is supported.
    """
    def __init__(self, **kwargs):
        """
        Class constructor.
        :param kwargs:
        - url: URL of the CMIS atom pub service. Obtained from the
        settings if not specified.
        - auth_config_id: ID of the authentication configuration. Obtained
        from the settings if not specified.
        """
        self.url = kwargs.pop('url', '')
        # Use default URL in the settings if None has been specified
        if not self.url:
            self.url = cmis_atom_pub_url()

        self._auth_config_id = kwargs.pop('auth_config_id', '')
        self._auth_config = None
        # Use default configuration ID in the settings if not specified
        if not self._auth_config_id:
            self._auth_config_id = cmis_auth_config_id()

        if self._auth_config_id:
            self._update_auth_config()

        self.username = ''
        self.password = ''

        # Update username and password
        self._update_username_password()

        self._connected = False
        self._cmis_client = None
        self._default_repo = None
        self._context_base_folder_name = 'FLTS'
        self.temp_folder_name = 'Temp'

    @property
    def context_folder_name(self):
        """
        :return: Returns the name of the base folder used for the particular
        context. This folder should be a child of the repository's root
        folder.
        :rtype: str
        """
        return self._context_base_folder_name

    @context_folder_name.setter
    def context_folder_name(self, name):
        """
        Sets the name of the base folder that will be used for the
        particular application context.
        :param name: Name of the context folder
        :type name: str
        """
        self._context_base_folder_name = name

    @property
    def context_base_folder(self):
        """
        :return: Returns the folder object corresponding to the context
        base folder name. Return None if it does not exist.
        :rtype: cmislib.domain.Folder
        """
        if not self._default_repo:
            return None

        if not self.context_folder_name:
            return None

        ctx_folder = None
        try:
            ctx_folder = self._default_repo.getObjectByPath(
                u'/{0}'.format(self.context_folder_name)
            )
        except ObjectNotFoundException:
            pass

        return ctx_folder

    @property
    def context_temp_folder_path(self):
        """
        :return: Returns the path of the temporary folder, which is
        relative to the base context folder.
        :rtype: str
        """
        if not self.context_folder_name:
            return ''

        return u'{0}/{1}'.format(
            self.context_folder_name,
            self.temp_folder_name
        )

    @property
    def context_temp_folder(self):
        """
        :return: Returns the folder object which is a temporary directory
        for working files in the CB-FLTS. This folder is a child of the
        context base folder. Returns None if it does not exist.
        :rtype: cmislib.domain.Folder
        """
        temp_folder_name = self.context_temp_folder_path
        if not temp_folder_name:
            return None

        temp_folder = None
        try:
            temp_folder = self._default_repo.getObjectByPath(
                u'/{0}'.format(self.context_temp_folder_path)
            )
        except ObjectNotFoundException:
            pass

        return temp_folder

    def create_temp_folder(self):
        """
        Creates the temp folder, under the context base folder, if None
        exists.
        :return: Returns True if the operation succeeded, otherwise False.
        :rtype: bool
        """
        status = False

        ctx_folder = self.context_base_folder
        if not ctx_folder:
            msg = 'Context base folder does not exist.'
            raise CmisDocumentMapperException(msg)

        tmp_folder = self.context_temp_folder
        # No need to create if it already exists
        if tmp_folder:
            return status

        tmp_folder = ctx_folder.createFolder(
            self.temp_folder_name
        )
        status = True

        return status

    @property
    def default_repository(self):
        """
        :return: Returns the default repository in the document server.
        The client must have had a successful connection to the service
        prior to using this property
        :rtype: cmislib.domain.Repository
        """
        return self._default_repo

    def _update_auth_config(self):
        # Update the authentication configuration object based on auth id
        self._auth_config = auth_config_from_id(
            self._auth_config_id
        )

    def _update_username_password(self):
        # Update the username and password from the authentication config
        if self._auth_config:
            self.username = self._auth_config.config('username')
            self.password = self._auth_config.config('password')

    @property
    def auth_config_id(self):
        """
        :return: Returns the ID of the authentication configuration.
        :rtype: str
        """
        return self._auth_config_id

    @auth_config_id.setter
    def auth_config_id(self, config_id):
        """
        Set the ID of the authentication configuration. This will trigger an
        update of the username and password.
        :param config_id: ID of the authentication configuration
        :type config_id: str
        """
        if config_id == self._auth_config_id:
            return

        self._auth_config_id = config_id
        self._update_auth_config()
        self._update_username_password()

    def connect(self):
        """
        :return: Returns True if the connection succeeded, else False.
        Failure to connect can be due to invalid URL or wrong authentication
        credentials.
        :rtype: bool
        """
        status = False
        self._cmis_client = CmisClient(
            self.url,
            self.username,
            self.password
        )

        try:
            self._default_repo = self._cmis_client.defaultRepository
            self._connected = True
            status = True
        except Exception as ex:
            pass

        return status

    @property
    def root_folder(self):
        """
        :return: Returns the root folder in the default repository. Returns
        None if the repository was not initialized properly.
        :rtype: cmislib.domain.Folder
        """
        if not self._default_repo:
            return None

        return self._default_repo.rootFolder

    def sub_folders(self, parent_folder):
        """
        Get the folders that are the immediate children of the specified
        parent folder.
        :param parent_folder: Folder for which the immediate children are
        to be extracted.
        :type parent_folder: cmislib.domain.Folder
        :return: Returns a list containing the immediate children folders
        of the parent folder. It can also return an empty list if the
        repository was not initialized properly.
        :rtype: cmislib.domain.Folder
        """
        if not self._default_repo:
            return []

        rs = parent_folder.getTree(depth='1')

        return rs.getResults()

    def child_folder(self, parent_folder, name):
        """
        Gets the child folder with the given name in the parent_folder.
        :param parent_folder: Parent folder containing the children to search
        against.
        :type parent_folder: cmislib.domain.Folder
        :param name: Name of the child folder.
        :type name: str
        :return: Child folder or None if not found.
        :rtype: cmislib.domain.Folder
        """
        folders = self.sub_folders(parent_folder)
        if len(folders) == 0:
            return None

        cf = None
        for f in folders:
            f_name = f.name
            if name == f_name:
                cf = f
                break

        return cf

    def contains_subfolder(self, parent_folder, name):
        """
        Checks if the folder with the given name exists in the parent_folder.
        :param parent_folder: Parent folder containing the children to search
        against.
        :type parent_folder: cmislib.domain.Folder
        :param name: Name of the child folder.
        :type name: str
        :return: True if the child folder exists, else False.
        :rtype: bool
        """
        return True if self.child_folder(parent_folder, name) else False

    def create_base_context_folder(self):
        """
        Create the base context folder, which will be a child of the root
        folder in the repository. The process also creates the temp folder
        which is also a child of the base context folder.
        :return: Returns True if the operation succeeded, or False if the
        folder already exists or if the repository was not initialized
        properly.
        """
        if self.context_base_folder:
            return False

        if not self.root_folder:
            return False

        if not self.context_folder_name:
            return False

        # Create context base folder
        ctx_folder = self.root_folder.createFolder(
            self.context_folder_name
        )

        # Create corresponding temp folder
        if ctx_folder:
            ctx_folder.createFolder(
                self.temp_folder_name
            )


class CmisDocumentMapperException(Exception):
    """
    Errors when managing an entity's supporting documents in a CMIS
    repository.
    """
    pass


class DocumentTypeFolderMapping(object):
    """
    Class for mapping an entity document type to the corresponding folder
    in the CMIS repository.
    """
    def __init__(self, **kwargs):
        self.doc_type = kwargs.pop('doc_type', '')
        self.doc_type_code = kwargs.pop('type_code', '')
        self.doc_type_id = kwargs.pop('type_id', -1)
        self.folder = None


class UploadedDocInfo(object):
    """
    Container for info on uploaded CMIS document.
    """
    def __init__(self, **kwargs):
        self.cmis_doc = kwargs.pop('cmis_doc', None)
        self.temp_dir = kwargs.pop('temp_dir', True)


class CmisEntityDocumentMapper(object):
    """
    Class that provides an interface for managing an entity's supporting
    documents in a CMIS repository.
    A child folder, relative to the context base folder, will be created
    using the entity name.
    """
    def __init__(self, **kwargs):
        self._cmis_mgr = kwargs.pop('cmis_manager', None)
        self._doc_model_cls = kwargs.pop('doc_model_cls', None)
        self._entity_name = kwargs.pop('entity_name', '')
        self._entity_folder = None
        if self._cmis_mgr and self._entity_name:
            self._set_entity_folder()

        self._doc_type_mapping = {}
        self._uploaded_docs = OrderedDict()

    def _extract_cmis_doc(self, uploaded_doc_info):
        return uploaded_doc_info.cmis_doc

    @property
    def uploaded_documents(self):
        """
        :return: Returns a collection indexed by document type with a list
        containing the uploaded Document objects.
        :rtype: dict
        """
        return {
            doc_type: map(self._extract_cmis_doc, doc_infos)
            for doc_type, doc_infos in self._uploaded_docs.iteritems()
        }

    def uploaded_documents_by_type(self, doc_type):
        """
        Gets the list of uploaded documents based on the document type.
        :param doc_type: Name of the document type.
        :type doc_type: str
        :return: Returns the list of uploaded documents based on the
        document type. Returns None if the document type does not exist
        in the collection of uploaded documents.
        :rtype: list
        """
        return self.uploaded_documents.get(doc_type, None)

    def _cmis_doc_id(self, doc):
        # Returns the unique identifier of the document in the CMIS repo.
        props = doc.getProperties()
        return props[CMIS_VERSION_SERIES_ID]

    def _uploaded_document_by_type_uuid(self, doc_type, uuid):
        # Returns a tuple containing the index of the document in the list
        # and corresponding document object. Returns (-1, None) if not found.
        if not doc_type in self.uploaded_documents:
            return None

        uploaded_type_docs = self.uploaded_documents_by_type(doc_type)

        idx, d = -1, None
        for i, doc in enumerate(uploaded_type_docs):
            if self._cmis_doc_id(doc):
                idx = i
                d = doc
                break

        return idx, d

    def remove_document(self, doc_type, uuid):
        """
        Removes the document with the given unique identifier and of the
        given type.
        :param doc_type: Name of the document type.
        :type doc_type: str
        :param uuid: Unique identifier of the document in the CMIS repository.
        :type uuid: str
        :return: Returns True if the operation succeeded or False if it
        failed. The latter can be due to:
            - The document type does not exist.
            - The document with the given identifier was not found.
            - The operation failed in the CMIS server side.
        :rtype: bool
        """
        # Need to manually remove items from the collection
        if not doc_type in self._uploaded_docs:
            return False

        idx = -1
        doc_infos = self._uploaded_docs[doc_type]
        for i, di in enumerate(doc_infos):
            doc = di.cmis_doc
            doc_id = self._cmis_doc_id(doc)
            if doc_id == uuid:
                idx = i
                break

        if idx == -1:
            return False

        # Remove document information object
        rm_doc_info = doc_infos.pop(idx)
        rm_doc = rm_doc_info.cmis_doc

        # Delete the document from the repository
        rm_doc.delete()
        del rm_doc_info

        return True

    def remove_all_documents(self, doc_type):
        """
        Removes all the documents (in the current session) for the given type.
        :param doc_type: Type of the document.
        :type doc_type: str
        """
        if not doc_type in self._uploaded_docs:
            return

        doc_infos = self._uploaded_docs[doc_type]
        for di in doc_infos:
            doc = di.cmis_doc
            # Attempt to delete and suppress any errors
            try:
                doc.delete()
            except:
                pass

            del di

        # Reset container
        self._uploaded_docs[doc_type] = []

    def uploaded_document_by_type_uuid(self, doc_type, uuid):
        """
        Searches the collection of uploaded documents for the AtomPub
        document based on the document type and corresponding unique
        identifier of the document.
        :param doc_type: Name of the document type.
        :type doc_type: str
        :param uuid: Unique document identifier in the CMIS repository.
        :type uuid: str
        :return: Returns the AtomPub document or None if not found.
        :rtype: cmislib.domain.Document
        """
        idx, doc = self._uploaded_document_by_type_uuid(doc_type, uuid)

        return doc

    @property
    def entity_folder(self):
        """
        :return: Returns the folder object for storing the supporting
        documents related to the reference entity. This will be a child
        under the context base folder.
        :rtype: cmislib.domain.Folder
        """
        return self._entity_folder

    def create_entity_folder(self):
        """
        Creates the entity folder, under the context base folder, if None
        exists.
        :return: Returns True if the operation succeeded, otherwise False.
        :rtype: bool
        """
        status = False
        if not self._entity_name:
            msg = 'Cannot create folder because entity name is empty.'
            raise CmisDocumentMapperException(msg)

        # No need to create if it already exists
        if self._entity_folder:
            return status

        ctx_folder = self._cmis_mgr.context_base_folder
        if not ctx_folder:
            msg = 'Context base folder does not exist.'
            raise CmisDocumentMapperException(msg)

        self._entity_folder = ctx_folder.createFolder(
            self._entity_name
        )
        status = True

        return status

    def _set_entity_folder(self):
        """
        Searches the repository and sets the entity folder. Creates if it
        does not exist.
        """
        if self._entity_folder:
            return

        if not self._cmis_mgr:
            msg = 'CmisManager object not specified.'
            raise CmisDocumentMapperException(msg)

        # Search repository
        ctx_folder = self._cmis_mgr.context_base_folder
        if not ctx_folder:
            msg = 'Context base folder does not exist.'
            raise CmisDocumentMapperException(msg)

        entity_folder = self._cmis_mgr.child_folder(
            ctx_folder, self._entity_name
        )
        if entity_folder:
            self._entity_folder = entity_folder
        else:
            self.create_entity_folder()

    @property
    def entity_name(self):
        """
        :return: Returns the name of the entity associated with the
        supporting documents managed by this object.
        :rtype: str
        """
        return self._entity_name

    @entity_name.setter
    def entity_name(self, name):
        """
        Sets the name of the entity associated with the supporting
        documents managed by this object. It checks if the corresponding
        folder exists in the CMIS repository and creates if it does not exist.
        :param name: Entity name.
        :type name: str
        """
        if not name:
            return

        self._entity_name = name
        self._set_entity_folder()

    def create_document_type_folder(self, name):
        """
        Creates a folder for storing documents of a specific type.
        :param name: Name of the document type.
        :type name: str
        :return: Returns the newly created document type folder.
        :rtype: cmislib.domain.Folder
        """
        if not self._entity_folder:
            msg = u'Cannot create {0} folder as parent folder does not ' \
                  u'exist'.format(name)
            raise CmisDocumentMapperException(msg)

        # Get mapper object
        doc_mapper = self.mapping(name)
        if not doc_mapper:
            msg = u'No mapping specified for {0} document type'.format(name)
            raise CmisDocumentMapperException(msg)

        doc_type_folder = self._entity_folder.createFolder(
            name
        )

        # Update document type mapping
        doc_mapper.folder = doc_type_folder

        return doc_type_folder

    def mapping(self, name):
        """
        Get the document type mapping object based on the name of the
        document type.
        :param name: Name of document type.
        :type name: str
        :return: Returns the document type mapping object based on the name
        of the document type or None if not found.
        :rtype: DocumentTypeFolderMapping
        """
        return self._doc_type_mapping.get(name, None)

    def mapping_by_code(self, code):
        """
        Get the document type mapping object based on the code of the
        document type.
        :param name: Code of document type.
        :type name: str
        :return: Returns the document type mapping object based on the code
        of the document type or None if not found.
        """
        return next(
            (
                m for m in self._doc_type_mapping.values()
                if m.doc_type_code == code
            ),
            None
        )

    def document_type_folder(self, name):
        """
        Gets the folder object for the given document type.
        :param name: Document type name.
        :type name: str
        :return: Returns the folder object corresponding to the given
        document type. It first searches in the document mapping collection
        and if not found, queries the CMIS repository under the children
        folders of the root entity folder. Returns None if there are no
        matching results.
        :rtype: cmislib.domain.Folder
        """
        doc_type_folder = None
        doc_type_mapping = self.mapping(name)

        if doc_type_mapping:
            doc_type_folder = doc_type_mapping.folder

        if doc_type_folder:
            return doc_type_folder

        # Lets search the repository
        if not self._entity_folder:
            msg = u'Cannot search for {0} folder as parent entity folder ' \
                  u'is None.'.format(name)
            raise CmisDocumentMapperException(msg)

        doc_type_folder = self._cmis_mgr.child_folder(
            self._entity_folder,
            name
        )

        # Set it to the mapping if it exists
        if doc_type_mapping and doc_type_folder:
            doc_type_mapping.folder = doc_type_folder

        return doc_type_folder

    @property
    def cmis_manager(self):
        """
        :return: Returns an instance of the CMIS manager which
        communicates with the CMIS repository.
        :rtype: CmisManager
        """
        return self._cmis_mgr

    @cmis_manager.setter
    def cmis_manager(self, cmis_mgr):
        """
        Sets the instance of the CMIS manager for communicating with the
        CMIS repository.
        :param cmis_mgr: Instance of the CMIS manager.
        :type cmis_mgr: CmisManager
        """
        self._cmis_mgr = cmis_mgr

        # Update reference to the entity folder
        if self._cmis_mgr:
            self._set_entity_folder()

    @property
    def document_model_cls(self):
        """
        :return: Returns the SQLAlchemy class that corresponds to an
        entity's supporting document.
        :rtype: stdm.data.database.Model
        """
        return self._doc_model_cls

    @document_model_cls.setter
    def document_model_cls(self, doc_model_cls):
        """
        Sets the SQLAlchemy class that corresponds to an entity's supporting
        document.
        :param doc_model_cls: Supporting document SQLAlchemy class
        :type doc_model_cls: stdm.data.database.Model
        """
        self._doc_model_cls = doc_model_cls

    def add_document_type(self, name, code='', type_id=-1):
        """
        Add the name of the document type that will be managed by this
        object. You can also set the corresponding code which can also be
        used (in place of document type name) when uploading a document of
        this given type.
        :param name: Name of the document type.
        :type name: str
        :param code: Code corresponding to the type of the document.
        :type code: str
        :param type_id: Primary key id of the document type in the lookup table.
        :type type_id: int
        """
        doc_type_mapping = DocumentTypeFolderMapping(
            doc_type=name,
            type_code=code,
            type_id=type_id
        )
        self.add_mapping(doc_type_mapping)

    def add_mapping(self, doc_type_mapping):
        """
        Adds a DocumentTypeFolderMapping object which contains information on
        the location for document types. Any existing mapper with the same
        document type name will be replaced.
        :param doc_type_mapping: Contains target location information in the
        CMIS repository.
        :type doc_type_mapping: DocumentTypeFolderMapping
        :raises: CmisDocumentMapperException if the mapper object has missing
        values for the key mandatory field i.e. document type name.
        """
        if not doc_type_mapping.doc_type:
            msg = 'Document type is missing in DocumentTypeFolderMapping ' \
                  'instance.'
            raise CmisDocumentMapperException(msg)

        self._doc_type_mapping[doc_type_mapping.doc_type] = doc_type_mapping

    def clear_mapping(self):
        """
        Resets the folder mapping for the different document types.
        :return:
        """
        self._doc_type_mapping = {}

    def _cmis_doc_to_db_model(self, cmis_doc, doc_type_id):
        # Create a database model object from the CMIS doc properties.
        if not self._doc_model_cls:
            msg = 'A database document model object has not been specified.'
            raise CmisDocumentMapperException(msg)

        # Get CMIS properties
        props = cmis_doc.getProperties()
        doc_identifier = props[CMIS_VERSION_SERIES_ID]
        doc_size = props[CMIS_CONTENT_STREAM_LENGTH]
        doc_name = props[CMIS_NAME]
        # Relative location in document repo file system
        doc_url = props[CMIS_CONTENT_STREAM_ID]
        created_by = props[CMIS_CREATED_BY]
        creation_date = props[CMIS_CREATION_DATE]

        # Add properties to model
        db_model = self._doc_model_cls()
        db_model.last_modified = creation_date
        db_model.document_identifier = doc_identifier
        db_model.source_entity = self.entity_name
        db_model.document_size = doc_size
        db_model.name = doc_name
        db_model.content_url = doc_url
        db_model.created_by = created_by
        db_model.document_type = doc_type_id

        return db_model

    def persist_documents(self, reference_name=''):
        """
        Moves the documents in the Temp directory to the corresponding
        document type folders for the given entity. If reference_name is
        specified, the document names will be replaced with this reference
        name. The document object models will also be created and returned
        as a list.
        :param reference_name: Name to be used for naming the documents when
        moved from the Temp folder.
        :type reference_name: str
        :return: Returns a list of document object models for attaching to
        the main entity object for saving in the database.
        :rtype: list
        """
        temp_folder = self._cmis_mgr.context_temp_folder

        doc_model_objs = []
        for doc_type, doc_infos in self._uploaded_docs.iteritems():
            # Counter for appending _n suffix in document names
            i = 0

            doc_type_folder = self.document_type_folder(doc_type)
            if not doc_type_folder:
                # Create document type folder if it does not exist
                doc_type_folder = self.create_document_type_folder(doc_type)

            if not doc_type_folder:
                msg = u'{0} folder could not be created.'.format(doc_type)
                raise CmisDocumentMapperException(msg)

            for di in doc_infos:
                doc_name = reference_name
                doc = di.cmis_doc

                # Move document if in Temp directory
                if di.temp_dir:
                    doc.move(temp_folder, doc_type_folder)

                    if i > 0:
                        doc_name = '{0}_{1:d}'.format(doc_name, i)

                    # Update the document name if reference_name is specified
                    if reference_name:
                        props = {CMIS_NAME: doc_name}
                        doc.updateProperties(props)
                        i += 1

                # Create database model
                type_mapping = self._doc_type_mapping.get(doc_type, None)
                if not type_mapping:
                    msg = 'The DocumentTypeFolderMapping object could not be found.'
                    raise CmisDocumentMapperException(msg)

                doc_type_id = type_mapping.doc_type_id
                db_model = self._cmis_doc_to_db_model(doc, doc_type_id)
                doc_model_objs.append(db_model)

        return doc_model_objs

    def upload_document(
            self,
            path,
            doc_type='',
            doc_type_code='',
            use_temp_dir=True,
            clear_all=True
    ):
        """
        Uploads the document specified in path to the folder of the given
        document type based on the specified document type folder mapping.
        :param path: Absolute path of the file to be uploaded.
        :type path: str
        :param doc_type: Name of the document type.
        :type doc_type: str
        :param doc_type_code: Code of the document type which is used to
        identify the document type. If doc_type has already been specified
        then the value of this parameter is skipped.
        :type doc_type_code: str
        :param use_temp_dir: Specify True to upload the document in the Temp
        directory using an auto-generated name then move it to the correct
        document type repository using the :func:'persist_documents' method.
        If set to False, the document will be directly uploaded to the
        corresponding document type folder. Default is True.
        :type use_temp_dir: bool
        :param clear_all: True to clear all previously uploaded documents (in
        the current session) for the given document type.
        :return: Returns the AtomPub document object, else None if it was
        not successfully created.
        :rtype: cmislib.domain.Document
        """
        if not doc_type and not doc_type_code:
            msg = 'Please specify the document type name or code.'
            raise CmisDocumentMapperException(msg)

        if not self._cmis_mgr:
            msg = 'CmisManager object not specified.'
            raise CmisDocumentMapperException(msg)

        # Get doc_type from code
        if doc_type_code and not doc_type_code:  # @gkahiu code underneath may never be reached
            doc_type_m = self.mapping_by_code(doc_type_code)
            if not doc_type_m:
                msg = u'Document type could not be retrieved from {0} ' \
                      u'document type code.'.format(doc_type_code)
                raise CmisDocumentMapperException(msg)
            else:
                doc_type = doc_type_m.doc_type

        if not doc_type in self._doc_type_mapping:
            msg = 'Mapping for the specified document type name not found.'
            raise CmisDocumentMapperException(msg)

        if use_temp_dir:
            dest_folder = self._cmis_mgr.context_temp_folder
        else:
            dest_folder = self.document_type_folder(doc_type)

        # Try create the folder if it does not exist
        if not dest_folder:
            if use_temp_dir:
                status = self._cmis_mgr.create_temp_folder()
                if not status:
                    msg = 'Temp directory could not be created.'
                    raise CmisDocumentMapperException(msg)
                else:
                    dest_folder = self._cmis_mgr.context_temp_folder
            else:
                dest_folder = self.create_document_type_folder(doc_type)

        # Clear all documents of the given type, if option has been specified
        if clear_all:
            self.remove_all_documents(doc_type)

        if use_temp_dir:
            doc_name = str(uuid4())
        else:
            # Get name of the file without the extension
            fi = QFileInfo(path)
            doc_name = fi.completeBaseName()

        # Determine whether file is text or binary
        read_mode = 'rb'
        mime_type, encoding = guess_type(path)
        text_idx = mime_type.find('text')
        if text_idx != -1:
            read_mode = 'r'

        # TODO: mime_type should be set automatically
        mime_type = 'application/pdf'

        cmis_doc = None
        with open(path, read_mode) as f:
            cmis_doc = dest_folder.createDocument(
                doc_name,
                contentFile=f,
                contentType=mime_type
            )

        # Update reference of uploaded documents.
        if not doc_type in self._uploaded_docs:
            self._uploaded_docs[doc_type] = []

        if cmis_doc:
            doc_info = UploadedDocInfo(
                cmis_doc=cmis_doc,
                temp_dir=use_temp_dir
            )

            uploaded_type_docs = self._uploaded_docs[doc_type]
            uploaded_type_docs.append(doc_info)

        return cmis_doc


def cmis_base_url():
    """
    Constructs the base URL from the CMIS Atom service end point.
    :return: Returns the base URL of the CMIS server or an empty string if
    the URL cannot be constructed or if the CMIS service has not been defined.
    :rtype: str
    """
    atom_pub_url = cmis_atom_pub_url()
    if not atom_pub_url:
        return ''

    url = QUrl(atom_pub_url)
    if not url.isValid():
        return ''

    if url.port() == -1:
        port = ''
    else:
        port = ':{0}'.format(url.port())

    return '{0}://{1}{2}'.format(
        url.scheme(),
        url.host(),
        port
    )


def login_rest_url():
    """
    :return: Returns the REST login URL.
    :rtype: str
    """
    return u'{0}/alfresco/s/api/login'.format(cmis_base_url())


def rest_ticket_url(ticket):
    """
    Builds the full rest URL based on the specified authentication ticket.
    :param ticket: Alfresco authentication ticket.
    :type ticket: str
    :return: Returns the full rest URL of the authentication ticket.
    :rtype: str
    """
    return u'{0}/ticket/{1}'.format(
        login_rest_url(),
        ticket
    )


def auth_credentials():
    # Returns a tuple containing the username and password as stored in the
    # QGIS configuration.
    u, pw = '', ''
    auth_conf = auth_config_from_id(cmis_auth_config_id())
    if auth_conf:
        u = auth_conf.config('username')
        pw = auth_conf.config('password')

    return u, pw


class PDFViewerException(Exception):
    """
    Exceptions related to the PDF document viewer (proxy).
    """
    pass


# Number of seconds to wait on a response from the CMIS server.
TIMEOUT = 7


def cmis_auth_ticket():
    """
    Retrieves the authentication ticket for use in accessing resources in the
    CMIS server.
    :raises:
        Timeout: When the client fails to connect to the server within the
        specified timeout period.
    :return: Returns a tuple containing the HTTP response from the server and
    the Alfresco authentication ticket. If the status code in the response
    object is not 200 then the authentication ticket will be empty.
    :rtype: tuple(response, auth_ticket)
    """
    response, auth_ticket = None, ''
    u, pw = auth_credentials()

    try:
        response = requests.post(
            login_rest_url(),
            json={
                'username': u,
                'password': pw
            },
            timeout=TIMEOUT
        )
    except Timeout:
        raise PDFViewerException('Connection to server timed out')

    if response and response.status_code == 200:
        resp_body = response.json()
        if 'data' in resp_body:
            auth_ticket = resp_body['data']['ticket']

    return response, auth_ticket


# Enum of auth ticket operations
VALIDATE, LOGOUT = range(0, 2)


def _manage_auth_ticket(auth_ticket, auth_ticket_op):
    # Convenience method for validating or logging out the authentication ticket.
    req_op = None
    response = None

    if auth_ticket_op == VALIDATE:
        req_op = requests.get
    elif auth_ticket_op == LOGOUT:
        req_op = requests.delete

    if not req_op:
        raise ValueError('Request operation could not be determined.')

    auth_ticket_url = rest_ticket_url(auth_ticket)
    try:
        response = req_op(
            auth_ticket_url,
            params={
                'alf_ticket': auth_ticket
            },
            timeout=TIMEOUT
        )
    except Timeout:
        raise PDFViewerException('Connection to server timed out')

    if response and response.status_code == 200:
        return True

    return False


def is_auth_ticket_valid(auth_ticket):
    """
    Check if the given authentication ticket is valid.
    :param auth_ticket: Authentication ticket.
    :type auth_ticket: str
    :return: Returns True if the authentication ticket is valid, else False.
    :rtype: bool
    """
    return _manage_auth_ticket(auth_ticket, VALIDATE)


def logout_auth_ticket(auth_ticket):
    """
    Logout and delete authentication ticket.
    :param auth_ticket: Authentication ticket to be logged out and deleted.
    :type auth_ticket: str
    :return: Returns True if the logout was successful, else False.
    :rtype: bool
    """
    return _manage_auth_ticket(auth_ticket, LOGOUT)


class PDFViewerProxy(QObject):
    """
    Provides an interface for browsing PDF documents using Google Chrome.
    It utilizes the QProcess framework to span new processes but Google
    Chrome's process model - where one parent process spans additional child
    processes - makes is difficult to manage (i.e. close/terminate) the
    individual processes.
    """
    error = pyqtSignal(tuple)  # (document_id, error_msg)

    def __init__(self, parent=None):
        super(PDFViewerProxy, self).__init__(parent)
        self._processes = {}
        # Control whether PDF print and save operations are allowed
        # Does not control Chrome's right-click context menu
        self.restricted = True

        self._base_url = cmis_base_url()
        if not self._base_url:
            msg = self.tr(
                'Invalid base URL. Check CMIS service end point.'
            )
            raise PDFViewerException(msg)

        # CHeck Google Chrome installation
        self._chrome_installed, self._chrome_path = is_chrome_installed()
        if not self._chrome_installed:
            msg = self.tr(
                'Google Chrome is required to view PDF documents.'
            )
            raise PDFViewerException(msg)

        doc_path = '/alfresco/d/d/workspace/SpacesStore'
        self._root_doc_url = '{0}{1}'.format(
            self._base_url,
            doc_path
        )
        self._auth_ticket = None

        # Try to set the authentication ticket
        self._gen_auth_ticket()

        # Logout from the CMIS server when the object is about to be destroyed
        self.destroyed.connect(
            self.invalidate_auth_ticket
        )

    def _gen_auth_ticket(self):
        # Generate an authentication ticket that can be used in the session.
        resp, auth_ticket = cmis_auth_ticket()
        if resp.status_code != 200:
            msg = 'Status {0:d} - {1}'.format(
                resp.status_code,
                self.tr('Unable to load the document viewer as the '
                        'authentication ticket could not be created.'
                        )
            )
            raise PDFViewerException(msg)

        self._auth_ticket = auth_ticket

    def _check_auth_ticket(self):
        # Checks if the authentication ticket is valid and if not, refreshes
        # it prior to loading the document viewer.
        if not is_auth_ticket_valid(self._auth_ticket):
            self._gen_auth_ticket()

    @property
    def root_doc_url(self):
        """
        :return: Returns the root document URL which, when prefixed with the
        document ID and name, provides the absolute document URL in the CMIS
        server.
        :rtype: str
        """
        return self._root_doc_url

    @property
    def processes(self):
        """
        :return: Returns a list of running QProcess objects where each
        process corresponds to an instance of a document view in Google
        Chrome.
        :rtype: list
        """
        return self._processes.values()

    def process(self, document_id):
        """
        Gets the QProcess instance corresponding to the 'id' that was
        specified during its creation.
        :param document_id: Unique process identifier.
        :type document_id: str
        :return: Returns the QProcess instance that matches the 'id' used
        during the process creation, otherwise returns None if not found.
        :rtype: QProcess
        """
        return self._processes.get(document_id, None)

    def view_document(self, document_identifier, document_name):
        """
        Opens the document with the given unique identifier in Google Chrome.
        :param document_identifier: Unique document identifier.
        :type document_identifier: str
        :param document_name: Name of the document as stored in the CMIS
        server.
        :type document_name: str
        """
        doc_proc = QProcess(self)
        doc_proc.setProperty(DOC_ID_PROP, document_identifier)
        doc_proc.error.connect(
            self._on_error
        )

        # Full document path
        abs_doc_path = '{0}/{1}/{2}'.format(
            self._root_doc_url,
            document_identifier,
            document_name
        )
        if self.restricted:
            # abs_doc_path = '{0}#toolbar=0'.format(abs_doc_path)
            abs_doc_path = '{0}'.format(abs_doc_path)

        # Check and update authentication ticket if required
        self._check_auth_ticket()

        # Append ticket to URL
        abs_doc_path = '{0}?ticket={1}'.format(
            abs_doc_path,
            self._auth_ticket
        )

        # Build args
        cmd_inputs = []
        cmd_inputs.append(self._chrome_path)
        cmd_inputs.append('--app={0}'.format(abs_doc_path))
        cmd_path = ' '.join(cmd_inputs)

        # Add to the collection
        self._processes[document_identifier] = doc_proc

        subprocess.call(cmd_path)

    def view_from_doc_model(self, document_model):
        """
        Opens the document based on the information contained in the document
        model object.
        :param document_model: Document model object containing the document
        identifier and document name.
        :type document_model: object
        """
        self.view_document(
            document_model.document_identifier,
            document_model.name
        )

    def invalidate_auth_ticket(self):
        """
        Logs out and deletes the current authentication ticket.
        """
        if self._auth_ticket:
            logout_auth_ticket(self._auth_ticket)

    def _on_error(self, error):
        doc_id = ''
        doc_proc = self.sender()
        if doc_proc:
            doc_id = doc_proc.property(DOC_ID_PROP)

        err_msg = ''
        if error == QProcess.FailedToStart:
            err_msg = 'Viewer failed to start. Check to ensure that Chrome ' \
                      'has been installed correctly and the program has ' \
                      'sufficient permissions to invoke Chrome.'
        elif error == QProcess.Crashed:
            err_msg = 'Chrome crashed after starting.'
        elif error == QProcess.ReadError:
            err_msg = 'An error occured when attempting to read from the ' \
                      'process.'
        elif error == QProcess.UnknownError:
            err_msg = 'Unknown error.'

        # Emit signal
        self.error.emit((
            doc_id,
            err_msg
        ))