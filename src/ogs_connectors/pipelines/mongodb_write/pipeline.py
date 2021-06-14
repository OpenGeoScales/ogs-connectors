from kedro.pipeline import Pipeline, node
from .logic import insert_partitioned_emissions

gcp_write_node = node(
    func=insert_partitioned_emissions,
    inputs=dict(
        emissions='staging',
        mongodb_params='params:relational_mongodb',
        params='params:mongodb_write'
    ),
    outputs=None
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            gcp_write_node
        ]
    )
