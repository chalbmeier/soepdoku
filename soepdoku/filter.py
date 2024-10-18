from .item import ValueSet, sympy_set_to_operator_value_str

class Filter(ValueSet):

    """
    Class to store a single SOEP-style filter.
    Example: q01;elb001=1 is stored as Filter object with attributes 'question': 'q01',
    'item': 'elb001', 'operator': '=', 'value': '2'. 
    """

    def __init__(
        self, 
        question=None, 
        item=None, 
        operator=None, 
        value=None, 
        subset=None,
        fullset=None,
        complement=None,
    ):
        """Creates a Filter object.

        Args:
            question (str, optional): Question of the filter. Defaults to None.
            item (str, optional): Item of the filter. Defaults to None.
            operator (str, optional): Operator of the filter. Defaults to None.
            value (str, optional): Value of the filter. Defaults to None.
            subset (sympy set, optional): _description_. Set representing the filter's value. Defaults to None.
            fullset (sympy set, optional): _description_. Set representing all values of item  Defaults to None.
            complement (sympy set, optional): _description_. Complement set of subset with respect to fullset. Defaults to None.
         
        """        
        self.question = str(question)
        self.item = str(item)
        if (subset is not None) & (value is None):
            operator, value = sympy_set_to_operator_value_str(subset)
        self.operator = str(operator)
        if self.operator == "==":
            self.operator = "="
        self.value = str(value)
        self.has_parent = True
        self.children = None
        self.flat_topo = []
        self.subset = subset
        self.fullset = fullset 
        self.complement = complement

    def __key(self):
        return (self.question, self.item, self.operator, self.value)

    def __hash__(self):
        return hash(self.__key())
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.question + ";" + self.item + self.operator + self.value

    __call__ = __str__

    __repr__ = __str__

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    def _flatten(self):
        """Required to convert nested filters into flat list.
        """         
        self.flat_topo = [self]
   
    def rename_items(self, mapper=None):
        """Renames a filter's item

        Args:
            mapper (dict, optional): Dictonary of old name to new name relation.
             Ex.: {'elb0001': 'elb0001_new'}. Defaults to None.
        """        
        if mapper is not None:
            if self.item in mapper:
                self.item = mapper[self.item]


    def contains(self, other):
        return _contains(self, other)

  

def _contains(filter1, filter2):
    """Tests the relation between two filters for different cases.
    1) filter1 and filter2 refer to the same question and item:
        The function returns True if values of filter1 are superset of filter2's values.
    2) filter1 and filter2 refer to a diffeent question/item:
        The function always returns True.
    3) filter2 is a combination of various filters:
        The function tests filter1 against each element (child) of filter2.

    Args:
        filter1 (Filter): A Filter instance.
        filter2 (Filter, BoolAnd, BoolOr): An instance of Filter, BoolAnd, or BoolOr.

    Returns:
        bool: True or False
    """


    # filter2 is filter
    if filter2.children==None:
        if (filter1.question==filter2.question) & (filter1.item==filter2.item):
            return filter1.subset.is_superset(filter2.subset)
        
        elif (filter1.question!=filter2.question) | (filter1.item!=filter2.item):
            return True # !!!
        return False
    # filter2 is BoolAnd or BoolOr
    else:
        if isinstance(filter2, BoolAnd):
            return all([_contains(filter1, child) for child in filter2.children])
        if isinstance(filter2, BoolOr):
            return any([_contains(filter1, child) for child in filter2.children])
            

class BoolBinOp:

    """
    Parent class for BoolAnd and BoolOr, which relate
    a group of Filter() to each other with the boolean operators "&" and "|"
    """

    repr_symbol: str = ""

    def __init__(self, t):
        """Creates a new instance of BoolBinOp. Each associated filter is stored in
        self.children.

        Args:
            t (list): The parsed tokens
        """    
        self.has_parent = True
        self.children = t[0][0::2]  # every second token is a filter
        self.flat_topo = []

    def __str__(self):
        sep = " %s " % self.repr_symbol
        if self.has_parent:
            return "(" + sep.join(map(str, self.children)) + ")"
        else:
            return sep.join(map(str, self.children))  # No parentheses around outer filter expression
    
    def from_filters(self, filter_list):
        """Sets self.children. Refactor.

        Args:
            filter_list (list): A list of Filter instances.
        """        
        self.children = filter_list
        self._flatten()
        
       
    def _flatten(self):
        """Creates flat list of all filter instances that belong to a nested combination of filters.
        """

        # Topological sort
        self.topo = []
        visited = set()

        def traverse(v):
            if v not in visited:
                visited.add(v)
                if v.children is not None:
                    for child in v.children:
                        traverse(child)
                if isinstance(v, Filter):
                    self.flat_topo.append(v)
        traverse(self)


    def rename_items(self, mapper=None):
        """Renames all filter items of the BoolBinOp instance.

        Args:
            mapper (dict, optional): Dictonary of old name to new name relation.
             Ex.: {'elb0001': 'elb0001_new'}. Defaults to None.
        """     
        if mapper is not None:    
            for filter in self.flat_topo:
                filter.rename_items(mapper=mapper)


class BoolAnd(BoolBinOp):
    """Boolean AND between two or more Filter()"""

    repr_symbol = "&"

    def contains(self, other):
        """Returns True if all self.children contain other.

        Args:
            other (Filter, BoolAnd, BoolOr): An instance of Filter, BoolAnd, or BoolOr.

        Returns:
            bool: True or False
        """        
        return all(f.contains(other) for f in self.children)


class BoolOr(BoolBinOp):   

    repr_symbol = "|"

    def contains(self, other):
        """Returns True if at least one self.children contains other.

        Args:
            other (Filter, BoolAnd, BoolOr): An instance of Filter, BoolAnd, or BoolOr.

        Returns:
            bool: True or False
        """   
        return any(f.contains(other) for f in self.children)

