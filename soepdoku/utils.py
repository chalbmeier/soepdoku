from .const import SOEP_MISSINGS    

def listify(d):
    """Converts values of a dictionary into list of values
    
    Paramaters
    ----------
    d : dict

    Returns
    -------
    dict
        Dictionary where all values are lists
    
    """

    result = {}
    for key, value in d.items():
        if type(value) in [list, dict, tuple, set]:
            result[key] = value
        elif type(value) in [int, float, complex, str]:
            result[key] = [value]
    return result


def get_missings(study="", dataset="", version="", variable=""):
    """Creates a dictionary of standard SOEP missing values with labels.
     'study', 'dataset', 'version', 'variable' can be added optionally. 

    Args:
        study (str, optional): Adds study to dictionary. Defaults to "".
        dataset (str, optional): Adds dataset to dictionary. Defaults to "".
        version (str, optional): Adds version to dictionary. Defaults to "".
        variable (str, optional): Adds variable to dictionary. Defaults to "".

    Returns:
        dict: Dictionary of standard SOEP missing values.
    """


    missings = SOEP_MISSINGS
    newkeys = ['study', 'dataset', 'version', 'variable']
    newvalues =  [study, dataset, version, variable]
    for k in list(missings.keys()):
        for key, value in zip(newkeys, newvalues):
            missings[k][key] = value
    return missings
    

