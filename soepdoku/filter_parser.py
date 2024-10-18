from .filter import Filter, BoolAnd, BoolOr
import pyparsing as pp

pp.ParserElement.enable_packrat()

class FilterParser:

    """The FilterParser class bundles a set of methods that facilitate the
    parsing of SOEP-style filter strings (Ex.: q01;elb0012=1). The methods define
    the allowed syntax of filters, transform parsed strings into Filter objects, and
    handle exceptions if erroneous strings are parsed.
    """

    def __init__(self):

        """__init__ defines the allowed syntax for filter strings, ex.: q01;elb0012=1.
        A valid filter is composed of a question (q01) followed by a semicolon, 
        an item (elb0012), an operator (=), and a value (1). A list or range of values 
        is also allowed instead. Filters can be put into parenthesis and chained together by
        the the logical operators & and |.
        """

        # Syntax for valid filters
        question = pp.Word(pp.alphanums + "_", min=1) #.set_fail_action(self.collect_error)
        question = question + pp.FollowedBy(";").set_fail_action(self.collect_error)
        #question = question.ignore(pp.Word('()[]'))
        item = pp.Word(pp.alphanums + "_")
        operator = pp.one_of([">", "<", "=", "<=", ">=", "==", "!="])
        value = pp.Regex(r"([+-]*\d+[,:]*)+")[1, ...]
        valid_filter = pp.Group(
            question + pp.Suppress(";") + item + operator + value
        ).set_parse_action(convert_to_Filter)

        # Syntax for invalid filterm ex.: q01elb0012=1. This forces
        # the parser to continue parsing after encountering an error 
        # allowing the parser to collect multiple errors in a string.
        # See https://stackoverflow.com/a/55797441
        seperator = pp.one_of(["&", "|"])
        invalid_filter = pp.OneOrMore(
            pp.Word(pp.printables, exclude_chars="()[]"), stop_on=seperator
        ).set_parse_action(
             lambda s, loc, parse_result: self.add_invalid_filter_excep(s, loc, parse_result) 
             )

        # Settings for additional error collection
        #valid_filter.set_fail_action(self.collect_error)
        question.set_name("valid question").set_fail_action(self.collect_error)
        item.set_name("valid item").set_fail_action(self.collect_error)
        operator.set_name("valid operator: =,<,>,<=,>=,!=").set_fail_action(
            self.collect_error
        )
        value.set_name("valid numbers").set_fail_action(self.collect_error)

        # Set boolean operators that combine filters into filter_expression
        AND = pp.Keyword("&")
        OR = pp.Keyword("|")

        # Define operator precedence and associativity of OR and AND.
        filter_expression = pp.infix_notation(
            valid_filter | invalid_filter,
            [
                (OR, 2, pp.opAssoc.LEFT, BoolOr),
                (AND, 2, pp.opAssoc.LEFT, BoolAnd),
            ],
            lpar=pp.Suppress(pp.one_of(["(", "["])),  # allow ( or [ as left parenthesis
            rpar=pp.Suppress(
                pp.one_of([")", "]"])
            ),  # allow ) or ] as right parenthesis
        ).set_name("valid filter expression")

        self.filter_expression = filter_expression

    def parse(self, filter_string, line):
        """Parses a filter_string and returns it as Filter object. The function does not raise
        parsing exceptions, but collects and returns them as lists.
 
        Args:
            filter_string (str): SOEP-style filter string, ex.: q01;elb0001=1 & q02;elb0125=3
            line (int): line of filter_string in source file

        Returns:
            (Filter, [exceptions]): Returns a tuple consisting of a new Filter object and
            a list of exceptions encountered during parsing.
        """
    
        filter = None
        self.invalid_filter_found = False

        if (filter_string=='') | (filter_string is None):
            return filter, []

        try:
            self.exceptions = (
                []
            )  # Collects exceptions from self.filter_expression.parse_string
            filter = self.filter_expression.parse_string(filter_string, parse_all=True)

            if self.invalid_filter_found==True:
                filter = None
            else:
                filter[0].has_parent = False # Top level filter has no parent
                filter = filter[0]  # no list
                filter._flatten() # add filter.flat_topo


        except (pp.ParseException, pp.ParseFatalException) as pe:
            self.exceptions.append(pe)

        finally:
            # Add line number
            for exception in self.exceptions:
                exception.__setattr__("source_line", line)
            return filter, self.exceptions

    def collect_error(self, s, loc, expr, err):
        """Collects exceptions and appends them to the list FilterParser.exceptions.

        Args:
            s (str): Parsed string
            loc (int): Location of error in string
            expr (): Currently parsed expression
            err (str): Error message
        """
    
        # Append new exception if not in self.exceptions
        new_excep = pp.ParseException(s, loc, err, elem=None)

        if all([excep.__str__() != new_excep.__str__() for excep in self.exceptions]):
            self.exceptions.append(new_excep)


    def add_invalid_filter_excep(self, s, loc, parse_result):
        """Adds an exception if an invalid filter parse result is found.

        Args:
            s (str): Source string
            loc (int): Current Location in string
            parse_result (unknown): Something that is not a valid Filter. Should be of type ParseResults.

        Returns:
            None
        """    
        self.invalid_filter_found = True
        msg = "Expected a valid filter."
        self.exceptions.append(ParseExceptionInvalidFilter(s, loc, msg, elem=None))
   
        return None


def convert_to_Filter(parse_result):
    """Takes parsed elements and creates a new Filter object with them.

    Args:
        parse_result (list): Elements recognized by the parser

    Returns:
        Filter: A new filter object
    """    

    filter = Filter(
        question=parse_result[0][0],
        item=parse_result[0][1],
        operator=parse_result[0][2],
        value=parse_result[0][3],
    )

    return filter


class ParseExceptionInvalidFilter(pp.ParseException):
    """Simple class to distinguish invalid filter exceptions from
    other ParseException."""
    def __init__(self, pstr, loc = 0, msg = None, elem=None):
        super().__init__(pstr, loc, msg, elem)