import pandas as pd
from .mapping import row_mapping


def gcp_connector(gcp_mtco2_flat):
    """
    @param gcp_mtco2_flat:
    """
    # Renaming
    gcp_mtco2_flat = gcp_mtco2_flat.rename(columns={
        "ISO 3166-1 alpha-3": "country_alpha-3",
        "Country": "country_name"
    })

    # Sectors to be considered
    sectors_list = ["Coal", "Oil", "Gas", "Cement", "Flaring", "Other"]

    # Convert the MtCO2 in MtC (to be in adequation with the values from other dataset of GCP)
    for sector in sectors_list:
        gcp_mtco2_flat[sector] = (1.0 / 3.664) * gcp_mtco2_flat[sector]

    # Unpivot dataframe so that one row is one emission
    gcp_mtco2_flat = pd.melt(
        gcp_mtco2_flat.reset_index(),
        id_vars=['Year', 'country_name', 'country_alpha-3'],
        value_vars=sectors_list,
        var_name='sector',
    )

    # Drop rows with nan
    gcp_mtco2_flat = gcp_mtco2_flat.loc[gcp_mtco2_flat['country_alpha-3'].notna()]
    gcp_mtco2_flat = gcp_mtco2_flat.loc[gcp_mtco2_flat['value'].notna()]

    # Create output record for each row
    gcp_mtco2_flat['record'] = gcp_mtco2_flat.apply(
        lambda row: row_mapping(row),
        axis=1
    )

    # Output as a list of dicts
    output = gcp_mtco2_flat['record'].to_list()
    return output


