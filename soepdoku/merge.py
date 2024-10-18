import pandas as pd
import numpy as np
from soepdoku.const import (
    DATA_SCALES,
    QUESTIONS_KEYS,
    LOGICALS_KEYS_IN,
    LOGICALS_KEYS_OUT,
    GENERATIONS_KEYS_IN,
    GENERATIONS_KEYS_OUT
)

def merge_quest_log_gen(
        questionnaire,
        logicals,
        generations,
        filter_dataset=None,
        filter_version=None,
        show_dataset=True,
        show_version=True,
        merge_on_version=True,
    ):
    """Merges questionnaire <- logicals <- generations with the goal to assign all
    output_dataset and output_variable in logicals and generations to the items of a 
    questionnaire.

    Parameters
    ----------
    questionnaire : DataFrame
        SOEP Dokumentation questions.csv.
    logicals : DataFrame
        SOEP Dokumentation logical_variables.csv.
    generations : DataFrame
        SOEP Dokumentation generations.csv.
    filter_dataset : list
        Filter output by dataset. Ex.: filter_dataset=['selfempl', 'lee2estab'] shows only selfempl
        and lee2estab datasets in output
    filter_version : list
        Filter output by version. Ex.: filter_version=['v39', 'v40']
    show_dataset : bool
        If True, dataset names are shown in output
    show_version : bool
        If True, version is shown in output
        
    Returns
    -------
    DataFrame
        DataFrame has new column 'output' that contains lists of output datasets and variables.
        Ex.: ['selfempl/elb0001_v1', 'selfempl2022/elb0001'].
        DataFrame may have more rows than initial questionnaire if an input variable has multiple 
        output variables
    
    """
    
    if filter_dataset is None:
        filter_dataset = []
    
    if filter_version is None:
        filter_version = []
    elif 'v0' not in filter_version:
        filter_version.append('v0') # v0 is internal version of logical_variables.csv

    
    # Check user input
    for df, columns, type in [
        (questionnaire, QUESTIONS_KEYS, 'questions.csv'), 
        (logicals, LOGICALS_KEYS_IN + LOGICALS_KEYS_OUT, 'logical_variables.csv'), 
        (generations, GENERATIONS_KEYS_IN + GENERATIONS_KEYS_OUT, 'generations.csv')]:
        try:
            assert(_columns_in_df(df, columns))
        except AssertionError:
            print(f"{type} does not have the required columns '{columns}'")
            raise

    # Pass global merge keys to internal keys
    _questions_keys = QUESTIONS_KEYS.copy()
    _logicals_keys_in = LOGICALS_KEYS_IN.copy()
    _logicals_keys_out = LOGICALS_KEYS_OUT.copy()
    _generations_keys_in = GENERATIONS_KEYS_IN.copy()
    _generations_keys_out = GENERATIONS_KEYS_OUT.copy()
    _generations_keys_in_nv = GENERATIONS_KEYS_IN.copy()
    _generations_keys_out_nv = GENERATIONS_KEYS_OUT.copy()

    # Add version column to merge keys
    if merge_on_version==True:
        if 'input_version' not in _generations_keys_in:
            _generations_keys_in = ['input_version'] + _generations_keys_in
        if 'output_version' not in _generations_keys_out:
            _generations_keys_out = ['output_version'] + _generations_keys_out
    
    questionnaire['initial_index'] = questionnaire.index
    questionnaires_temp = questionnaire[_questions_keys + ['initial_index']]
    logicals_temp = logicals[_logicals_keys_in + _logicals_keys_out]
    generations_temp = generations[_generations_keys_in + _generations_keys_out]

    ### Merge questionnaire <- logical_variables
    data = pd.merge(
        questionnaires_temp, 
        logicals_temp, 
        how='left',
        left_on=_questions_keys,  # question, item
        right_on=_logicals_keys_in # question, item
    )

    ### Merge logical_variables <- generations
    data = pd.merge(
        data,
        generations_temp,
        how='left',
        left_on=_logicals_keys_out, # dataset, variable
        right_on=_generations_keys_in_nv, # input_dataset, input_variable
    )

    # Name output variables in logicals as in generations
    mapper = {
        k1: k2 + '_0'
        for k1, k2 
        in zip(_logicals_keys_out, _generations_keys_out_nv) # dataset, variable -> output_dataset_0, output_variable_0
    }   
    data.rename(columns=mapper, inplace=True)
    if merge_on_version==True:
        data['output_version_0'] = 'v0' # logicals has no output_version

    ### Merge generations iteratively as long as new output variables are found
    new_output_found = True
    count = 1 # output counter
    while new_output_found:
        
        # Add more output_variables
        data = pd.merge(
            data, 
            generations_temp, 
            how='left',
            left_on=_generations_keys_out, # output_dataset, output_variable
            right_on=_generations_keys_in, # input_dataset, input_variable
            suffixes=('_'+str(count), '') # output_dataset, output_variable -> output_dataset_i, output_variable_i
        )
        
        new_output_found = not left_data_contains_right_data(data, count, columns=_generations_keys_out)

        count +=1
    
    # Rename, ex: key1: key1_4, key2: key2_4, if count = 4
    data.rename(columns={c: c + '_' + str(count) for c in _generations_keys_out}, inplace=True)
  
    # Get column names
    columns = [[c + '_' + str(i) for c in _generations_keys_out] for i in range(count+1)]
    columns_flat = [i for lst in columns for i in lst]

    # Filter data by filter_dataset
    if bool(filter_dataset):
        data = apply_filter(
            data, 
            output_columns=columns, 
            filter_column='output_dataset', 
            filter=filter_dataset
        )
    
    # Filter data by filter_version
    if bool(filter_version):
        data = apply_filter(
            data, 
            output_columns=columns, 
            filter_column='output_version', 
            filter=filter_version
        )

    # Remove dataset names 
    if show_dataset==False:
        data = remove_column_from_output(data, column='output_dataset', end=count+1)

    if show_version==False:
        data = remove_column_from_output(data, column='output_version', end=count+1)
    
    # Collect content of merged columns in single columnn
    data['output'] = data[columns_flat].apply(
            lambda x: concat_str_cols_twice(x, columns), axis=1
        )
    drop_columns = columns_flat + _generations_keys_in
    data.drop(columns=drop_columns, inplace=True)
    
    # Concatenate rows 
    data = data.groupby(_questions_keys, as_index=False)['output'].apply(lambda x: concat(x))
   
    # Remove leading ,
    data['output'] = data['output'].str.lstrip(to_strip=',')

    # Get initial sorting
    data = data.merge(questionnaires_temp, how='left', on=QUESTIONS_KEYS)
    data = data.sort_values(by=['initial_index']).drop(columns=['initial_index'])

    return data


def concat(aseries):
    return ','.join(set([i for li in aseries for i in li.split(',')]))



def left_data_contains_right_data(data, count, columns=None):
    """Checks if merged left data contains merged right data 
    """

    if columns == None:
        return True
    
    import numpy as np

    result = np.ones(shape=(data.shape[0], count))

    new_columns = columns

     # Is any old column same as new column? -> New column contains no new information
    for i in range(1, count): # exclude 0, which is output from logical_variables
        old_columns = [c + '_' + str(i) for c in columns]
        result[:, i] = columns_equal(data[old_columns], data[new_columns])
    
    # Columns empty?
    result[:, -1] = ((data[new_columns]=="") | (data[new_columns].isna())).any(axis=1)  
    
    # Return true if new columns are equal to at least one of the old columns for all rows
    return result.any(axis=1).all()

def columns_equal(df1, df2):

    """Compares the columns of two dataframes of same shape. Compares row by row.
    Column names are ignored.
    
    Parameters
    ----------
    df1 : DataFrame
        DataFrame of shape N x K 
    df2 : DataFrame
        DataFrame of shape N x K

    Returns
    -------
    DataFrame of boolean values
        DataFrame has shape N x 1. Is True for row n if all K columns of df1[n] and df2[n] are equal

    """

    # Make column names equal
    d2tmp = df2.rename(columns={c2: c1 for c1, c2 in zip(df1.columns, df2.columns)})
    return (df1==d2tmp).all(axis=1)


def apply_filter(data, output_columns=None, filter_column='', filter=None):
    if (output_columns==None) | (filter_column=='') | (filter==None):
        return data
    for i, clist in enumerate(output_columns):
        datasetcolumn = filter_column + '_' + str(i)
        data.loc[~data[datasetcolumn].isin(filter), clist] = "" # Keep only items in filter
    return data


def remove_column_from_output(data, column='', end=0):
    if (column=='') | (end==0):
        return data
    cols = []
    for i in range(end):
        cols.append(column + '_' + str(i))
    data.loc[:, cols] = ""
    return data

def concat_str_cols_twice(series, col_lists):
  
    result = []
    for columns in col_lists:
        string = concat_str_cols(series, columns, sep='/')
        if string != "":
            result.append(string)
    return ','.join(result)


def concat_str_cols(series, columns, sep='/'):
    """Concatenates content of string columns to single string

    Parameters
    ----------
    series : pandas Series
    columns : list of str
        Column names in Series
    sep : str, optional
        Concatenate columns with seperator 'sep', by default '/'

    Returns
    -------
    str
       Concatenated content of columns
    """
   
    values = [
        str(series[col])
        for col in columns
        if ((series[col]!="") & (isinstance(series[col], str)))
    ]
    if len(values)>0:
        return sep.join(values)
    return ""


def get_similar_questions(
    questionnaire1,
    questionnaire2,
    compare_columns = ['text_de'],
    copy_columns = ['question', 'item'],
    algorithm='levenshtein'
    ):

    """For each question in questionnaire1, find the most similar question
    in questionnaire2 

    Parameters
    ----------
    questionnaire1 : DataFrame
    questionnaire2 : DataFrame
    compare_columns : list of str
        List of column names of questionnaire1 and questionnaire2 that are compared to each other.
    algorithm : str, optional
        Algorithm to calculate similarity between questions.
    Returns
    -------
    DataFrame

    """
    
    if algorithm=='levenshtein':
        import Levenshtein
    else:
        raise Exception("Supports only algorithm 'levenshtein'")

    # Select only items that contain data
    mask1 = questionnaire1.scale.isin(DATA_SCALES)
    mask2 = questionnaire2.scale.isin(DATA_SCALES)

    texts1 = _concat_columns_to_array(questionnaire1.loc[mask1, compare_columns])
    texts2 = _concat_columns_to_array(questionnaire2.loc[mask2, compare_columns])
    indices2 = questionnaire2[mask2].index

    result = np.full((sum(mask1), 2), np.nan)
   
    for i, s1 in enumerate(texts1):
        for j, s2 in zip(indices2, texts2):
            newdist =  Levenshtein.distance(s1, s2)/(max(len(s1), len(s2)))
            if np.isnan(result[i][1]):
                result[i][0] = j
                result[i][1] = newdist
            elif newdist<result[i][1]:
                result[i][0] = j
                result[i][1] = newdist
    
    # Merge result to questionnaire1
    questionnaire1.loc[mask1, ['index_2', 'distance']] = result
    questionnaire1 = pd.merge(
        questionnaire1,
        questionnaire2[copy_columns + compare_columns],
        left_on='index_2',
        right_on=questionnaire2.index,
        how = 'left',
        suffixes = ['', '_2'],
    )

    return questionnaire1


def _concat_columns_to_array(df):
    return [' '.join([val for val in col if val]) for col in df.values]


def _columns_in_df(df, columns):
    return all([col in df.columns for col in columns])