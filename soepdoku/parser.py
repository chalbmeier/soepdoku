from .filter_parser import FilterParser, ParseExceptionInvalidFilter

class Parser:
    """The parser class provides a set of methods to parse SOEP metadata tables.
    Parsing is currently limited to filter strings. The parser expects a 
    pandas DataFrame as input. 
    """    

    def __init__(self):
        """Initializes a new Parser instance.
        """        
        self.filter_parser = FilterParser()
        self.parsing_errors = ParsingErrors()

    def parse(self, dataframe):
        """Parses a dataframe with SOEP metadata row by row. Parsing of filter strings
          requires them to be stored in a column called 'filter'. The function adds a new
          column 'filter_parsed' to the dataframe.

        Args:
            dataframe (DataFrame): A pandas dataframe. 

        Returns:
            self.parsing_errors (list): A list of exceptions encountered during parsing.
        """
 
        if 'filter' not in dataframe.columns:
            return self.parsing_errors

        dataframe['filter_parsed'] = None

        for i in dataframe.index:
            result = self._parse_item(dataframe.loc[i], i+2)
            # +2 to account for different line numbering in spreadsheet software
            
            if result is not None:
                dataframe.at[i, 'filter_parsed'] = result

        if len(self.parsing_errors) > 0:
            print("Parsing of filters finished with errors.")

        return self.parsing_errors

    def _parse_item(self, row, source_line):
        """Parses a pandas Series. For parsing of filters, the series requires the column 'filter'.

        Args:
            row (Series): A pandas series.
            source_line (int): The row index of the Series in the source table.

        Returns:
            result (Filter, BoolAnd, BoolOr): The parsed filter.
        """
        
        try:
            result, new_errors = self.filter_parser.parse(row['filter'], source_line)
        except:
            result = None
        else:
            self.parsing_errors.update(new_errors)

        return result


class ParsingErrors:
    """This class provides methods to handle the list of exceptions
    encountered during parsing."""

    def __init__(self):
        self.parsing_errors = []

    def update(self, error):
        """Adds a list of new exceptions to self.parsing_errors

        Args:
            error (list): list of new exceptions
        """        
        self.parsing_errors += error

    def emit(self, handlers):
        """Emits the list of parsing exceptions to handlers

        Args:
            handlers (): A list of objects with an emit method that formats/prints/saves exceptions 
        """        

        for error in self.parsing_errors:
            for handler in handlers:
                handler.emit(error)


    def filter_exceptions(self):
        """Filters the list of exceptions. Exceptions are filtered groupwise, where
        every group consists of exceptions referring to the same row/line in the source table.
        """
        exceptions = []
        exceps_in_line = []
        prev_line = None

        for excep in self.parsing_errors:
            if excep.source_line != prev_line:
                exceptions += self._remove_parse_exception_invalid_filter(exceps_in_line)
                exceps_in_line = []
                prev_line = excep.source_line
            exceps_in_line.append(excep)

        # Exceptions of last line
        exceptions += self._remove_parse_exception_invalid_filter(exceps_in_line)
        self.parsing_errors = exceptions
    

    def _remove_parse_exception_invalid_filter(self, exceptions):
        """Removes all exceptions of type ParseExceptionInvalidFilter
          from a list of exceptions if there are multiple exceptions in the list.

        Args:
            exceptions (list): list of exceptions

        Returns:
            list: list of filtered exceptions
        """        
        if len(exceptions)<=1:
            return exceptions
        else:
            first_excep = [exceptions[0]]
            filtered_excep = [excep for excep in exceptions if not isinstance(excep, ParseExceptionInvalidFilter)]
        return filtered_excep if len(filtered_excep)>0 else first_excep
        

    def __len__(self):
        return len(self.parsing_errors)
