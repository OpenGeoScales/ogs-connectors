from kedro.pipeline import node
import pandas as pd
from .mapping import row_mapping, assessments_cols_mapping, assessments_cols, scope_items_cols_mapping, scope_items_cols

pd.set_option('display.max_columns', 500)

INPUT_DATA_PATH = 'data/'
OUTPUT_DATA_PATH = '.'

gas_cols = [
    'co2',
    'ch4',
    'n2o',
    'other',
    'total',
    'co2_biogenic'
]


def entity_preprocessing(df, columns_mapping, select_columns):
    """

    """
    # Rename and select relevant columns
    df = df.rename(columns_mapping, axis=1)[select_columns]
    return df


def processing(emissions, assessments, scope_items):
    # # Processing
    #
    # Merge everything left side of emission

    emissions = emissions.merge(
        assessments,
        on='assessment_id',
        how='left'
    )

    emissions = emissions.merge(
        scope_items,
        on='scope_item_id',
        how='left'
    )

    # legal units mapping definition
    # assessment_id matches several SIREN
    # siren_legal_units = data['legal_units'].loc[data['legal_units']['legal_unit_id_type'] == 'SIREN']
    # clean_emissions = clean_emissions.merge(
    #     siren_legal_units,
    #     on='assessment_id',
    #     how='left'
    # )

    # Melt
    id_cols = [
        col for col in emissions.columns
        if col not in gas_cols
    ]
    clean_emissions = pd.melt(
        frame=emissions,
        id_vars=id_cols,
        value_vars=gas_cols,
        var_name='gas'
    )

    clean_emissions['record'] = clean_emissions.apply(
        lambda row: row_mapping(row),
        axis=1
    )

    clean_emissions = clean_emissions[:10]

    return clean_emissions


def ademe_connector(assessments, emissions, legal_units, scope_items, texts):
    """
    @param emissions: pandas Dataframe
    @param assessments: pandas Dataframe
    """
    # Assessments mapping and output cols definition
    assessments = entity_preprocessing(
        df=assessments,
        columns_mapping=assessments_cols_mapping,
        select_columns=assessments_cols
    )

    # Scope Items mapping and output cols definition
    scope_items = entity_preprocessing(
        df=scope_items,
        columns_mapping=scope_items_cols_mapping,
        select_columns=scope_items_cols
    )

    return processing(emissions, assessments, scope_items)['record']


ademe_connector_node = node(
    func=ademe_connector,
    inputs=dict(
        assessments='ademe_assessments',
        emissions='ademe_emissions',
        legal_units='ademe_legal_units',
        scope_items='ademe_scope_items',
        texts='ademe_texts'
    ),
    outputs='ademe_merged'
)
