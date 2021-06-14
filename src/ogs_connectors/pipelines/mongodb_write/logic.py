from .exceptions import InsertEmissionError
from ogs_connectors.io_tools import get_mongodb_client
from tqdm import tqdm
from typing import List, Dict, Optional, Callable
import logging
from kedro.framework.session import get_current_session

logger = logging.getLogger(__name__)


def get_geo_components(geo_components_collection) -> List[Dict]:
    """
    Get all documents from the geo_components_collection
    @param geo_components_collection: pymongo collection
    @return:
    """
    return list(geo_components_collection.find({}))


def get_data_sources(data_sources_collection) -> List[Dict]:
    """
    Gel all documents from the data_sources_collection
    @param data_sources_collection: pymongo collection
    @return:
    """
    return list(data_sources_collection.find({}))


def find_geo_component(geo_component: Dict, ref_geo_components: List[Dict]) -> Optional[str]:
    """
    Given a geo_component, return its id in the referential, None if not found
    @param geo_component: dict, geo_component to find
    @param ref_geo_components: list of dict, list of the geo_components to find among
    @rtype: object
    """
    # Get geo_component identifier type
    identifier_type = geo_component['identifier']['type']

    for ref_geo_component in ref_geo_components:
        # Check whether or not identifier is known for this ref_geo_component
        if identifier_type not in ref_geo_component['identifiers']:
            continue

        if ref_geo_component['identifiers'][identifier_type] == geo_component['identifier']['id']:
            return ref_geo_component['_id']

    return None


def find_data_source(data_source: Dict, ref_data_sources: List[Dict]) -> Optional[str]:
    """
    Given a data_source, return its id in the referential, None if not found
    @param data_source: dict, data_source to find
    @param ref_data_sources: list of dict, list of the data_sources to find among
    """
    for ref_data_source in ref_data_sources:
        if data_source['name'] == ref_data_source['name']:
            return ref_data_source['_id']

    return None


def create_document(emission: Dict, ref_geo_components: List[Dict], ref_data_sources: List[Dict]) -> Dict:
    """
    Given an emission and referentials, try to insert the emission
    @param emission:
    @param ref_geo_components:
    @param ref_data_sources:
    """
    # Get geo_component id
    geo_component_id = find_geo_component(
        geo_component=emission['geo_component'],
        ref_geo_components=ref_geo_components
    )

    if not geo_component_id:
        raise InsertEmissionError('geo_component not found: %s' % emission['geo_component'])

    # Get data_source id
    data_source_id = find_data_source(
        data_source=emission['data_source'],
        ref_data_sources=ref_data_sources
    )

    if not data_source_id:
        raise InsertEmissionError('data_source not found: %s' % emission['data_source'])

    # Format document
    emission_document = {
        'geo_component_id': geo_component_id,
        'data_source_id': data_source_id,
        'date': emission['date'],
        'gas': emission['emission']['gas'],
        'value': emission['emission']['value'],
        'unit': emission['emission']['unit'],
        'sector': emission['emission']['sector'],
    }

    return emission_document


def insert_emissions(emissions: List[Dict], mongodb_params: Dict) -> None:
    """
    Given a list of emissions, insert them into the emissions_collection
    @param emissions: list of dicts, emissions
    @param mongodb_params: dict, mongodb connection parameters
    """
    # Get credentials for current session
    # TODO: find alternative (currently using private function)
    session = get_current_session()
    context = session.load_context()
    credentials = context._get_config_credentials()

    # Create mongodb clients from params and credentials
    client = get_mongodb_client(
        mongodb_params=mongodb_params,
        mongodb_credentials=credentials['relational_mongodb']

    )

    # Get database and associated collections
    db = client.get_database(mongodb_params.get('database_name'))
    geo_components_collection = db[mongodb_params.get('geo_components_collection_name')]
    data_sources_collection = db[mongodb_params.get('data_sources_collection_name')]
    emissions_collection = db[mongodb_params.get('emissions_collection_name')]

    # Load once referential collections
    ref_geo_components = get_geo_components(geo_components_collection)
    ref_data_sources = get_data_sources(data_sources_collection)

    nb_inserted = 0
    nb_failed = 0
    documents_to_insert = []

    # Create documents to insert out of emissions
    for emission in tqdm(emissions):
        try:
            document = create_document(emission, ref_geo_components, ref_data_sources)
            documents_to_insert.append(document)
            nb_inserted += 1
        except InsertEmissionError as e:
            logger.error('Failed to insert emission: %s' % e)
            nb_failed += 1

    # Batch insert of created documents
    if documents_to_insert:
        emissions_collection.insert_many(documents_to_insert)

    logger.info('Succesfully inserted %s emissions.' % nb_inserted)
    if nb_failed:
        logger.warning('Failed to insert %s emissions. See logs for details.' % nb_failed)


def extract_data_source(dataset_name: str) -> str:
    """
    Given a dataset name, extracts the data source.
    Data source being the first field of the dataset name (split by /)
    @param dataset_name: str, name of the dataset
    @return: str, extracted data source
    """
    # data_source is the first partition key
    return dataset_name.split('/')[0]


def filter_data_sources(partitioned_dataset: Dict[str, Callable], data_sources: List[str]) -> Dict[str, Callable]:
    """
    Given a partitioned dataset (dict of partitions: datasets) and a list of data sources,
    Filter the dict so that only given data sources are kept
    @param partitioned_dataset:
    @param data_sources:
    @return:
    """
    for dataset_name in list(partitioned_dataset):
        dataset_data_source = extract_data_source(dataset_name)

        # Remove dataset if not in the given data_sources
        if dataset_data_source not in data_sources:
            partitioned_dataset.pop(dataset_name)
            continue

        # Remove data_source from the list to find
        data_sources.remove(dataset_data_source)

    # Warnings if some data_sources were not found
    if data_sources:
        for data_source in data_sources:
            logger.warning('Data source: %s not found in dataset. Ignoring.' % data_source)

    return partitioned_dataset


def insert_partitioned_emissions(emissions: Dict[str, Callable], mongodb_params: Dict, params: Dict) -> None:
    """
    Given emissions, a partitioned dataset, and a list of data sources, insert the different sub datasets
    into mongodb, making sure to insert only desired data sources
    @param emissions: partitioned dataset (dict): emissions dataset
    @param mongodb_params: dict: mongodb params
    @param params: dict: process params
    @return:
    """
    emissions = filter_data_sources(
        partitioned_dataset=emissions,
        data_sources=params['data_sources']
    )

    for key in emissions.keys():
        logger.info('Inserting emissions for data source: %s.' % key)
        insert_emissions(
            emissions=emissions[key](),
            mongodb_params=mongodb_params
        )
