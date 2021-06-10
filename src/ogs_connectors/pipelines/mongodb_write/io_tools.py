import pymongo
from typing import Dict


def get_mongodb_client(mongodb_params: Dict, mongodb_credentials: Dict) -> pymongo.MongoClient:
    """
    Instantiate pymongo client given params and credentials by formatting proper url.
    @param mongodb_params: dict, params, includes urls and connection params
    @param mongodb_credentials: dict, credentials, includes user and password
    @return:
    """
    # Base url
    full_url = "mongodb://"

    # Get username, password. Only add them to url if present in the parameters
    username, password = mongodb_credentials.get('user'), mongodb_credentials.get('password')
    if (username is not None) & (password is not None):
        full_url += "{username}:{password}@".format(
            username=username,
            password=password
        )

    # Get clusters' url
    clusters = ','.join(mongodb_credentials['cluster_urls'])
    full_url += clusters

    # Get connection parameters. Only add them to url if present in the parameters
    connection_params = mongodb_params.get('connection_params')
    if connection_params:
        params = '&'.join([
            key + '=' + value
            for key, value in mongodb_params['connection_params'].items()
        ])
        full_url += '/?{params}'.format(
            params=params
        )

    return pymongo.MongoClient(full_url)
