from kedro.pipeline import node
from typing import List, Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)


def partition_function_constructor(keys: List[str]) -> Callable:
    """
    Given a list of keys, return a function that partitions according to the list of keys
    @param keys: list of str, partition keys
    @return:
    """
    def partition_function(content: Any) -> Dict[str, Any]:
        """
        Given content, returns a dictionary of a single key value pair.
        Key being the complete partition, value being the content
        @param content: any, content to partition
        @return: dict
        """
        return {
            '{partitions}/data.json'.format(
                partitions='/'.join(keys)
            ): content
        }

    return partition_function


def partitioning_node_constructor(keys: List[str]) -> node:
    """
    Given a list of partition keys, return a function that allows the creation of a partitioning node, from an input
    dataset to an output dataset
    @param keys: list of str, list of keys to partition the dataset
    @return: callable, function returning a kedro node
    """
    partition_function = partition_function_constructor(keys)

    def partitioning_node(input_dataset_name, output_dataset_name) -> Callable:
        """
        Given an input dataset name and an output dataset name (as defined in the data catalog), return a node that
        applies partitioning
        @param input_dataset_name: str, name of a dataset as defined in the data catalog
        @param output_dataset_name: str, name of a dataset as defined in the data catalog
        @return: kedro node, node to be added in a pipeline
        """
        return node(
            func=partition_function,
            inputs=dict(
                content=input_dataset_name,
            ),
            outputs=output_dataset_name
        )

    return partitioning_node
