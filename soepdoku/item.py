from sympy import FiniteSet, Intersection, Interval, S, Union, oo


class ValueSet():

    """The ValueSet class is the parent class for the Item and Filter classes.
     It implements methods that apply the functionality of SymPy sets to items and filters.  
    """    

    def __init__(self):
        """Creates an instance of ValueSet
        """  
        self.operator = None 
        self.value = None
        self.fullset = None
        self.subset = None
        self.complement = None

    def values_to_set(self, input):
        """Takes numeric input and translates it into the corresponding SymPy set self.fullset.
        Then the function sets the SymPy sets self.subset and self.complement from self.fullset and
        self.value.

        Args:
            input (): Numeric-like input. Can be a list of int or float, the str 'bin', the str 'int', or
            a range of values in SOEP-filter notation (Ex. 1:10). 
        """        
        
        # Set full set of possible values
        self.set_fullset(input)

        # Set subset of filtered values
        self.set_subset()

        # Set complement set
        self.set_complement()
    
    def set_fullset(self, input):
        """Takes numeric input and translates it into the corresponding SymPy set self.fullset.

        Args:
            input (): Numeric-like input. Can be a list of int or float, the str 'bin', the str 'int', or
            a range of values in SOEP-filter notation (Ex. 1:10). 

        Returns:
            None: Returns None
        """
        

        # Case: List of values, ex.: [-1, 1, 2, 3 , 4]
        if input is None:
            return None

        if isinstance(input, list):
            self.fullset = FiniteSet(*input)
        
        # Case: str
        elif isinstance(input, str):
            # Case: 'bin'
            if input=='bin':
                self.fullset = FiniteSet(0, 1)

            # Case: 'int'
            elif input=='int':
                self.fullset = S.Reals # Or better Interval(0, oo)?
            
            # Case: Range of values, ex.: '1:10'
            elif ':' in input:
                a, b = input.split(':')
                self.fullset = Interval(int(a), int(b))

            # Case: Other SOEP metadata scales
            elif input in ['sec', 'txt', 'chr']:
                self.fullset = None

    def set_subset(self):
        """Creates a SymPy set from str self.value. Stores the set in self.subset.

        Returns:
            None: Returns None
        """        

        if self.value is None:
            return None

        # Range, ex.: '0:10'
        if ':' in self.value:
            a, b = self.value.split(':')
            self.subset = Interval(int(a), int(b))

        # List of numbers, ex.: '2,3,4'
        elif ',' in self.value:
            values = self.value.split(',')
            self.subset = FiniteSet(*[int(i) for i in values])

        # Integer, ex.: '2'
        elif isinstance(int(self.value), int):
            value = int(self.value)

            # Equal, ex.: =2
            if (self.operator=='=') | (self.operator=='=='):
                self.subset = Intersection(FiniteSet(value), self.fullset)
            # Larger or equal, ex.: >=2
            if self.operator==">=":
                self.subset = Intersection(Interval(value, oo), self.fullset)
            # Larger, ex.: >2
            if self.operator=='>':
                self.subset = Intersection(Interval(value, oo, left_open=True), self.fullset)
            # Smaller, ex.: <2
            if self.operator=='<':
                self.subset = Intersection(Interval(-oo, value, right_open=True), self.fullset)
            # Smaller or equal, ex.: <=2
            if self.operator=='<=':
                self.subset = Intersection(Interval(-oo, value), self.fullset)
            # Unequal, ex.: !=2
            if self.operator=='!=':
                self.subset = Intersection(Union(Interval(-oo, value, right_open=True), Interval(value, oo, left_open=True)), self.fullset)

            #operator = pp.one_of([">", "<", "=", "<=", ">=", "==", "!="])
    

    def set_complement(self):
        """Creates a SymPy set from self.fullset and self.subset. Stores the set in self.complement.
        """        

        if (self.subset is not None) & (self.fullset is not None):
            self.complement = self.subset.complement(self.fullset)


def sympy_set_to_operator_value_str(set):
    """Takes a SymPy set and returns a str representation of the set in SOEP-style filter notation.

    Args:
        set (SymPy set): A SymPy set.

    Returns:
        str: The set in SOEP-style filter notation.
    """

    if set.is_FiniteSet:
        return ("=", ','.join([str(v) for v in set]))
    elif set.is_Interval:
        a, b = set.start, set.end
       
        # Case (-oo, c) -> <c
        if (set.is_left_unbounded) & (set.right_open):
            return ("<", str(b))
        # Case (-oo, c] -> <=c
        elif (set.is_left_unbounded) & (not set.right_open):
            return ("<=", str(b))
        # Case (c, oo) -> >c
        elif (set.is_right_unbounded) & (set.left_open):
            return (">", str(a))
        # Case [c, oo] -> >=c
        elif (set.is_right_unbounded) & (not set.left_open):
            return (">=", str(a))
        # Case [a, b] or (a, b) or [a, b) or (a, b]
        if (not set.is_right_unbounded) & (not set.is_left_unbounded):
            return ("=", str(a) + ":" + str(b))
    else:
        print("Missing", type(set))
        return ("=", "999999999") # IMPLEMENTATION MISSING!


class Item(ValueSet):
    """The Item class provides methods to facilitate the work with SOEP-style items.
    Items are very similar to Filter objects. Both are objects with a set of allowed values.
    The difference is that filters also have a subset of values (the filtered values).
    Refactoring possibly required.

    Args:
        ValueSet (class): Item inherits from the ValueSet class.
    """    

    def __init__(
            self,
            question=None,
            item=None,
            scale=None,
            value=None,
            filters_in=None,
            filters_out=None
        ):
        """Creates a new Item instance.

        Args:
            question (str, optional): Question number associated with the item, ex.: 'q01'. Defaults to None.
            item (str, optional): Name of the item itself, ex.: 'elb0001'. Defaults to None.
            scale (str, optional): Scale of the item, ex.: 'bin'. Defaults to None.
            value (str, optional): Value of item, ex.: '1:5'. Defaults to None.
            filters_in (list of Filter, BoolOr, BoolAnd, optional): List of filters that limit
            access to this item. Defaults to None.
            filters_out (list of Filter, BoolOr, BoolAnd, optional): List of filters with same
            question and item as this item. Defaults to None.
        """        
        super().__init__()
        self.question = question
        self.item = item
        self.scale = scale
        self.value = value
        self.filters_in = filters_in
        if filters_out==None:
            filters_out = []
        self.filters_out = filters_out

    def __repr__(self):
        return f"{self.question};{self.item}"
    
    def __format__(self, format_spec):
        return format(str(self), format_spec)
    
    def length(self):
        pass
