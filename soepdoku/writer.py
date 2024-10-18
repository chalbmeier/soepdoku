from .const import CSV_TYPE_TO_COLS

def write_csv(
        dataframe,
        csvfile=None, 
        csvtype=None, 
        sort_columns=False, 
        drop_filter_parsed=True
    ):
    """Writes a DataFrame containing SOEP-style metadata to a CSV file. 

    Args:
        dataframe (DataFrame): A pandas DataFrame containing SOEP-style metadata.
        csvfile (Path or str, optional): CSV file to be written. Defaults to None.
        csvtype (str, optional): SOEP-type of CSV file. Ex.: 'varialbes'.
        Required for sort_columns. Defaults to None.
        sort_columns (bool, optional): If True, columns are sorted in accordance
        with SOEP metadata standards. Defaults to False.
        drop_filter_parsed (bool, optional): If True, column 'filter_parsed' is dropped
        before writing. Defaults to True.
    """    

    # Sort columns according to SOEP standards
    if sort_columns==True:
        exception_msg = (
            "Provide argument 'csvtype' so that columns can be sorted according "
            "to the type. Ex.: csvtype='variables'. Or set sort_columns=False."
         )

        # Get csvtype for proper sorting.
        if (csvtype is None):
            if hasattr(dataframe, 'csvtype'):
                csvtype = dataframe.csvtype
            else:
                raise Exception(exception_msg)

        sorted_columns = CSV_TYPE_TO_COLS[csvtype]
        add_cols = [col for col in dataframe.columns if col not in sorted_columns]
        dataframe = dataframe[sorted_columns + add_cols]

    # Drop column 'filter_parsed', which is not the SOEP standard.
    if (drop_filter_parsed==True) & ('filter_parsed' in dataframe.columns):
        dataframe.drop(columns=['filter_parsed'], inplace=True) 

    # Write dataframe, the index column is not the SOEP standard.
    dataframe.to_csv(csvfile, index=False)
