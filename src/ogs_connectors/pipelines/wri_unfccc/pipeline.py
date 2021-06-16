from kedro.pipeline import Pipeline, node
from ogs_connectors.pipelines import schema_validation_node_constructor, partitioning_node_constructor
from .logic import wri_unfccc_connector

# Mapping node
wri_unfccc_connector_node = node(
    func=wri_unfccc_connector,
    inputs=dict(
        df='wri_unfccc_cw_ghg',
    ),
    outputs='wri_unfccc_mapped'
)

# Validation node
schema_validation_node = schema_validation_node_constructor('schema_staging')(
    input_dataset_name='wri_unfccc_mapped',
    output_dataset_name='wri_unfccc_staging'
)

# Partitioning node
partitioning_node = partitioning_node_constructor(
    keys=['wri_unfccc']
)(
    input_dataset_name='wri_unfccc_staging',
    output_dataset_name='staging'
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            wri_unfccc_connector_node,
            schema_validation_node,
            partitioning_node
        ]
    )
