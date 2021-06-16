import datetime

data_name = 'wri-unfccc'
url = 'https://www.climatewatchdata.org/'

mapped_sectors = {
    # Common AI/NAI
    "Waste": "waste",
    "Agriculture": "agriculture",
    "Energy": "total_energy",
    "Other": "other",

    # UNFCCC_NAI
    "Industrial Processes": "industrial_processes",
    "Land-Use Change and Forestry": "lucf",
    "Solvent and Other Product Use": "industrial_processes",
    "Total GHG emissions including LULUCF/LUCF": "total_including_lucf",
    "Total GHG emissions excluding LULUCF/LUCF": "total_excluding_lucf",

    # UNFCCC_AI
    "Industrial Processes and Product Use": "industrial_processes",
    "Land Use, Land-Use Change and Forestry": "lucf",
    "Total GHG emissions with LULUCF": "total_including_lucf",
    "Total GHG emissions without LULUCF": "total_excluding_lucf"
}

mapped_gas_name = {
    "Aggregate GHGs": "kyotogases",
    "CH4": "CH4",
    "CO2": "CO2",
    "N2O": "N2O",
    "Aggregate F-gases": "F-gas"
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
            'link': url,
            'properties': {
                'scenario': row['source']
            }
        },
        'geo_component': {
            'scale': 'Country',
            'identifier': {
                'id': row['country'],
                'type': 'alpha3'
            }
        },
        'date': datetime.datetime(row['year'], 1, 1).strftime('%Y-%m-%d'),
        'emission': {
            'gas': mapped_gas_name[row['gas']],
            'value': row['value'],
            'unit': {
                'unit_used': 'Mt co2eq'
            },
            'sector': {
                'sector_origin_name': row['sector'],
                'sector_mapped_name': mapped_sectors[row['sector']]
            }
        }
    }
