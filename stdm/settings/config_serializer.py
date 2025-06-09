"""
/***************************************************************************
Name                 : ConfigurationWriter
Description          : Reads/writes configuration object from/to file.
Date                 : 15/February/2016
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
import logging
from collections import OrderedDict
from datetime import (
    datetime
)
from decimal import Decimal

from qgis.PyQt.QtCore import (
    QFile,
    QFileInfo,
    QIODevice,
    QObject,
    pyqtSignal
)
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement,
    QDomNode
)

from stdm.data.configfile_paths import FilePaths
from stdm.data.configuration.association_entity import AssociationEntity
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.entity import (
    BaseColumn,
    ForeignKeyColumn
)
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.entity_relation import EntityRelation
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.profile import Profile
from stdm.data.configuration.social_tenure import SocialTenure
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.value_list import ValueList
from stdm.settings.config_updaters import ConfigurationUpdater
from stdm.settings.database_updaters import DatabaseUpdater
from stdm.utils.util import (
    date_from_string,
    datetime_from_string,
    string_to_boolean
)

LOGGER = logging.getLogger('stdm')


class ConfigurationFileSerializer(QObject):
    """
    (De)serializes configuration object from/to a specified file object.
    """
    update_progress = pyqtSignal(str)
    update_complete = pyqtSignal(QDomDocument)
    db_update_progress = pyqtSignal(str)

    def __init__(self, path, parent=None):
        """
        :param path: File location where the configuration will be saved.
        :type path: str
        """
        QObject.__init__(self, parent)
        self.path = path
        self.config = StdmConfiguration.instance()
        self.file_handler = FilePaths()
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )

    def save(self):
        """
        Serialize configuration object to the given file location.
        """
        if self.config.is_null:
            raise ConfigurationException('StdmConfiguration object is null')

        if not self.path:
            raise IOError('File path for saving the configuration is empty.')

        save_file_info = QFileInfo(self.path)

        # Check if the suffix is in the file name
        # TODO: Remove str function
        if not str(save_file_info.suffix()).lower != 'stc':
            self.path = '{0}.{1}'.format(self.path, 'stc')
            save_file_info = QFileInfo(self.path)

        # Test if the file is writeable
        save_file = QFile(self.path)
        if not save_file.open(QIODevice.WriteOnly):
            raise IOError('The file cannot be saved in '
                          '{0}'.format(self.path))

        # Create DOM document and populate it with STDM config properties
        config_document = QDomDocument()
        self.write_xml(config_document)

        if save_file.write(config_document.toByteArray()) == -1:
            raise IOError('The configuration could not be written to file.')

    def write_xml(self, document):
        """
        Populate the DOM document with the configuration properties.
        :param document: DOM document to be updated.
        :type document: QDomDocument
        """
        config_element = document.createElement('Configuration')
        config_element.setAttribute('version', str(self.config.VERSION))

        # Append main element
        document.appendChild(config_element)

        # Append profile information
        for p in self.config.profiles.values():
            ProfileSerializer.write_xml(p, config_element, document)

    def load(self):
        """
        Loads the contents of the configuration file to the corresponding
        instance object.
        """
        if not QFile.exists(self.path):
            raise IOError('{0} does not exist. Configuration file cannot be '
                          'loaded.'.format(self.path))

        config_file = QFile(self.path)

        if not config_file.open(QIODevice.ReadOnly):
            raise IOError('Cannot read configuration file. Check read '
                          'permissions.')

        config_doc = QDomDocument()

        status, msg, line, col = config_doc.setContent(config_file)
        if not status:
            raise ConfigurationException('Configuration file cannot be '
                                         'loaded: {0}'.format(msg))

        # Load configuration items
        self.read_xml(config_doc)

    def update(self, document):
        """
        Tries to upgrade the configuration file specified in the DOM document
        to the current version.
        :param document: Older version of STDM config.
        :type document: QDomDocument
        :return: True if the upgrade succeeded including the updated document
        object, else False with None document object.
        :rtype: tuple(bool, QDomDocument)
        """
        self.append_log('Started the update process.')
        self.config_updater = ConfigurationUpdater(document)
        self.config_updater.update_progress.connect(
            self.on_update_progress
        )
        # TODO the on_version_updated should listen to version_updated ...
        # .... signal when schema update is refactored.
        # self.config_updater.version_updated.connect(
        #     self.on_version_updated
        # )
        self.config_updater.update_complete.connect(
            self.on_update_complete
        )

        status, dom_document = self.config_updater.exec_()
        return status, dom_document

    def on_update_complete(self, updated_document):
        """
        Loads the updated dom document into configuration instance.
        It then saves it to configuration.stc using save() method.
        :param document: The updated dom document
        :type document: QDomDocument
        :return:
        :rtype:
        """
        doc_element = updated_document.documentElement()

        self._load_config_items(doc_element)
        self.append_log(
            'Loaded the updated configuration to '
            'STDM configuration.'
        )
        self.update_progress.emit(
            'Loaded the updated configuration to '
            'STDM configuration.'
        )
        self.save()
        self.append_log(
            'Successfully created an updated configuration.stc.'
        )

        self.update_complete.emit(updated_document)

    def on_version_updated(self, document):
        """
        A slot raised on a specific config version is
        updated to backup database. But currently it is raised when
        update_complete signal is emitted.
        """
        db_updater = DatabaseUpdater(document)
        db_updater.db_update_progress.connect(self.on_db_update_progress)
        # TODO the schema updater must be refactored to update db using dom_document
        schema_updater = ConfigurationSchemaUpdater()

        schema_updater.exec_()

        #db_updater.upgrade_database()

        # Restore lost views that may have been lost during drop cascade.
        # TODO second time exec_ needs to be removed when schema updater is refactored

        #schema_updater.exec_()
        
        # TODO emit update_complete here when the schema updater is refactored

    def on_update_progress(self, message):
        """
        A slot raised when an update progress signal is emitted
        from any of the updaters through ConfigurationUpdater.
        :param message: The progress message
        :type message: String
        :return:
        :rtype:
        """
        self.update_progress.emit(message)

    def on_db_update_progress(self, message):
        """
        A slot raised when the database update progress signal is emitted.
        :param message: The progress message
        :type message: String
        """
        self.db_update_progress.emit(message)

    def read_xml(self, document):
        """
        Reads configuration file and loads contents into a configuration
        instance.
        :param document: Main document object containing config information.
        :type document: QDomDocument
        """
        # Reset items in the config file
        self.config._clear()

        # Load items afresh
        # Check tag and version attribute first
        doc_element = document.documentElement()

        if doc_element.isNull():
            # Its an older config file hence, try upgrade
            updated_document = self._update_status(document)

        if not doc_element.hasAttribute('version'):
            # Again, an older version
            updated_document = self._update_status(document)

        # Check version
        config_version = doc_element.attribute('version')
        if config_version:
            config_version = float(config_version)

        else:
            # Fatal error
            raise ConfigurationException('Error extracting version '
                                         'number from the '
                                         'configuration file.')

        if config_version < StdmConfiguration.instance().VERSION:
            # Upgrade configuration
            updated_document = self._update_status(document)

            doc_element = updated_document.documentElement()
        elif config_version == StdmConfiguration.instance().VERSION:
            doc_element = document.documentElement()

        # All should be well at this point so start parsing the items
        self._load_config_items(doc_element)

    def _load_config_items(self, element):
        # Load profiles
        profile_elements = element.elementsByTagName('Profile')

        p_count = profile_elements.count()

        for i in range(p_count):
            profile_element = profile_elements.item(i).toElement()
            profile = ProfileSerializer.read_xml(profile_element, element,
                                                 self.config)

            if profile is not None:
                profile.sort_entities()
                self.config.add_profile(profile)

            else:
                LOGGER.debug('Empty profile name in the configuration file. '
                             'Profile cannot be loaded.')

    def _update_status(self, document):
        status, doc = self.update(document)

        if not status:
            raise ConfigurationException('Configuration could not be updated. '
                                         'Please contact your system '
                                         'administrator.')

        return doc

    def append_log(self, info):
        """
        Append info to a single file
        :param info: update information to save to file
        :type info: str
        """
        info_file = open(self.log_file_path, "a")
        time_stamp = datetime.now().strftime(
            '%d-%m-%Y %H:%M:%S'
        )
        info_file.write('\n')
        info_file.write('{} - '.format(time_stamp))

        info_file.write(info)
        info_file.write('\n')
        info_file.close()


def _populate_collections_from_element(element, tag_name, collection):
    group_el = element.firstChildElement(tag_name)

    if not group_el.isNull():
        er_collection = group_el.childNodes()

        for i in range(er_collection.count()):
            er_el = er_collection.item(i).toElement()

            if er_el.hasAttribute('name'):
                name = str(er_el.attribute('name'))

                collection[name] = er_el


class ProfileSerializer:
    """
    (De)serialize profile information.
    """

    @staticmethod
    def _populate_entity_relations(element, collection):
        # Populate collection
        _populate_collections_from_element(
            element,
            'Relations',
            collection
        )

    @staticmethod
    def _populate_associations(element, collection):
        # Populate collection
        _populate_collections_from_element(
            element,
            AssociationEntitySerializer.GROUP_TAG,
            collection
        )

    @staticmethod
    def read_xml(element, config_element, configuration):
        """
        :param element: Element containing profile information.
        :type element: QDomElement
        :param config_element: Parent configuration element.
        :type config_element: QDomElement
        :param configuration: Current configuration instance.
        :type configuration: StdmConfiguration
        :return: Returns a Profile object using information contained in the
        profile element.
        :rtype: Profile
        """
        profile_name = element.attribute('name', '')
        if not profile_name:
            LOGGER.debug('Empty profile name. Profile will not be loaded.')

            return None

        # TODO: Remove unicode
        profile = Profile(str(profile_name), configuration)

        # Set description
        description = element.attribute('description', '')
        profile.description = description

        '''
        Now populate the entity relations and associations for use by child
        elements.
        '''
        association_elements = {}
        entity_relation_elements = {}
        ProfileSerializer._populate_associations(element,
                                                 association_elements)
        ProfileSerializer._populate_entity_relations(element,
                                                     entity_relation_elements)

        '''
        We resort to manually loading the entities (and subclasses) which
        have no dependencies to any parents. Start with value lists.
        '''
        value_lists_el = element.firstChildElement(ValueListSerializer.GROUP_TAG)
        if not value_lists_el.isNull():
            ValueListSerializer.read_xml(value_lists_el, profile,
                                         association_elements,
                                         entity_relation_elements)

        deferred_elements = []

        # Process entity elements with no dependency first
        child_nodes = element.childNodes()
        for i in range(child_nodes.count()):
            child_element = child_nodes.item(i).toElement()
            child_tag_name = child_element.tagName()
            item_serializer = EntitySerializerCollection.handler_by_tag_name(
                child_tag_name
            )

            if child_element.tagName() == 'Entity':
                if item_serializer is not None:
                    # Check if element has dependency
                    if not item_serializer.has_dependency(child_element):
                        item_serializer.read_xml(child_element, profile,
                                                 association_elements,
                                                 entity_relation_elements)

                    else:
                        # Queue the item - tuple containing element and serializer
                        deferred_elements.append((child_element, item_serializer))

        # Process deferred items
        for c in deferred_elements:
            el, serializer = c[0], c[1]
            '''
            serializer.read_xml(el, profile, association_elements,
                        entity_relation_elements)
            '''

            # Resolve dependency
            serializer.resolve_dependency(
                el,
                profile,
                element,
                association_elements,
                entity_relation_elements
            )

        # Set social tenure entities
        str_el = element.firstChildElement('SocialTenure')
        if not str_el.isNull():
            SocialTenureSerializer.read_xml(str_el, profile,
                                            association_elements,
                                            entity_relation_elements)

        return profile

    @staticmethod
    def entity_element(profile_element, entity_name):
        """
        Searches the profile for an entity with the given short name.
        :param profile_element: Profile element to search.
        :type profile_element: QDomElement
        :param entity_name: Entity short name to search for.
        :rtype: str
        :return: Entity element with the corresponding short name, else None
        if not found.
        :rtype: QDomElement
        """
        e_element = None

        entity_el_list = profile_element.elementsByTagName('Entity')

        for i in range(entity_el_list.count()):
            entity_element = entity_el_list.item(i).toElement()
            entity_attribute = entity_element.attribute(
                EntitySerializer.SHORT_NAME,
                ''
            )

            if entity_attribute == entity_name:
                e_element = entity_element

                break

        return e_element

    @staticmethod
    def write_xml(profile, parent_node, document):
        """
        Appends profile information to the parent node.
        :param profile: Profile object
        :type profile: Profile
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        profile_element = document.createElement('Profile')

        profile_element.setAttribute('name', profile.name)
        profile_element.setAttribute('description', profile.description)

        # Append entity information
        for e in profile.entities.values():
            item_serializer = EntitySerializerCollection.handler(e.TYPE_INFO)

            if item_serializer:
                item_serializer.write_xml(e, profile_element, document)

        # Append entity relation information
        er_parent_element = document.createElement('Relations')
        for er in profile.relations.values():
            EntityRelationSerializer.write_xml(er, er_parent_element, document)

        profile_element.appendChild(er_parent_element)

        # Append social tenure information
        SocialTenureSerializer.write_xml(profile.social_tenure,
                                         profile_element, document)

        parent_node.appendChild(profile_element)


class SocialTenureSerializer:
    """
    (De)serializes social tenure information.
    """
    PARTY = 'party'
    SPATIAL_UNIT = 'spatialUnit'
    TENURE_TYPE = 'tenureTypeList'
    LAYER_DISPLAY = 'layerDisplay'
    MULTIPARTY = 'supportsMultipleParties'
    VALIDITY_TAG = 'Validity'
    START_TAG = 'Start'
    END_TAG = 'End'
    MINIMUM = 'minimum'
    MAXIMUM = 'maximum'
    SP_TENURE_MAPPINGS = 'SpatialUnitTenureMappings'
    SP_TENURE_MAPPING = 'Mapping'
    T_TYPE_ATTRS = 'CustomAttributes'
    T_ATTRS_ENTITY = 'TenureEntity'
    ENTITY = 'entity'

    @staticmethod
    def read_xml(child_element, profile, association_elements,
                 entity_relation_elements):
        """
        Reads the social tenure attributes in the child element and set them
        in the profile.
        :param child_element: Element containing social tenure information.
        :type child_element: QDomElement
        :param profile: Profile object whose STR attributes are to be set.
        :type profile: Profile
        """
        party = str(child_element.attribute(
            SocialTenureSerializer.PARTY, '')
        ).strip()
        spatial_unit = str(child_element.attribute(
            SocialTenureSerializer.SPATIAL_UNIT, '')
        ).strip()
        layer_display = str(child_element.attribute(
            SocialTenureSerializer.LAYER_DISPLAY, '')
        )
        multi_party = str(child_element.attribute(
            SocialTenureSerializer.MULTIPARTY, '')
        )

        # Set STR attributes
        if party:
            # Get list of party names
            parties = party.split(',')
            parties = [p.strip() for p in parties]
            profile.set_social_tenure_attr(SocialTenure.PARTY, parties)

        if spatial_unit:
            # Get list of spatial unit names
            sp_units = spatial_unit.split(',')
            sp_units = [sp.strip() for sp in sp_units]
            profile.set_social_tenure_attr(
                SocialTenure.SPATIAL_UNIT,
                sp_units
            )

        if layer_display:
            profile.social_tenure.layer_display_name = layer_display

        if multi_party:
            profile.social_tenure.multi_party = _str_to_bool(multi_party)

        # Set start validity ranges
        start_min_dt = SocialTenureSerializer._read_validity_date(
            child_element,
            SocialTenureSerializer.START_TAG,
            SocialTenureSerializer.MINIMUM
        )
        start_max_dt = SocialTenureSerializer._read_validity_date(
            child_element,
            SocialTenureSerializer.START_TAG,
            SocialTenureSerializer.MAXIMUM
        )
        if start_min_dt is not None and start_max_dt is not None:
            profile.set_social_tenure_attr(
                SocialTenure.START_DATE,
                (start_min_dt, start_max_dt)
            )

        # Set end validity ranges
        end_min_dt = SocialTenureSerializer._read_validity_date(
            child_element,
            SocialTenureSerializer.END_TAG,
            SocialTenureSerializer.MINIMUM
        )
        end_max_dt = SocialTenureSerializer._read_validity_date(
            child_element,
            SocialTenureSerializer.END_TAG,
            SocialTenureSerializer.MAXIMUM
        )
        if end_min_dt is not None and end_max_dt is not None:
            profile.set_social_tenure_attr(
                SocialTenure.END_DATE,
                (end_min_dt, end_max_dt)
            )

        # Set spatial unit tenure mapping
        sp_tenure_mapping_els = child_element.elementsByTagName(
            SocialTenureSerializer.SP_TENURE_MAPPINGS
        )
        if sp_tenure_mapping_els.count() > 0:
            sp_tenure_mapping_node = sp_tenure_mapping_els.item(0)
            sp_tenure_mapping_el = sp_tenure_mapping_node.toElement()

            sp_t_mapping_nodes = sp_tenure_mapping_el.childNodes()
            for i in range(sp_t_mapping_nodes.count()):
                t_mapping_el = sp_t_mapping_nodes.item(i).toElement()
                sp_unit = t_mapping_el.attribute(
                    SocialTenureSerializer.SPATIAL_UNIT,
                    ''
                )
                tenure_list = t_mapping_el.attribute(
                    SocialTenureSerializer.TENURE_TYPE,
                    ''
                )
                profile.social_tenure.add_spatial_tenure_mapping(
                    sp_unit,
                    tenure_list
                )

        # Set tenure type custom attributes
        custom_attrs_ent_els = child_element.elementsByTagName(
            SocialTenureSerializer.T_TYPE_ATTRS
        )
        if custom_attrs_ent_els.count() > 0:
            attrs_ent_node = custom_attrs_ent_els.item(0)
            attrs_ent_el = attrs_ent_node.toElement()

            attrs_nodes = attrs_ent_el.childNodes()
            for i in range(attrs_nodes.count()):
                custom_ent_el = attrs_nodes.item(i).toElement()
                t_type = custom_ent_el.attribute(
                    SocialTenureSerializer.TENURE_TYPE,
                    ''
                )
                custom_ent = custom_ent_el.attribute(
                    SocialTenureSerializer.ENTITY,
                    ''
                )
                profile.social_tenure.add_tenure_attr_custom_entity(
                    t_type,
                    custom_ent
                )

    @staticmethod
    def _read_validity_date(str_element, tag_name, min_max):
        # Returns the validity start/end minimum/maximum dates
        validities = str_element.elementsByTagName(
            SocialTenureSerializer.VALIDITY_TAG
        )
        if validities.count() == 0:
            return None

        validity_node = validities.item(0)
        validity_el = validity_node.toElement()

        if tag_name == SocialTenureSerializer.START_TAG:
            start_tags = validity_el.elementsByTagName(
                SocialTenureSerializer.START_TAG
            )
            if start_tags.count() == 0:
                return None

            start_node = start_tags.item(0)
            start_el = start_node.toElement()

            if start_el.hasAttribute(min_max):
                return date_from_string(start_el.attribute(min_max))
            else:
                return None

        if tag_name == SocialTenureSerializer.END_TAG:
            end_tags = validity_el.elementsByTagName(
                SocialTenureSerializer.END_TAG
            )
            if end_tags.count() == 0:
                return None

            end_node = end_tags.item(0)
            end_el = end_node.toElement()

            if end_el.hasAttribute(min_max):
                return date_from_string(end_el.attribute(min_max))
            else:
                return None

        return None

    @staticmethod
    def write_xml(social_tenure, parent_node, document):
        """
        Appends social tenure information to the profile node.
        :param social_tenure: Social tenure object
        :type social_tenure: SocialTenure
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        party_names = [p.short_name for p in social_tenure.parties]
        cs_party_names = ','.join(party_names)

        social_tenure_element = document.createElement('SocialTenure')

        social_tenure_element.setAttribute(
            SocialTenureSerializer.PARTY,
            cs_party_names
        )

        # Add spatial unit names
        sp_unit_names = [sp.short_name for sp in social_tenure.spatial_units]
        cs_sp_unit_names = ','.join(sp_unit_names)

        social_tenure_element.setAttribute(
            SocialTenureSerializer.SPATIAL_UNIT,
            cs_sp_unit_names
        )

        social_tenure_element.setAttribute(SocialTenureSerializer.TENURE_TYPE,
                                           social_tenure.tenure_type_collection.short_name)
        social_tenure_element.setAttribute(SocialTenureSerializer.LAYER_DISPLAY,
                                           social_tenure.layer_display())
        social_tenure_element.setAttribute(SocialTenureSerializer.MULTIPARTY,
                                           str(social_tenure.multi_party))

        # Append validity dates if specified (v1.5)
        if social_tenure.validity_start_column.minimum > social_tenure.validity_start_column.SQL_MIN:
            # Add minimum date
            SocialTenureSerializer._add_validity(
                social_tenure_element,
                document,
                SocialTenureSerializer.START_TAG,
                SocialTenureSerializer.MINIMUM,
                social_tenure.validity_start_column.minimum
            )

        if social_tenure.validity_start_column.maximum < social_tenure.validity_start_column.SQL_MAX:
            # Add maximum date
            SocialTenureSerializer._add_validity(
                social_tenure_element,
                document,
                SocialTenureSerializer.START_TAG,
                SocialTenureSerializer.MAXIMUM,
                social_tenure.validity_start_column.maximum
            )

        if social_tenure.validity_end_column.minimum > social_tenure.validity_end_column.SQL_MIN:
            # Add minimum date
            SocialTenureSerializer._add_validity(
                social_tenure_element,
                document,
                SocialTenureSerializer.END_TAG,
                SocialTenureSerializer.MINIMUM,
                social_tenure.validity_end_column.minimum
            )

        if social_tenure.validity_end_column.maximum < social_tenure.validity_end_column.SQL_MAX:
            # Add maximum date
            SocialTenureSerializer._add_validity(
                social_tenure_element,
                document,
                SocialTenureSerializer.END_TAG,
                SocialTenureSerializer.MAXIMUM,
                social_tenure.validity_end_column.maximum
            )

        # Set spatial unit mapping (v1.7)
        sp_unit_tenure_mapping_root_el = document.createElement(
            SocialTenureSerializer.SP_TENURE_MAPPINGS
        )
        for sp, tvl in social_tenure.spatial_units_tenure.items():
            t_mapping_el = document.createElement(
                SocialTenureSerializer.SP_TENURE_MAPPING
            )
            t_mapping_el.setAttribute(
                SocialTenureSerializer.SPATIAL_UNIT,
                sp
            )
            t_mapping_el.setAttribute(
                SocialTenureSerializer.TENURE_TYPE,
                tvl.short_name
            )
            sp_unit_tenure_mapping_root_el.appendChild(t_mapping_el)

        social_tenure_element.appendChild(sp_unit_tenure_mapping_root_el)

        # Set tenure type - custom attribute mapping
        custom_attrs_root_el = document.createElement(
            SocialTenureSerializer.T_TYPE_ATTRS
        )
        for t, ent in social_tenure.custom_attribute_entities.items():
            t_ent_el = document.createElement(
                SocialTenureSerializer.T_ATTRS_ENTITY
            )
            t_ent_el.setAttribute(
                SocialTenureSerializer.TENURE_TYPE,
                t
            )
            t_ent_el.setAttribute(
                SocialTenureSerializer.ENTITY,
                ent.short_name
            )
            custom_attrs_root_el.appendChild(t_ent_el)

        social_tenure_element.appendChild(custom_attrs_root_el)

        parent_node.appendChild(social_tenure_element)

    @staticmethod
    def _add_validity(str_element, document, tag_name, min_max, value):
        # Get validity node
        validities = str_element.elementsByTagName(
            SocialTenureSerializer.VALIDITY_TAG
        )
        if validities.count() == 0:
            validity_el = document.createElement(
                SocialTenureSerializer.VALIDITY_TAG
            )
            str_element.appendChild(validity_el)
        else:
            validity_node = validities.item(0)
            validity_el = validity_node.toElement()

        # Append start date
        if tag_name == SocialTenureSerializer.START_TAG:
            start_tags = validity_el.elementsByTagName(
                SocialTenureSerializer.START_TAG
            )
            if start_tags.count() == 0:
                start_el = document.createElement(
                    SocialTenureSerializer.START_TAG
                )
                validity_el.appendChild(start_el)
            else:
                start_node = start_tags.item(0)
                start_el = start_node.toElement()

            # Set minimum or maximum
            start_el.setAttribute(min_max, str(value))

        # Append end date
        if tag_name == SocialTenureSerializer.END_TAG:
            end_tags = validity_el.elementsByTagName(
                SocialTenureSerializer.END_TAG
            )
            if end_tags.count() == 0:
                end_el = document.createElement(
                    SocialTenureSerializer.END_TAG
                )
                validity_el.appendChild(end_el)
            else:
                end_node = end_tags.item(0)
                end_el = end_node.toElement()

            # Set minimum or maximum
            end_el.setAttribute(min_max, str(value))


class EntitySerializerCollection:
    """
    Container for entity-based serializers which are registered using the
    type info of the Entity subclass.
    """
    _registry = OrderedDict()

    @classmethod
    def register(cls):
        if not hasattr(cls, 'ENTITY_TYPE_INFO'):
            return

        EntitySerializerCollection._registry[cls.ENTITY_TYPE_INFO] = cls

    @staticmethod
    def handler(type_info):
        return EntitySerializerCollection._registry.get(type_info, None)

    @classmethod
    def entry_tag_name(cls):
        if hasattr(cls, 'GROUP_TAG'):
            return cls.GROUP_TAG

        return cls.TAG_NAME

    @staticmethod
    def handler_by_tag_name(tag_name):
        handler = [s for s in EntitySerializerCollection._registry.values()
                   if s.entry_tag_name() == tag_name]

        if len(handler) == 0:
            return None

        return handler[0]

    @classmethod
    def has_dependency(cls, element):
        """
        :param element: Element containing entity information.
        :type element: QDomElement
        :return: Return True if the entity element has columns that are
        dependent on other entities such as foreign key columns.Default is
        False.
        :rtype: bool
        """
        return False

    @classmethod
    def group_element(cls, parent_node, document):
        """
        Creates a parent/group element which is then used as the parent node
        for this serializer. If no 'GROUP_TAG' class attribute is specified
        then the profile node is returned.
        :param parent_node: Parent node corresponding to the profile node,
        :type parent_node: QDomNode
        :param document: main document object.
        :type document: QDomDocument
        :return: Prent/group node fpr appending the child node created by
        this serializer.
        :rtype: QDomNode
        """
        if not hasattr(cls, 'GROUP_TAG'):
            return parent_node

        group_tag = getattr(cls, 'GROUP_TAG')

        # Search for group element and create if it does not exist
        group_element = parent_node.firstChildElement(group_tag)

        if group_element.isNull():
            group_element = document.createElement(group_tag)
            parent_node.appendChild(group_element)

        return group_element


class EntitySerializer(EntitySerializerCollection):
    """
    (De)serializes entity information.
    """
    TAG_NAME = 'Entity'

    # Specify attribute names
    GLOBAL = 'global'
    SHORT_NAME = 'shortName'
    NAME = 'name'
    DESCRIPTION = 'description'
    ASSOCIATIVE = 'associative'
    EDITABLE = 'editable'
    CREATE_ID = 'createId'
    PROXY = 'proxy'
    SUPPORTS_DOCUMENTS = 'supportsDocuments'
    DOCUMENT_TYPE_LOOKUP = 'documentTypeLookup'
    ENTITY_TYPE_INFO = 'ENTITY'
    ROW_INDEX = 'rowindex'
    LABEL = 'label'
    DEPENDENCY_FLAGS = [ForeignKeyColumn.TYPE_INFO]

    @staticmethod
    def read_xml(child_element, profile, association_elements,
                 entity_relation_elements):
        """
        Reads entity information in the entity element and add to the profile.
        :param child_element: Element containing entity information.
        :type child_element: QDomElement
        :param profile: Profile object to be populated with the entity
        information.
        :type profile: Profile
        """
        short_name = str(child_element.attribute(
            EntitySerializer.SHORT_NAME, '')
        )
        if short_name:
            optional_args = {}

            # Check global
            is_global = str(child_element.attribute(
                EntitySerializer.GLOBAL, '')
            )
            if is_global:
                is_global = _str_to_bool(is_global)
                optional_args['is_global'] = is_global

            # Proxy
            proxy = str(child_element.attribute(
                EntitySerializer.PROXY, '')
            )
            if proxy:
                proxy = _str_to_bool(proxy)
                optional_args['is_proxy'] = proxy

            # Create ID
            create_id = str(child_element.attribute(
                EntitySerializer.CREATE_ID, '')
            )
            if create_id:
                create_id = _str_to_bool(create_id)
                optional_args['create_id_column'] = create_id

            # Supports documents
            supports_docs = str(child_element.attribute(
                EntitySerializer.SUPPORTS_DOCUMENTS, '')
            )
            if supports_docs:
                supports_docs = _str_to_bool(supports_docs)
                optional_args['supports_documents'] = supports_docs

            ent = Entity(short_name, profile, **optional_args)

            # Associative
            associative = str(child_element.attribute(
                EntitySerializer.ASSOCIATIVE, '')
            )
            if associative:
                associative = _str_to_bool(associative)
                ent.is_associative = associative

            # Editable
            editable = str(child_element.attribute(
                EntitySerializer.EDITABLE, '')
            )
            if editable:
                editable = _str_to_bool(editable)
                ent.user_editable = editable

            # Description
            description = str(child_element.attribute(
                EntitySerializer.DESCRIPTION, '')
            )
            ent.description = description

            # RowIndex
            row_index = str(child_element.attribute(
                EntitySerializer.ROW_INDEX, '')
            )
            if row_index:
                row_index = str(row_index)
                ent.row_index = int(row_index)

            # Label
            label = str(child_element.attribute(
                EntitySerializer.LABEL, '')
            )
            ent.label = label

            # Add entity to the profile so that it is discoverable
            profile.add_entity(ent)

            column_elements = EntitySerializer.column_elements(child_element)

            for ce in column_elements:
                # Just validate that it is a 'Column' element
                if str(ce.tagName()) == 'Column':
                    '''
                    Read element and load the corresponding column object
                    into the entity.
                    '''

                    ColumnSerializerCollection.read_xml(ce, ent,
                                                        association_elements,
                                                        entity_relation_elements)

    @staticmethod
    def column_elements(entity_element):
        """
        Parses the entity element and returns a list of column elements.
        :param entity_element: Element containing entity information.
        :type entity_element: QDomElement
        :return: A list of elements containing column information.
        :rtype: list
        """
        col_els = []

        cols_group_el = entity_element.firstChildElement('Columns')

        if not cols_group_el.isNull():
            # Populate columns in the entity
            column_elements = cols_group_el.childNodes()

            for i in range(column_elements.count()):
                column_el = column_elements.item(i).toElement()

                col_els.append(column_el)

        return col_els

    @classmethod
    def has_dependency(cls, element):
        """
        :param element: Element containing entity information.
        :type element: QDomElement
        :return: Return True if the entity element has columns that are
        dependent on other entities such as foreign key columns.Default is
        False.
        :rtype: bool
        """
        dep_cols = EntitySerializer._dependency_columns(element)
        if len(dep_cols) == 0:
            return False

        return True

    @classmethod
    def _dependency_columns(cls, element):
        # Returns a list of dependency column elements
        dep_col_elements = []

        column_elements = EntitySerializer.column_elements(element)

        for ce in column_elements:
            if ce.hasAttribute('TYPE_INFO'):
                type_info = str(ce.attribute('TYPE_INFO'))

                # Check if the type info is in the flags' list
                if type_info in cls.DEPENDENCY_FLAGS:
                    dep_col_elements.append(ce)

        return dep_col_elements

    @classmethod
    def resolve_dependency(
            cls,
            element,
            profile,
            profile_element,
            association_elements,
            entity_relation_elements
    ):
        """
        Performs a depth-first addition of an entity to a profile by
        recursively cascading all related entities first.
        :param element: Element representing the entity.
        :type element: QDomElement
        :param profile: Profile object to be populated with the entity
        information.
        :type profile: Profile
        """
        dep_cols = EntitySerializer._dependency_columns(element)

        # Add entity directly if there are no dependency columns
        if len(dep_cols) == 0:
            EntitySerializer.read_xml(
                element,
                profile,
                association_elements,
                entity_relation_elements
            )

            return

        for c in dep_cols:
            # Get foreign key columns
            type_info = str(c.attribute('TYPE_INFO'))

            if type_info == ForeignKeyColumn.TYPE_INFO:
                # Get relation element
                er_element = ForeignKeyColumnSerializer.entity_relation_element(c)
                relation_name = str(er_element.attribute('name', ''))
                er_element = entity_relation_elements.get(relation_name, None)

                if er_element is not None:
                    # Get parent
                    parent = str(
                        er_element.attribute(
                            EntityRelationSerializer.PARENT,
                            ''
                        )
                    )

                    # Get parent entity element
                    if parent:
                        parent_element = ProfileSerializer.entity_element(
                            profile_element,
                            parent
                        )

                        if parent_element is not None:
                            # Check if parent has dependency
                            if EntitySerializer.has_dependency(parent_element):
                                # Resolve dependency
                                EntitySerializer.resolve_dependency(
                                    parent_element,
                                    profile,
                                    profile_element,
                                    association_elements,
                                    entity_relation_elements
                                )

                            # No more dependencies
                            else:
                                EntitySerializer.read_xml(
                                    parent_element,
                                    profile,
                                    association_elements,
                                    entity_relation_elements
                                )

        # Now add entity to profile
        EntitySerializer.read_xml(
            element,
            profile,
            association_elements,
            entity_relation_elements
        )

    @staticmethod
    def write_xml(entity, parent_node, document):
        """
        ""
        Appends entity information to the profile node.
        :param entity: Social tenure object
        :type entity: SocialTenure
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        entity_element = document.createElement(EntitySerializer.TAG_NAME)

        # Set entity attributes
        entity_element.setAttribute(EntitySerializer.GLOBAL,
                                    str(entity.is_global))
        entity_element.setAttribute(EntitySerializer.SHORT_NAME,
                                    entity.short_name)
        # Name will be ignored when the deserializing the entity object
        entity_element.setAttribute(EntitySerializer.NAME,
                                    entity.name)
        entity_element.setAttribute(EntitySerializer.DESCRIPTION,
                                    entity.description)
        entity_element.setAttribute(EntitySerializer.ASSOCIATIVE,
                                    str(entity.is_associative))
        entity_element.setAttribute(EntitySerializer.EDITABLE,
                                    str(entity.user_editable))
        entity_element.setAttribute(EntitySerializer.CREATE_ID,
                                    str(entity.create_id_column))
        entity_element.setAttribute(EntitySerializer.PROXY,
                                    str(entity.is_proxy))
        entity_element.setAttribute(EntitySerializer.SUPPORTS_DOCUMENTS,
                                    str(entity.supports_documents))
        entity_element.setAttribute(EntitySerializer.ROW_INDEX,
                                    str(entity.row_index))
        entity_element.setAttribute(EntitySerializer.LABEL,
                                    entity.label)

        # Set document type lookup
        if entity.supports_documents:
            doc_type_lookup = entity.supporting_doc.document_type_entity
            entity_element.setAttribute(EntitySerializer.DOCUMENT_TYPE_LOOKUP,
                                        str(doc_type_lookup.short_name))

        # Root columns element
        columns_element = document.createElement('Columns')

        # Append column information
        for c in entity.columns.values():
            column_serializer = ColumnSerializerCollection.handler(c.TYPE_INFO)

            if column_serializer:
                column_serializer.write_xml(c, columns_element, document)

        entity_element.appendChild(columns_element)

        parent_node.appendChild(entity_element)


EntitySerializer.register()


class AssociationEntitySerializer(EntitySerializerCollection):
    """
    (De)serializes association entity information.
    """
    GROUP_TAG = 'Associations'
    TAG_NAME = 'Association'

    # Attribute names
    FIRST_PARENT = 'firstParent'
    SECOND_PARENT = 'secondParent'

    # Corresponding type info to (de)serialize
    ENTITY_TYPE_INFO = 'ASSOCIATION_ENTITY'

    @staticmethod
    def read_xml(element, profile, association_elements,
                 entity_relation_elements):
        """
        Reads association information from the element.
        :param child_element: Element containing association entity
        information.
        :type child_element: QDomElement
        :param profile: Profile object to be populated with the association
        entity information.
        :type profile: Profile
        :return: Association entity object.
        :rtype: AssociationEntity
        """
        ae = None

        short_name = element.attribute(EntitySerializer.SHORT_NAME, '')
        if short_name:
            ae = AssociationEntity(str(short_name), profile)

            first_parent = element.attribute(
                AssociationEntitySerializer.FIRST_PARENT, '')
            second_parent = element.attribute(
                AssociationEntitySerializer.SECOND_PARENT, '')

            ae.first_parent = str(first_parent)
            ae.second_parent = str(second_parent)

        return ae

    @staticmethod
    def write_xml(association_entity, parent_node, document):
        """
        ""
        Appends association entity information to the profile node.
        :param value_list: Association entity object
        :type value_list: AssociationEntity
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        assoc_entity_element = document.createElement(AssociationEntitySerializer.TAG_NAME)

        assoc_entity_element.setAttribute(EntitySerializer.NAME,
                                          association_entity.name)
        assoc_entity_element.setAttribute(EntitySerializer.SHORT_NAME,
                                          association_entity.short_name)

        assoc_entity_element.setAttribute(AssociationEntitySerializer.FIRST_PARENT,
                                          association_entity.first_parent.short_name)
        assoc_entity_element.setAttribute(AssociationEntitySerializer.SECOND_PARENT,
                                          association_entity.second_parent.short_name)

        group_node = AssociationEntitySerializer.group_element(parent_node, document)

        group_node.appendChild(assoc_entity_element)


AssociationEntitySerializer.register()


class ValueListSerializer(EntitySerializerCollection):
    """
    (De)serializes ValueList information.
    """
    GROUP_TAG = 'ValueLists'
    TAG_NAME = 'ValueList'
    CODE_VALUE_TAG = 'CodeValue'

    # Attribute names
    NAME = 'name'
    CV_CODE = 'code'
    CV_VALUE = 'value'

    # Corresponding type info to (de)serialize
    ENTITY_TYPE_INFO = 'VALUE_LIST'

    @staticmethod
    def read_xml(child_element, profile, association_elements,
                 entity_relation_elements):
        """
        Reads the items in the child list element and add to the profile.
        If child element is a group element then children nodes are also
        extracted.
        :param child_element: Element containing value list information.
        :type child_element: QDomElement
        :param profile: Profile object to be populated with the value list
        information.
        :type profile: Profile
        """
        value_list_elements = child_element.elementsByTagName(
            ValueListSerializer.TAG_NAME
        )

        for i in range(value_list_elements.count()):
            value_list_el = value_list_elements.item(i).toElement()
            name = value_list_el.attribute('name', '')
            if name:
                value_list = ValueList(str(name), profile)

                # Get code values
                cd_elements = value_list_el.elementsByTagName(
                    ValueListSerializer.CODE_VALUE_TAG
                )

                for c in range(cd_elements.count()):
                    cd_el = cd_elements.item(c).toElement()
                    code = cd_el.attribute(ValueListSerializer.CV_CODE, '')
                    value = cd_el.attribute(ValueListSerializer.CV_VALUE, '')

                    # Add lookup items only when value is not empty
                    if value:
                        value_list.add_value(value, code)

                # Check if the value list is for tenure types
                if name == 'check_tenure_type':
                    profile.set_social_tenure_attr(SocialTenure.SOCIAL_TENURE_TYPE,
                                                   value_list)

                elif name == 'check_social_tenure_relationship_document_type':
                    tenure_doc_type_t_name = profile.social_tenure.supporting_doc. \
                        document_type_entity.short_name
                    vl_doc_type = profile.entity(tenure_doc_type_t_name)

                    if vl_doc_type is not None:
                        vl_doc_type.copy_from(value_list, True)

                else:
                    # Add value list to the profile
                    profile.add_entity(value_list)

    # Specify attribute names
    @staticmethod
    def write_xml(value_list, parent_node, document):
        """
        ""
        Appends value list information to the profile node.
        :param value_list: Value list object
        :type value_list: ValueList
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        value_list_element = document.createElement(ValueListSerializer.TAG_NAME)

        value_list_element.setAttribute(ValueListSerializer.NAME,
                                        value_list.short_name)

        # Add code value elements
        for cv in value_list.values.values():
            cd_element = document.createElement(ValueListSerializer.CODE_VALUE_TAG)

            cd_element.setAttribute(ValueListSerializer.CV_VALUE, cv.value)
            cd_element.setAttribute(ValueListSerializer.CV_CODE, cv.code)

            value_list_element.appendChild(cd_element)

        group_node = ValueListSerializer.group_element(parent_node, document)

        group_node.appendChild(value_list_element)


ValueListSerializer.register()


class EntityRelationSerializer:
    """
    (De)serializes EntityRelation information.
    """
    TAG_NAME = 'EntityRelation'

    NAME = 'name'
    PARENT = 'parent'
    PARENT_COLUMN = 'parentColumn'
    CHILD = 'child'
    CHILD_COLUMN = 'childColumn'
    DISPLAY_COLUMNS = 'displayColumns'
    SHOW_IN_PARENT = 'showInParent'
    SHOW_IN_CHILD = 'showInChild'

    @staticmethod
    def read_xml(element, profile, association_elements,
                 entity_relation_elements):
        """
        Reads entity relation information from the element object.
        :param element: Element object containing entity relation information.
        :type element: QDomElement
        :param profile: Profile object that the entity relations belongs to.
        :type profile: Profile
        :param association_elements: Collection of QDomElements containing
        association entity information.
        :type association_elements: dict
        :param entity_relation_elements: Collection of QDomElements
        containing entity relation information.
        :type entity_relation_elements: dict
        :return: Returns an EntityRelation object constructed from the
        information contained in the element.
        :rtype: EntityRelation
        """
        kw = {}
        kw['parent'] = str(
            element.attribute(EntityRelationSerializer.PARENT, '')
        )
        kw['child'] = str(
            element.attribute(EntityRelationSerializer.CHILD, '')
        )
        kw['parent_column'] = str(
            element.attribute(EntityRelationSerializer.PARENT_COLUMN, '')
        )
        kw['child_column'] = str(
            element.attribute(EntityRelationSerializer.CHILD_COLUMN, '')
        )
        kw['show_in_parent'] = str(
            element.attribute(EntityRelationSerializer.SHOW_IN_PARENT, 'True')
        )
        kw['show_in_child'] = str(
            element.attribute(EntityRelationSerializer.SHOW_IN_CHILD, 'True')
        )
        dc_str = str(
            element.attribute(EntityRelationSerializer.DISPLAY_COLUMNS, '')
        )

        if not dc_str:
            dc = []
        else:
            dc = dc_str.split(',')
        kw['display_columns'] = dc

        er = EntityRelation(profile, **kw)

        return er

    @staticmethod
    def write_xml(entity_relation, parent_node, document):
        """
        Appends entity relation information to the parent node.
        :param entity_relation: Entity relation object.
        :type entity_relation: EntityRelation
        :param parent_node: Parent node.
        :type parent_node: QDomNode
        :param document: Main document object
        :type document: QDomDocument
        """
        er_element = document.createElement(EntityRelationSerializer.TAG_NAME)

        # Set attributes
        er_element.setAttribute(EntityRelationSerializer.NAME,
                                entity_relation.name)
        er_element.setAttribute(EntityRelationSerializer.PARENT,
                                entity_relation.parent.short_name)
        er_element.setAttribute(EntityRelationSerializer.PARENT_COLUMN,
                                entity_relation.parent_column)
        er_element.setAttribute(EntityRelationSerializer.CHILD,
                                entity_relation.child.short_name)
        er_element.setAttribute(EntityRelationSerializer.CHILD_COLUMN,
                                entity_relation.child_column)
        er_element.setAttribute(EntityRelationSerializer.DISPLAY_COLUMNS,
                                ','.join(entity_relation.display_cols))
        er_element.setAttribute(EntityRelationSerializer.SHOW_IN_PARENT,
                                str(entity_relation.show_in_parent))
        er_element.setAttribute(EntityRelationSerializer.SHOW_IN_CHILD,
                                str(entity_relation.show_in_child))
        parent_node.appendChild(er_element)


class ColumnSerializerCollection:
    """
    Container for column-based serializers which are registered using the
    type info of the column subclass.
    """
    _registry = {}
    TAG_NAME = 'Column'

    # Attribute names
    DESCRIPTION = 'description'
    NAME = 'name'
    INDEX = 'index'
    MANDATORY = 'mandatory'
    SEARCHABLE = 'searchable'
    UNIQUE = 'unique'
    USER_TIP = 'tip'
    MINIMUM = 'minimum'
    MAXIMUM = 'maximum'
    LABEL = 'label'
    ROW_INDEX = 'rowindex'  # for ordering on a listview

    @classmethod
    def register(cls):
        if not hasattr(cls, 'COLUMN_TYPE_INFO'):
            return

        ColumnSerializerCollection._registry[cls.COLUMN_TYPE_INFO] = cls

    @staticmethod
    def handler_by_element(element):
        t_info = str(ColumnSerializerCollection.type_info(element))

        if not t_info:
            return None

        return ColumnSerializerCollection.handler(t_info)

    @staticmethod
    def type_info(element):
        return element.attribute('TYPE_INFO', '')

    @staticmethod
    def read_xml(element, entity, association_elements,
                 entity_relation_elements):
        column_handler = ColumnSerializerCollection.handler_by_element(
            element
        )

        if column_handler is not None:
            column_handler.read(element, entity, association_elements,
                                entity_relation_elements)

    @classmethod
    def read(cls, element, entity, association_elements,
             entity_relation_elements):
        col_type_info = str(ColumnSerializerCollection.type_info(element))
        if not col_type_info:
            return

        # Get column attributes
        name = str(element.attribute(ColumnSerializerCollection.NAME, ''))
        if not name:
            return

        kwargs = {}

        # Description
        description = str(
            element.attribute(ColumnSerializerCollection.DESCRIPTION, '')
        )
        kwargs['description'] = description

        # Index
        index = str(
            element.attribute(ColumnSerializerCollection.INDEX, 'False')
        )
        kwargs['index'] = _str_to_bool(index)

        # Mandatory
        mandatory = str(
            element.attribute(ColumnSerializerCollection.MANDATORY, 'False')
        )
        kwargs['mandatory'] = _str_to_bool(mandatory)

        # Searchable
        searchable = str(
            element.attribute(ColumnSerializerCollection.SEARCHABLE, 'False')
        )
        kwargs['searchable'] = _str_to_bool(searchable)

        # Unique
        unique = str(
            element.attribute(ColumnSerializerCollection.UNIQUE, 'False')
        )
        kwargs['unique'] = _str_to_bool(unique)

        # User tip
        user_tip = str(
            element.attribute(ColumnSerializerCollection.USER_TIP, '')
        )
        kwargs['user_tip'] = user_tip

        # Label
        label = str(
            element.attribute(ColumnSerializerCollection.LABEL, '')
        )
        kwargs['label'] = label

        # Row Index - for ordering on a viewer
        row_index = str(
            element.attribute(ColumnSerializerCollection.ROW_INDEX, '')
        )
        kwargs['row_index'] = row_index

        # Minimum
        if element.hasAttribute(ColumnSerializerCollection.MINIMUM):
            minimum = element.attribute(ColumnSerializerCollection.MINIMUM)
            '''
            The value is not set if an exception is raised. Type will
            use defaults.
            '''
            try:
                kwargs['minimum'] = cls._convert_bounds_type(minimum)
            except ValueError:
                pass

        # Maximum
        if element.hasAttribute(ColumnSerializerCollection.MAXIMUM):
            maximum = element.attribute(ColumnSerializerCollection.MAXIMUM)

            try:
                kwargs['maximum'] = cls._convert_bounds_type(maximum)
            except ValueError:
                pass

        # Mandatory arguments
        args = [name, entity]

        # Custom arguments provided by subclasses
        custom_args, custom_kwargs = cls._obj_args(args, kwargs, element,
                                                   association_elements,
                                                   entity_relation_elements)

        # Get column type based on type info
        column_cls = BaseColumn.column_type(col_type_info)

        if column_cls is not None:
            column = column_cls(*custom_args, **custom_kwargs)

            # Append column to the entity
            entity.add_column(column)

    @classmethod
    def _obj_args(cls, args, kwargs, element, associations, entity_relations):
        """
        To be implemented by subclasses if they want to pass additional
        or modify existing arguments in the class constructor of the given
        column type.
        Default implementation returns the default arguments that were
        specified in the function.
        """
        return args, kwargs

    @classmethod
    def _convert_bounds_type(cls, value):
        """
        Converts string value of the minimum/maximum value to the correct
        type e.g. string to date, string to int etc.
        Default implementation returns the original value as a string.
        """
        return value

    @classmethod
    def write_xml(cls, column, parent_node, document):
        col_element = document.createElement(cls.TAG_NAME)

        # Append general column information
        col_element.setAttribute('TYPE_INFO', cls.COLUMN_TYPE_INFO)
        col_element.setAttribute(ColumnSerializerCollection.DESCRIPTION,
                                 column.description)
        col_element.setAttribute(ColumnSerializerCollection.NAME, column.name)
        col_element.setAttribute(ColumnSerializerCollection.INDEX,
                                 str(column.index))
        col_element.setAttribute(ColumnSerializerCollection.MANDATORY,
                                 str(column.mandatory))
        col_element.setAttribute(ColumnSerializerCollection.SEARCHABLE,
                                 str(column.searchable))
        col_element.setAttribute(ColumnSerializerCollection.UNIQUE,
                                 str(column.unique))
        col_element.setAttribute(ColumnSerializerCollection.USER_TIP,
                                 column.user_tip)
        col_element.setAttribute(ColumnSerializerCollection.LABEL,
                                 column.label)
        col_element.setAttribute(ColumnSerializerCollection.ROW_INDEX,
                                 str(column.row_index))

        if hasattr(column, 'minimum'):
            col_element.setAttribute(ColumnSerializerCollection.MINIMUM,
                                     str(column.minimum))

        if hasattr(column, 'maximum'):
            col_element.setAttribute(ColumnSerializerCollection.MAXIMUM,
                                     str(column.maximum))

        # Append any additional information defined by subclasses.
        cls._write_xml(column, col_element, document)

        parent_node.appendChild(col_element)

    @classmethod
    def _write_xml(cls, column, column_element, document):
        """
        To be implemented by subclasses if they want to append additional
        information to the column element. Base implementation does nothing.
        """
        pass

    @staticmethod
    def handler(type_info):
        return ColumnSerializerCollection._registry.get(type_info, None)


class TextColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes text column type.
    """
    COLUMN_TYPE_INFO = 'TEXT'


TextColumnSerializer.register()


class VarCharColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes VarChar column type.
    """
    COLUMN_TYPE_INFO = 'VARCHAR'

    @classmethod
    def _convert_bounds_type(cls, value):
        return int(value)


VarCharColumnSerializer.register()


class TextColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes VarChar column type.
    """
    COLUMN_TYPE_INFO = 'TEXT'

    @classmethod
    def _convert_bounds_type(cls, value):
        return int(value)


TextColumnSerializer.register()


class IntegerColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes integer column type.
    """
    COLUMN_TYPE_INFO = 'INT'

    @classmethod
    def _convert_bounds_type(cls, value):
        return int(value)


IntegerColumnSerializer.register()


class DoubleColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes double column type.
    """
    COLUMN_TYPE_INFO = 'DOUBLE'
    NUMERIC_TAG = 'Numeric'
    PRECISION = 'precision'
    SCALE = 'scale'

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Get numeric properties
        numeric_el = element.firstChildElement(
            DoubleColumnSerializer.NUMERIC_TAG
        )
        if not numeric_el.isNull():
            precision = int(
                numeric_el.attribute(DoubleColumnSerializer.PRECISION, '18')
            )
            scale = int(
                numeric_el.attribute(DoubleColumnSerializer.SCALE, '6')
            )

            # Append additional information
            kwargs['precision'] = precision
            kwargs['scale'] = scale

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append numeric attributes
        num_element = document.createElement(
            DoubleColumnSerializer.NUMERIC_TAG
        )
        num_element.setAttribute(
            DoubleColumnSerializer.PRECISION,
            str(column.precision)
        )
        num_element.setAttribute(
            DoubleColumnSerializer.SCALE,
            str(column.scale)
        )

        column_element.appendChild(num_element)

    @classmethod
    def _convert_bounds_type(cls, value):
        return Decimal.from_float(float(value))


DoubleColumnSerializer.register()


class SerialColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes serial/auto-increment column type.
    """
    COLUMN_TYPE_INFO = 'SERIAL'


SerialColumnSerializer.register()


class DateColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes date column type.
    """
    COLUMN_TYPE_INFO = 'DATE'
    CURRENT_DATE = 'currentDate'

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Set current date settings
        curr_date_el = element.firstChildElement(
            DateColumnSerializer.CURRENT_DATE
        )
        if not curr_date_el.isNull():
            current_min = _str_to_bool(curr_date_el.attribute(
                'minimum',
                ''
            ))
            current_max = _str_to_bool(curr_date_el.attribute(
                'maximum',
                ''
            ))

            # Append additional information
            kwargs['min_use_current_date'] = current_min
            kwargs['max_use_current_date'] = current_max

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append use current date settings
        dt_element = \
            document.createElement(DateColumnSerializer.CURRENT_DATE)
        dt_element.setAttribute('minimum', str(column.min_use_current_date))
        dt_element.setAttribute('maximum', str(column.max_use_current_date))

        column_element.appendChild(dt_element)

    @classmethod
    def _convert_bounds_type(cls, value):
        return date_from_string(value)


DateColumnSerializer.register()


class DateTimeColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes date time column type.
    """
    COLUMN_TYPE_INFO = 'DATETIME'
    CURRENT_DATE_TIME = 'currentDateTime'

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Set current date time settings
        curr_date_time_el = element.firstChildElement(
            DateTimeColumnSerializer.CURRENT_DATE_TIME
        )
        if not curr_date_time_el.isNull():
            current_min = _str_to_bool(curr_date_time_el.attribute(
                'minimum',
                ''
            ))
            current_max = _str_to_bool(curr_date_time_el.attribute(
                'maximum',
                ''
            ))

            # Append additional information
            kwargs['min_use_current_datetime'] = current_min
            kwargs['max_use_current_datetime'] = current_max

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append use current datetime settings
        dt_element = \
            document.createElement(DateTimeColumnSerializer.CURRENT_DATE_TIME)
        dt_element.setAttribute('minimum', str(column.min_use_current_datetime))
        dt_element.setAttribute('maximum', str(column.max_use_current_datetime))

        column_element.appendChild(dt_element)

    @classmethod
    def _convert_bounds_type(cls, value):
        return datetime_from_string(value)


DateTimeColumnSerializer.register()


class BooleanColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes yes/no column type.
    """
    COLUMN_TYPE_INFO = 'BOOL'


BooleanColumnSerializer.register()


class GeometryColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes geometry column type.
    """
    COLUMN_TYPE_INFO = 'GEOMETRY'
    GEOM_TAG = 'Geometry'

    # Attribute names
    SRID = 'srid'
    GEOMETRY_TYPE = 'type'
    LAYER_DISPLAY = 'layerDisplay'

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Include the geometry type and SRID in the arguments.
        geom_el = element.firstChildElement(GeometryColumnSerializer.GEOM_TAG)
        if not geom_el.isNull():
            geom_type = int(geom_el.attribute(
                GeometryColumnSerializer.GEOMETRY_TYPE,
                '2'
            ))

            srid = int(geom_el.attribute(
                GeometryColumnSerializer.SRID,
                '4326'
            ))

            display_name = str(geom_el.attribute(
                GeometryColumnSerializer.LAYER_DISPLAY,
                ''
            ))

            # Append additional geometry information
            args.append(geom_type)
            kwargs['srid'] = srid
            kwargs['layer_display'] = display_name

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append custom geometry information
        geom_element = \
            document.createElement(GeometryColumnSerializer.GEOM_TAG)
        geom_element.setAttribute(GeometryColumnSerializer.SRID,
                                  str(column.srid))
        geom_element.setAttribute(GeometryColumnSerializer.GEOMETRY_TYPE,
                                  column.geom_type)
        geom_element.setAttribute(GeometryColumnSerializer.LAYER_DISPLAY,
                                  column.layer_display_name)

        column_element.appendChild(geom_element)


GeometryColumnSerializer.register()


class ForeignKeyColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes foreign key column type.
    """
    COLUMN_TYPE_INFO = 'FOREIGN_KEY'
    RELATION_TAG = 'Relation'

    @classmethod
    def entity_relation_element(cls, foreign_key_element):
        # Returns the entity relation element from a foreign key element.
        return foreign_key_element.firstChildElement(
            ForeignKeyColumnSerializer.RELATION_TAG
        )

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Include entity relation information.
        relation_el = ForeignKeyColumnSerializer.entity_relation_element(
            element
        )

        if not relation_el.isNull():
            relation_name = str(relation_el.attribute('name', ''))
            er_element = entity_relation_elements.get(relation_name, None)

            if er_element is not None:
                profile = args[1].profile
                er = EntityRelationSerializer.read_xml(er_element, profile,
                                                       assoc_elements,
                                                       entity_relation_elements)

                status, msg = er.valid()
                if status:
                    # Append entity relation information
                    kwargs['entity_relation'] = er

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append entity relation name
        fk_element = \
            document.createElement(ForeignKeyColumnSerializer.RELATION_TAG)
        fk_element.setAttribute('name', column.entity_relation.name)

        column_element.appendChild(fk_element)


ForeignKeyColumnSerializer.register()


class LookupColumnSerializer(ForeignKeyColumnSerializer):
    """
    (De)serializes lookup column type.
    """
    COLUMN_TYPE_INFO = 'LOOKUP'


LookupColumnSerializer.register()


class PercentColumnSerializer(DoubleColumnSerializer):
    """
    (De)serializes percent column type.
    """
    COLUMN_TYPE_INFO = 'PERCENT'


PercentColumnSerializer.register()


class AdminSpatialUnitColumnSerializer(ForeignKeyColumnSerializer):
    """
    (De)serializes administrative spatial unit column type.
    """
    COLUMN_TYPE_INFO = 'ADMIN_SPATIAL_UNIT'

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        return args, kwargs


AdminSpatialUnitColumnSerializer.register()


class AutoGeneratedColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes administrative spatial unit column type.
    """
    COLUMN_TYPE_INFO = 'AUTO_GENERATED'
    CODE = 'Code'
    PREFIX_SOURCE = 'prefix_source'
    LEADING_ZERO = 'leading_zero'
    SEPARATOR = 'separator'
    COLUMNS = 'columns'
    COLUMN_SEPARATORS = 'columnSeparators'
    DISABLE_AUTO_INCREMENT = 'disableAutoIncrement'
    ENABLE_EDITING = 'enableEditing'
    HIDE_PREFIX = 'hidePrefix'

    @classmethod
    def _convert_bounds_type(cls, value):
        return int(value)

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        # Include the prefix_code in the arguments.
        code_ele = element.firstChildElement(
            AutoGeneratedColumnSerializer.CODE
        )
        if not code_ele.isNull():

            prefix_source = code_ele.attribute(
                AutoGeneratedColumnSerializer.PREFIX_SOURCE,
                ''
            )
            columns = code_ele.attribute(
                AutoGeneratedColumnSerializer.COLUMNS,
                ''
            )
            column_separators = code_ele.attribute(
                AutoGeneratedColumnSerializer.COLUMN_SEPARATORS,
                ''
            )
            leading_zero = code_ele.attribute(
                AutoGeneratedColumnSerializer.LEADING_ZERO,
                ''
            )
            separator = code_ele.attribute(
                AutoGeneratedColumnSerializer.SEPARATOR,
                ''
            )
            disable_auto_increment = code_ele.attribute(
                AutoGeneratedColumnSerializer.DISABLE_AUTO_INCREMENT,
                'True'
            )
            enable_editing = code_ele.attribute(
                AutoGeneratedColumnSerializer.ENABLE_EDITING,
                'False'
            )
            hide_prefix = code_ele.attribute(
                AutoGeneratedColumnSerializer.HIDE_PREFIX,
                'False'
            )
            if not columns:
                columns = []
            else:
                columns = columns.split(',')

            if not column_separators:
                column_separators = []
            else:
                column_separators = column_separators.split(',')

            disable_auto_increment = string_to_boolean(disable_auto_increment, False)
            enable_editing = string_to_boolean(enable_editing, False)
            hide_prefix = string_to_boolean(hide_prefix, False)

            # Append prefix_source
            kwargs['prefix_source'] = prefix_source
            kwargs['columns'] = columns
            kwargs['leading_zero'] = leading_zero
            kwargs['separator'] = separator
            kwargs['disable_auto_increment'] = disable_auto_increment
            kwargs['enable_editing'] = enable_editing
            kwargs['column_separators'] = column_separators
            kwargs['hide_prefix'] = hide_prefix

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append code prefix source
        dt_element = document.createElement(
            AutoGeneratedColumnSerializer.CODE
        )
        dt_element.setAttribute('prefix_source', column.prefix_source)
        dt_element.setAttribute('columns', ','.join(column.columns))
        dt_element.setAttribute('leading_zero', column.leading_zero)
        dt_element.setAttribute('separator', column.separator)
        dt_element.setAttribute(
            'disableAutoIncrement', str(column.disable_auto_increment)
        )
        dt_element.setAttribute('enableEditing', str(column.enable_editing))

        dt_element.setAttribute(
            'columnSeparators', ','.join(column.column_separators)
        )
        dt_element.setAttribute(
            'hidePrefix', str(column.hide_prefix)
        )
        column_element.appendChild(dt_element)


AutoGeneratedColumnSerializer.register()


class MultipleSelectColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes multiple select column type information.
    """
    COLUMN_TYPE_INFO = 'MULTIPLE_SELECT'

    ASSOCIATION_TAG = 'associationEntity'

    @classmethod
    def _obj_args(cls, args, kwargs, element, associations, entity_relations):
        # Include entity relation information.
        assoc_el = element.firstChildElement(
            MultipleSelectColumnSerializer.ASSOCIATION_TAG
        )

        if not assoc_el.isNull():
            assoc_name = str(assoc_el.attribute('name', ''))
            association_element = associations.get(assoc_name, None)

            if association_element is not None:
                first_parent = str(association_element.attribute(
                    AssociationEntitySerializer.FIRST_PARENT, '')
                )

                if first_parent:
                    # Include the name of the first_parent table in kwargs
                    kwargs['first_parent'] = first_parent

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append association entity short name
        association_entity_element = \
            document.createElement(MultipleSelectColumnSerializer.ASSOCIATION_TAG)
        association_entity_element.setAttribute('name',
                                                column.association.name)

        column_element.appendChild(association_entity_element)


MultipleSelectColumnSerializer.register()


def _str_to_bool(bool_str):
    if len(bool_str) > 1:
        bool_str = bool_str[0]
    return str(bool_str).upper() == 'T'


class ExpressionColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes administrative spatial unit column type.
    """
    COLUMN_TYPE_INFO = 'EXPRESSION'

    EXPRESSION = 'expression'
    OUTPUT_DATA_TYPE = 'outputDataType'

    @classmethod
    def _convert_bounds_type(cls, value):
        return int(value)

    @classmethod
    def _obj_args(cls, args, kwargs, element, assoc_elements,
                  entity_relation_elements):
        exp_ele = element.firstChildElement(
            ExpressionColumnSerializer.EXPRESSION
        )
        if not exp_ele.isNull():
            expression = exp_ele.attribute(
                ExpressionColumnSerializer.EXPRESSION,
                ''
            )
            output_data_type = exp_ele.attribute(
                ExpressionColumnSerializer.OUTPUT_DATA_TYPE,
                ''
            )

            kwargs['expression'] = expression
            kwargs['output_data_type'] = output_data_type

        return args, kwargs

    @classmethod
    def _write_xml(cls, column, column_element, document):
        # Append code prefix source
        dt_element = document.createElement(
            ExpressionColumnSerializer.EXPRESSION
        )
        dt_element.setAttribute('expression', column.expression)
        dt_element.setAttribute('outputDataType', column.output_data_type)

        column_element.appendChild(dt_element)


ExpressionColumnSerializer.register()
