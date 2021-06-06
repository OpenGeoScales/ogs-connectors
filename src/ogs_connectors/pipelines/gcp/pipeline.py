from kedro.pipeline import Pipeline, node
from ogs_connectors.pipelines.validation_node import schema_validation_node_constructor
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
schema_validation_node = schema_validation_node_constructor('schema_staging')(
    input_dataset_name='gcp_mapped',
    output_dataset_name='gcp_staging'
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            gcp_connector_node,
            schema_validation_node
        ]
    )
