import datetime

data_name = "gcp"
url = "https://www.globalcarbonproject.org/carbonbudget/20/data.html"
mapped_gas_name = "CO2"

# Sector mapping
mapped_sectors = {
    "Coal": "fossil_emissions_coal",
    "Oil": "fossil_emissions_oil",
    "Gas": "fossil_emissions_gas",
    "Cement": "fossil_emissions_cement",
    "Flaring": "fossil_emissions_flaring",
    "Other": "fossil_emissions_other"
}


def row_mapping(row):
    """
    Given a pandas Dataframe rows, map to the desired dict format
    :param row:
    :return:
    """
    return {
        'data_source': {
            'name': data_name,
            'link': url
        },
        'geo_component': {
            'scale': 'Country',
            'identifier': {
                'id': row['country_alpha-3'],
                'type': 'alpha3'
            }
        },
        'date': datetime.datetime(row['Year'], 1, 1).strftime('%Y-%m-%d'),
        'emission': {
            'gas': mapped_gas_name,
            'value': row['value'],
            'unit': {
                'unit_used': 'MtC'
            },
            'sector': {
                'sector_origin_name': row['sector'],
                'sector_mapped_name': mapped_sectors[row['sector']]
            }
        }
    }
