from kedro.pipeline import Pipeline, node
from .logic import insert_emissions

gcp_write_node = node(
    func=insert_emissions,
    inputs=dict(
        emissions='gcp_staging',
        mongodb_params='params:relational_mongodb'
    ),
    outputs=None
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            gcp_write_node
        ]
    )
