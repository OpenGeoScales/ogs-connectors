def row_mapping(row):
    """
    Given a pandas Dataframe rows, map to the desired dict format
    :param row:
    :return:
    """
    return {
        'data_provider': {
            'name': 'ademe',
        },
        'data_source:': {
            'name': 'ademe',
            'link': 'url'
        },
        'geo': {
            'organization': row['organization_name']
        },
        'time': {
            'scale': 'year',
            'value': row['reporting_year']
        },
        'emission': {
            'gas': row['gas'],
            'value': row['value'],
            'scope_name': row['scope_label'],
            'sub_scope_name': row['label']
        }
    }


assessments_cols_mapping = {
    'id': 'assessment_id'
}
assessments_cols = [
    'assessment_id',
    'organization_name',
    'organization_description',
    'organization_type',
    'collectivity_type',
    'reporting_year'
]
scope_items_cols_mapping = {
    'id': 'scope_item_id'
}
scope_items_cols = [
    'scope_item_id',
    'label',
    'scope_id',
    'scope_label'
]