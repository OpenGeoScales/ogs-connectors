from kedro.pipeline import node
import jsonschema
from jsonschema import ValidationError
from tqdm import tqdm
from typing import List

import logging

logger = logging.getLogger(__name__)


def validate_rows(rows: List[dict], schema: dict):
    """
    json validation for list of jsons
    Given rows, a list of dict and schema, a dict representing a jsonschema, validates objects one by one.
    Only valid objects are returned
    @param rows: list of dic
    @param schema:
    @return:
    """
    validated_rows = []
    error_rows = []

    for row in tqdm(rows):
        try:
            jsonschema.validate(row, schema)
            validated_rows.append(row)
        except ValidationError as e:
            logger.error('ValidationError: %s' % e)
            error_rows.append(row)

    if error_rows:
        logger.warning('Failed to validate %s rows (Out of %s)' % (len(error_rows), len(rows)))

    # return validated_rows, error_rows
    return validated_rows


def schema_validation_node_constructor(schema_dataset_name):
    """
    Given a schema dataset name (as defined in the data catalog), return a function that allows the creation of a
    schema validation node, from an input dataset to an output dataset
    @param schema_dataset_name: str, name of the dataset as defined in the data catalog
    @return: callable, function returning a kedro node
    """

    def validation_node(input_dataset_name, output_dataset_name):
        """
        Given an input dataset name and an output dataset name (as defined in the data catalog), return a node that
        executes the schema validation: function validate_rows
        @param input_dataset_name: str, name of a dataset as defined in the data catalog
        @param output_dataset_name: str, name of a dataset as defined in the data catalog
        @return: kedro node, node to be added in a pipeline
        """
        return node(
            func=validate_rows,
            inputs=dict(
                rows=input_dataset_name,
                schema=schema_dataset_name
            ),
            outputs=output_dataset_name,
            name='%s_validation' % schema_dataset_name
        )

    return validation_node
