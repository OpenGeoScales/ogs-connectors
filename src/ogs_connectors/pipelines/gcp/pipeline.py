from kedro.pipeline import Pipeline, node
from ogs_connectors.pipelines import schema_validation_node_constructor, partitioning_node_constructor
from .logic import gcp_connector

# Mapping node
gcp_connector_node = node(
    func=gcp_connector,
    inputs=dict(
        gcp_mtco2_flat='gcp_mtco2_flat',
    ),
    outputs='gcp_mapped'
)

# Validation node
schema_validation_node = schema_validation_node_constructor(
    schema_dataset_name='schema_staging'
)(
    input_dataset_name='gcp_mapped',
    output_dataset_name='gcp_staging'
)

# Partitioning node
partitioning_node = partitioning_node_constructor(
    keys=['gcp']
)(
    input_dataset_name='gcp_staging',
    output_dataset_name='staging'
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            gcp_connector_node,
            schema_validation_node,
            partitioning_node
        ]
    )
