from sqlalchemy import (
    create_engine,
    MetaData
)
from sqlalchemy.engine import reflection
from sqlalchemy.orm import relationship
from sqlalchemy.ext.automap import automap_base

from stdm.data.database import (
    metadata,
    Model,
    STDMDb
)

def _bind_metadata(metadata):
    #Ensures there is a connectable set in the metadata
    if metadata.bind is None:
            metadata.bind = STDMDb.instance().engine

def _rename_supporting_doc_collection(base, local_cls, ref_cls, constraint):
    #Rename document collection property in an entity model
    referred_name = ref_cls.__name__

    if referred_name == 'EntitySupportingDocumentProxy':
        return 'documents'
    else:
        #Default
        return ref_cls.__name__.lower() + '_collection'


def entity_model(entity, entity_only=False, with_supporting_document=False):
    """
    Creates a mapped class and corresponding relationships from an entity
    object. Entities of 'EntitySupportingDocument' type are not supported
    since they are already mapped from their parent classes, a TypeError will
    be raised.
    :param entity: Entity
    :type entity: Entity
    :param entity_only: True to only reflect the table corresponding to the
    specified entity. Remote entities and corresponding relationships will
    not be reflected.
    :type entity_only: bool
    :return: An SQLAlchemy model reflected from the table in the database
    corresponding to the specified entity object.
    """
    if entity.TYPE_INFO == 'ENTITY_SUPPORTING_DOCUMENT':
        raise TypeError('<EntitySupportingDocument> type not supported. '
                        'Please use the parent entity.')

    rf_entities = [entity.name]

    if not entity_only:
        parents = [p.name for p in entity.parents()]
        children = [c.name for c in entity.children()]

        rf_entities.extend(parents)
        rf_entities.extend(children)

    _bind_metadata(metadata)

    #We will use a different metadata object just for reflecting 'rf_entities'
    rf_metadata = MetaData(metadata.bind)
    rf_metadata.reflect(only=rf_entities)

    '''
    Remove supporting document tables if entity supports them. The supporting
    document models will be setup manually.
    '''
    ent_supporting_docs_table = None
    profile_supporting_docs_table = None

    if entity.supports_documents:
        ent_supporting_doc = entity.supporting_doc.name
        profile_supporting_doc = entity.profile.supporting_document.name

        ent_supporting_docs_table = rf_metadata.tables.get(ent_supporting_doc,
                                                           None
        )
        profile_supporting_docs_table = rf_metadata.tables.get(
            profile_supporting_doc, None
        )

        #Remove the supporting doc tables from the metadata
        if not ent_supporting_docs_table is None:
            rf_metadata.remove(ent_supporting_docs_table)
        if not profile_supporting_docs_table is None:
            rf_metadata.remove(profile_supporting_docs_table)

    Base = automap_base(metadata=rf_metadata, cls=Model)

    '''
    Return the supporting document model that corresponds to the
    primary entity.
    '''
    supporting_doc_model = None

    #Setup supporting document models
    if entity.supports_documents:
        supporting_doc_model = configure_supporting_documents_inheritance(
            ent_supporting_docs_table, profile_supporting_docs_table, Base,
            entity.name
        )

    #Set up mapped classes and relationships
    Base.prepare(
        name_for_collection_relationship=_rename_supporting_doc_collection
    )

    if with_supporting_document:
        return getattr(Base.classes, entity.name, None), supporting_doc_model

    return getattr(Base.classes, entity.name, None)

def configure_supporting_documents_inheritance(entity_supporting_docs_t,
                                               profile_supporting_docs_t,
                                               base, parent_entity):
    class ProfileSupportingDocumentProxy(base):
        """
        Represents the root table for storing supporting documents in a
        given profile.
        """
        __table__ = profile_supporting_docs_t

        __mapper_args__ = {
            'polymorphic_identity': 'NA',
            'polymorphic_on': 'source_entity'
        }

    #Get the link columns
    t_doc_id_col = getattr(entity_supporting_docs_t.c, 'supporting_doc_id')
    p_doc_id_col = getattr(profile_supporting_docs_t.c, 'id')

    class EntitySupportingDocumentProxy(ProfileSupportingDocumentProxy):
        """
        Represents the entity supporting documents table.
        """
        __table__ = entity_supporting_docs_t

        __mapper_args__ = {
            'polymorphic_identity': parent_entity,
            'inherit_condition': t_doc_id_col == p_doc_id_col
        }

    return EntitySupportingDocumentProxy


def entity_foreign_keys(entity):
    _bind_metadata(metadata)
    insp = reflection.Inspector.from_engine(metadata.bind)

    return [fi['name'] for fi in insp.get_foreign_keys(entity.name)]


def profile_foreign_keys(profile):
    """
    Gets all foreign keys for tables in the given profile.
    :param profile: Profile object.
    :type profile: Profile
    :return: A list containing foreign key names of the given profiles.
    :rtype: list(str)
    """
    from stdm.data.pg_utils import pg_table_exists

    _bind_metadata(metadata)
    insp = reflection.Inspector.from_engine(metadata.bind)

    fks = []
    for t in profile.table_names():
        #Assert if the table exists
        if not pg_table_exists(t):
            continue

        t_fks = insp.get_foreign_keys(t)
        for fk in t_fks:
            if 'name' in fk:
                fk_name = fk['name']
                fks.append(fk_name)

    return fks