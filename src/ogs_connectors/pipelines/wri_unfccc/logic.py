from .mapping import row_mapping
import pandas as pd
from typing import List, Dict


def wri_unfccc_connector(df: pd.DataFrame) -> List[Dict]:
    """
    wri_unfccc connector
    Given a pandas dataframe, extracts the different emissions and return them as a list
    of dicts
    @param df:
    @return:
    """
    # Set the year columns in the same one
    df = df.melt(
        id_vars=["country", "source", "sector", "gas"],
        var_name="year",
        value_name="value"
    )

    # Drop empty value rows
    df = df.loc[df['value'].notna()].reset_index()

    # Drop 'ANNEXI' country rows
    df = df.loc[df['country'] != 'ANNEXI'].reset_index()

    # Create output record for each row
    df['record'] = df.apply(
        lambda row: row_mapping(row),
        axis=1
    )

    # Output as a list of dicts
    output = df['record'].to_list()
    return output
