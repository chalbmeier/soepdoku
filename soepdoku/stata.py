from soepdoku.const import CSV_TYPE_TO_COLS, TYPES_PANDAS_TO_SOEP
from soepdoku import write_csv
import pandas as pd
from pandas.io.stata import StataReader

def stata_to_csv(
        data,
        output_dir,
        variables=True,
        variable_categories=True,
        replace=True,
        label_var='label_de',
        constant_columns = None,
    ):

    """Reads labels from a Stata dta-file and returns SOEP-style variables.csv and variable_categories.csv.
    Function relies on pandas.io.stata and its implementation of retrieving variable and value labels.

    Parameters
    ----------
    data : Stata dta-file
    output_dir : str or path
        Directory where variables.csv and variable_categories.csv are stored.
    variables : bool, optional
        Write variables.csv if True. Default is True.
    variable_categories.csv : bool, optional
        Write variable_categories.csv if True. Default is True.
    replace : bool, optional
        Replace existing csv files in directory. Currently not implemented. 
    label_var : str, optional
        Name of column in which variable labels and value labels are stored. Default is 'label_de'.
    constant_columns : dict, optional 
        Add additional columns with constant values to variables.csv and variable_categories.csv. Default is None.
        Ex: 
        constant_columns={
            "study": "soep-core",
            "dataset": "soep-core-2021-lee2estab",
            "version": "v38",
            "label": "",
            "concept": "",
            "type": "",
            "description": "",
            "description_de": "",
            "minedition": "internal",
            "template_id": "",
        }
    Returns
    -------
    variables.csv and variable_categories.csv
    """

    if constant_columns is None:
        constant_columns = {}

    with StataReader(data) as reader:  
        variable_labels = reader.variable_labels()# Ex: {'x1': '', 'x2': '', 'x3': 'Score', 'x4': 'Attitude'}
        value_labels = reader.value_labels() # Ex: {'x3': {1: '[1] score 1', 2: '[2] score 2', 3: '[3] score 3'}, 'x1_lbl': {1: '[1] Value1', 2: '[2] Value2'}}
        value_labels_list = reader._lbllist  # Contains label name assigned to each variable. Ex: ['x1_lbl', '', 'x3', 'x1_lbl']
        var_to_value_labels = {variable: value_labels.get(lblname, {}) for variable, lblname in zip(list(variable_labels.keys()), value_labels_list)}
        var_to_value_labels = {variable: dict(sorted(values.items())) for variable, values in var_to_value_labels.items()} # Sort by value
    
    # If no labels retrieved, don't write to csv -> to do: discuss whether writing empty csv is preferable
    if not bool(variable_labels):
        variables = False

    if not bool(value_labels):
        variable_categories = False 
        
    # variables.csv
    if variables==True:
        if not writing_permitted():
            return None
        else:
            df = gen_dataframe_from_dict(variable_labels, columns_in_dict=['variable', label_var])
            df = add_datatypes(df, data)
            df = add_constant_columns(df, columns=constant_columns, csvtype='variables')
            write_csv(df, output_dir+'/variables.csv', csvtype='variables', sort_columns=True)
      
    # variable_categories.csv
    if variable_categories==True:
        if not writing_permitted():
            return None
        
        else:
            df = gen_dataframe_from_dict(var_to_value_labels, columns_in_dict=['variable', 'value', label_var])
            df = add_constant_columns(df, columns=constant_columns, csvtype='variable_categories')
            write_csv(df, output_dir+'/variable_categories.csv', csvtype='variable_categories', sort_columns=True)

    

def writing_permitted():
    return True


def gen_dataframe_from_dict(dictionary, columns_in_dict):
    """Generates a pandas DataFrame from a dictionary. In the simplest case, the dictionary
     has the form {'key1': 'value1', 'key2': 'value2', ...}. Every key-value pair results in
    a row in the dataframe. More complex cases of nested dictionaries are handled as well.

    Args:
        dictionary (dict)
        columns_in_dict (list of str): A list of str column names that are assigned to the resulting
        dataframe.

    Returns:
        DataFrame
    """
    
    if not bool(dictionary):
        return None
    
    data, _ = unpack_dict(dictionary)
    data = pd.DataFrame.from_dict(data, orient='index', columns=columns_in_dict)

    return data


def unpack_dict(value, parent=None, index=0, result=None):
    """Recursively unpacks a nested dictionary and returns a 'flat' dictionary of form
    {0: [v1, v2, v3], 1: [v4, v5, v6], 2: [v7, v8, v9]}

    Args:
        value (str, int, float, dict): The current value to handle.
        parent (list, optional): A list of additional values that are appended to a key-value pair. Defaults to None.
        index (int, optional): Counts recursive iterations. Defaults to 0.
        result (dict, optional): The result of the previous recursive step. Defaults to None.

    Returns:
        result, index (dict, int): The updated result and the current index.
    """    

    # Initialize
    if result is None:
        result = {}

    if parent is None:
        parent = []

    # Base case
    if type(value) in [str, int, float]:
        result[index] = parent + [str(value)]
        index += 1
        return result, index
    
    # Recusive step, assumes that value is dictionary
    for k, v in value.items():
        parent += [str(k)]
        result, index = unpack_dict(v, parent=parent, index=index, result=result)
        parent.remove(str(k))
    
    return result, index
    
def add_datatypes(df, statadta):
    """Adds the 'type' column to a pandas DataFrame that contains a SOEP-style
    table of variables. The 'type' of each variable is retrieved from a Stata dta file.
  
    Args:
        df (DataFrame):
        statadta (Stata dta): A Stata dta file

    Returns:
        df (DataFrame): Updated dataframe
    """
    

    if df is None:
        return None

    df_temp = pd.read_stata(statadta, convert_categoricals=False)
    dtypes = df_temp.dtypes
    dtypes.name = 'type'
    dtypes = dtypes.replace(TYPES_PANDAS_TO_SOEP)
    df = df.merge(dtypes, left_on='variable', right_index=True)
    return df

def add_constant_columns(df, columns, csvtype='variables'):
    """Adds columns to a dataframe with constant values across rows.

    Args:
        df (DataFrame): pandas DataFrame.
        columns (dict): Dictionary of form {'colum name': 'constant value'}
        csvtype (str, optional): Type of table/dataframe, one of allowed SOEP metadata tables.
        Defaults to 'variables'.

    Returns:
        df (DataFrame): Updated dataframe
    """


    existing_cols = df.columns

    for col, val in columns.items():
        if (col in CSV_TYPE_TO_COLS[csvtype]) & (col not in existing_cols):
            df[col] = val
    return df