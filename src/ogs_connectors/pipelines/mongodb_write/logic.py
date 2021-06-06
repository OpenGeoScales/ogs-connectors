from .exceptions import InsertEmissionError
import pymongo
import json
from tqdm import tqdm
from kedro.config import ConfigLoader
import logging

logger = logging.getLogger(__name__)

try:
    # Try to get credentials (only in run mode, not in notebooks)
    conf_paths = ["conf/base", "conf/local"]
    conf_loader = ConfigLoader(conf_paths)
    credentials = conf_loader.get("credentials*")
except ValueError:
    credentials = None


def get_geo_components(geo_components_collection):
    """

    @param geo_components_collection:
    @return:
    """
    return list(geo_components_collection.find({}))


def get_data_sources(data_sources_collection):
    """

    @param data_sources_collection:
    @return:
    """
    return list(data_sources_collection.find({}))


def cast_json(line):
    try:
        json_sample = json.loads(line)
    except:
        logging.error('Failed to parse to json:', line)
        return {}
    return json_sample


def find_geo_component(geo_component, ref_geo_components):
    """
    Given a geo_component, return its id in the referential, None if not found
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


def find_data_source(data_source, ref_data_sources):
    """
    Given a data_source, return its id in the referential, None if not found
    """
    for ref_data_source in ref_data_sources:
        if data_source['name'] == ref_data_source['name']:
            return ref_data_source['_id']

    return None


def insert_emission(emissions_collection, emission, ref_geo_components, ref_data_sources):
    """
    Given an emission and referentials, try to insert the emission
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

    emissions_collection.insert_one(emission_document)


def insert_emissions(emissions, mongodb_params):
    """
    Given a list of emissions, insert them into the collection
    """
    client = pymongo.MongoClient(credentials['relational_mongodb']['url'])
    db = client.get_database(mongodb_params.get('database_name'))
    geo_components_collection = db[mongodb_params.get('geo_components_collection_name')]
    data_sources_collection = db[mongodb_params.get('data_sources_collection_name')]
    emissions_collection = db[mongodb_params.get('emissions_collection_name')]

    print(emissions[:3])

    ref_geo_components = get_geo_components(geo_components_collection)
    ref_data_sources = get_data_sources(data_sources_collection)

    nb_inserted = 0
    nb_failed = 0

    for emission in tqdm(emissions):
        try:
            insert_emission(emissions_collection, emission, ref_geo_components, ref_data_sources)
            nb_inserted += 1
        except InsertEmissionError as e:
            logger.error('Failed to insert emission: %s' % e)
            nb_failed += 1

    logger.info('Succesfully inserted %s emissions.' % nb_inserted)
    if nb_failed:
        logger.warning('Failed to insert %s emissions. See logs for details.' % nb_failed)
