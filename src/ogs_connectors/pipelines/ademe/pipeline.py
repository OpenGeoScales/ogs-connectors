from kedro.pipeline import Pipeline
from .nodes import *


def create_pipeline(**kwargs):
    return Pipeline(
        [
            ademe_connector_node
        ]
    )
