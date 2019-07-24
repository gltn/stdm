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
from cmislib import (
    CmisClient
)
from stdm.security.auth_config import (
    auth_config_from_id
)
from stdm.settings.registryconfig import (
    cmis_atom_pub_url,
    cmis_auth_config_id
)


class CmisManager(object):
    """
    Provides an interface for STDM modules to communicate with the CMIS
    server. Currently, only the Atom Pub service is supported.
    """
    def __init__(self, **kwargs):
        """
        Class constructor
        :param kwargs:
        - url: URL of the CMIS atom pub service.
        - auth_config_id: ID of the authentication configuration
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

    @property
    def default_repository(self):
        """
        :return: Returns the default repository in the document server.
        The client must have had a successfult connection to this service
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

        return rs.getResults().values()

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
        folders = self.sub_folders(parent_folder)
        if len(folders) == 0:
            return False

        status = False
        for f in folders:
            f_name = f.name
            if name == f_name:
                status = True
                break

        return status

    def upload_document(self, folder, document_path, binary_read_mode=True):
        """
        Uploads a document specified in the given file path to the CMIS
        folder. Please note that some repositories do not allow uploading
        to the root folder.
        :param folder: CMIS folder where the document will be uploaded.
        :type folder: cmislib.domain.Folder
        :param document_path: Path in the local system where containing the
        document to be uploaded to the CMIS directory.
        :type document_path: str
        :param binary_read_mode: True to read the document as a binary file
        or False to use text mode. Default is True.
        :type binary_read_mode: bool
        :return: Returns the created document object in the CMIS folder,
        else None if the document could not be uploaded.
        :rtype: cmislib.domain.Document
        """
        doc = None

        read_mode = 'rb' if binary_read_mode else 'r'
        with open(document_path, read_mode) as f:
            doc = folder.createDocument(
                'Test',
                contentFile=f
            )

        return doc






