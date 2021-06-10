from .mapping import row_mapping


def wri_unfccc_connector(df):
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
