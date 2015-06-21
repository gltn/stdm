"""
Package that enables the customization of the map composer to create custom reports and documents.
"""
from .composer_wrapper import ComposerWrapper
from .composer_item_config import (
    ChartConfig,
    ComposerItemConfig,
    DataLabelConfig,
    LineItemConfig,
    ManageTemplatesConfig,
    MapConfig,
    OpenTemplateConfig,
    PhotoConfig,
    SaveTemplateConfig,
    TableConfig
)
from .configuration_collection_base import (
    ConfigurationCollectionBase,
    ItemConfigBase,
    ItemConfigValueHandler,
    LinkedTableItemConfiguration,
    LinkedTableValueHandler,
    col_values
)
from .item_formatter import (
    BaseComposerItemFormatter,
    ChartFormatter,
    LineFormatter,
    DataLabelFormatter,
    MapFormatter,
    PhotoFormatter,
    TableFormatter
)
from .composer_data_source import ComposerDataSource
from .document_generator import (
    DocumentGenerator
)
from .spatial_fields_config import SpatialFieldsConfiguration
from .photo_configuration import (
    PhotoConfiguration
)
from .table_configuration import (
    TableConfiguration
)
from .chart_configuration import (
    BarValueConfiguration,
    ChartConfiguration,
    legend_positions,
    VerticalBarConfiguration
)