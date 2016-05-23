from sqlalchemy import (
    create_engine,
    MetaData
)
from sqlalchemy.engine import reflection
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


def entity_model(entity, entity_only=False):
    """
    Creates a mapped class and corresponding relationships from an entity
    object.
    :param entity: Entity
    :type entity: Entity
    :param entity_only: True to only reflect the table corresponding to the
    specified entity. Remote entities and corresponding relationships will
    not be reflected.
    :type entity_only: bool
    :return: An SQLAlchemy model reflected from the table in the database
    corresponding to the specified entity object.
    """
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

    Base = automap_base(metadata=rf_metadata, cls=Model)

    #Set up mapped classes and relationships
    Base.prepare()

    return getattr(Base.classes, entity.name, None)


def entity_foreign_keys(entity):
    _bind_metadata(metadata)
    insp = reflection.Inspector.from_engine(metadata.bind)

    return [fi['name'] for fi in insp.get_foreign_keys(entity.name)]
