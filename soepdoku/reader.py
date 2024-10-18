from pathlib import Path
from .const import VALID_CSV_TYPES
from .parser import Parser
from .handler import ConsoleHandler


def read_csv(csvfile, csvtype=None, output='DataFrame', parse_filters=False, filter_excep=True):

    """Read SOEP-style metadata stored in a CSV file. 

    Args:
        csvfile (Path or str): Path to CSV file.
        csvtype (str, optional): Type of CSV file, ex.: 'questions' or 'variables'. Valid types
        are stored in .const.VALID_CSV_TYPES.
        If not provided, the type is automatically inferred from the file name.
        output (str, optional): The CSV file is converted to given type. Defaults to 'DataFrame'.
        parse_filters (bool, optional): If True, the 'filter' column is parsed and converted to
        SOEP-style Filter() objects. Defaults to False.

    Raises:
        Exception: If 'output' is a currently unsupported type.

    Returns:
        Returns a data object of the type provided in 'output'. Default is 'DataFrame'.
    """
    

    reader = Reader(csvfile, csvtype=csvtype)

    if output=='DataFrame':
        data = reader.read_as_dataframe()
    else:
        raise Exception(f"output='{output}' invalid argument. Use 'DataFrame'.")

    # Parse filters
    if parse_filters==True:
        parser = Parser()
        parsing_errors = parser.parse(data)  # updates data

        # Filter exceptions before emitting
        if filter_excep==True:
            parsing_errors.filter_exceptions()

        # Show parsing exceptions
        handler = ConsoleHandler()
        parsing_errors.emit(handlers=[handler])

    return data


class Reader:

    def __init__(self, csvfile, csvtype=None):  

        """Initializes a Reader object. During initialization, the type of csvfile is validated
        or inferred.

        Args:
            csvfile (Path or str): csvfile to be read
            csvtype (str, optional): Type of CSV file, ex.: 'questions' or 'variables'. 
            If not provided, the type is automatically inferred from the file name. Defaults to None.

        Raises:
            ValueError: If provided csvtype is not a valid type.

        Returns:
            Reader: A Reader object
        """    
        self.csvfile = csvfile

        if csvtype == None:
            self.csvtype = self.infer_type()
        elif csvtype not in VALID_CSV_TYPES:
            raise ValueError(f'csvtype has to be one of {VALID_CSV_TYPES}.')
        else:
            self.csvtype = csvtype
        
      
    def infer_type(self):

        """Infers type of a CSV file from file name. In SOEP-style metadata, file names
        indicate the type of content in a CSV file. Ex. 'variables.csv' contains variable
        definitions and labels.

        Raises:
            ValueError: If the file name is non-standard.

        Returns:
            str: The type of the CSV file.
        """

        filename = Path(self.csvfile).stem
        for csvtype in VALID_CSV_TYPES:
            # Exact match
            if csvtype==filename:
                return csvtype

        raise ValueError(
            f"type of csvfile unknown. Please use csvtype argument to indicate whether type is one of {VALID_CSV_TYPES}."
        )
    
    def read_as_dataframe(self):

        """Reads csvfile and returns them as pandas DataFrame(). Arguments of pandas.read_csv() are
        set in accordance with SOEP metadata guidelines.

        Returns:
            DataFrame: A pandas DataFrame
        """        
    
        import pandas as pd
        df = pd.read_csv(
            self.csvfile,
            encoding="utf-8",
            header=0,
            dtype=str,
            keep_default_na=False
        )
        df.path = self.csvfile
        df.csvtype = self.csvtype

        return df