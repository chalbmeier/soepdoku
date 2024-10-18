import pytest
from soepdoku.filter_parser import FilterParser
from soepdoku.filter import BoolAnd, BoolOr, Filter
from pyparsing.exceptions import ParseException


##########################################
# Test filter_parser
##########################################

### Test parsing of simple filters, ex.: 'Q20;elb0233=2'
parser = FilterParser()
@pytest.mark.parametrize('test_input, expected_result', [
    (['Q20;elb0234=2', 2], [Filter(question='Q20', item='elb0234', operator='=', value='2'), []]),
    (['2;pl0234<2', 2], [Filter(question='2', item='pl0234', operator='<', value='2'), []]),
    (['2;pl0234!=-2', 5], [Filter(question='2', item='pl0234', operator='!=', value='-2'), []]),
    (['2;pl0234==10', 5], [Filter(question='2', item='pl0234', operator='=', value='10'), []]),
    (['q02;elb001=1,2,10', 5], [Filter(question='q02', item='elb001', operator='=', value='1,2,10'), []]),
    (['q02;elb001<1:5', 10], [Filter(question='q02', item='elb001', operator='<', value='1:5'), []]),
    (['q02;elb001!=1:50', 10], [Filter(question='q02', item='elb001', operator='!=', value='1:50'), []]),
    (['q02;elb001<=-5', 10], [Filter(question='q02', item='elb001', operator='<=', value='-5'), []]),
    (['q02;elb001>=-5', 10], [Filter(question='q02', item='elb001', operator='>=', value='-5'), []]),
    (['q02;elb001>-5', 10], [Filter(question='q02', item='elb001', operator='>', value='-5'), []]),
    (['q02;bcp_01>-5', 10], [Filter(question='q02', item='bcp_01', operator='>', value='-5'), []]),
    (['F_3;bcp01=3', 10], [Filter(question='F_3', item='bcp01', operator='=', value='3'), []]),
    (['(7;elb0234=2)', 2], [Filter(question='7', item='elb0234', operator='=', value='2'), []]),
])
def test_filter_parser(test_input, expected_result):
    assert list(parser.parse(test_input[0], test_input[1])) == expected_result


### Test parsing of combined filters, ex.: '1;elb001=3 & 2;elb512=4'
@pytest.mark.parametrize('test_input, expected_result', [
    (
        '1;elb001=3 & 2;elb512=4',
        {
            'class': BoolAnd,
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3'),
            'child2': Filter(question='2', item='elb512', operator='=', value='4')
         }
    ),
    (
        '(1;elb001=3 & 2;elb512=4)',
        {
            'class': BoolAnd,
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3'),
            'child2': Filter(question='2', item='elb512', operator='=', value='4')
         }
    ),
    (
        '(1;elb001=3) & (2;elb512=4)',
        {
            'class': BoolAnd,
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3'),
            'child2': Filter(question='2', item='elb512', operator='=', value='4')
         }
    ),
        (
        '(1;elb001=3)&(2;elb512=4)',
        {
            'class': BoolAnd,
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3'),
            'child2': Filter(question='2', item='elb512', operator='=', value='4')
         }
    ),
    (
        '1;elb001=3,5,7 | 2;elb512<=4:12',
        {
            'class': BoolOr,
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='<=', value='4:12')
         }
    ),
]) 
def test_filter_parser_boolean_1(test_input, expected_result):
    filters, _ = parser.parse(test_input, 10)
    assert isinstance(filters, expected_result['class'])
    assert len(filters.children) == expected_result['length']
    assert filters.children[0] == expected_result['child1']
    assert filters.children[1] == expected_result['child2']


### Test parsing of combined filters, ex.: '(1;elb001=3 & 2;elb512=4) & 3;elb002=1'
@pytest.mark.parametrize('test_input, expected_result', [
    (
        '(1;elb001=3,5,7 | 2;elb512!=4) & 3;elb002=1',
        {
            'class1': BoolAnd, # outer class
            'class2': BoolOr, # inner left class
            'class3': Filter, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
        (
        '1;elb001=3,5,7 | (2;elb512!=4 & 3;elb002=1)',
        {
            'class1': BoolOr, # outer class
            'class2': Filter, # inner left class
            'class3': BoolAnd, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '(1;elb001=3,5,7) | (2;elb512!=4 & 3;elb002=1)',
        {
            'class1': BoolOr, # outer class
            'class2': Filter, # inner left class
            'class3': BoolAnd, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '1;elb001=3,5,7 & 2;elb512!=4 | 3;elb002=1',
        {
            'class1': BoolAnd, # outer class
            'class2': Filter, # inner left class
            'class3': BoolOr, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '1;elb001=3,5,7 | 2;elb512!=4 & 3;elb002=1',
        {
            'class1': BoolAnd, # outer class
            'class2': BoolOr, # inner left class
            'class3': Filter, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '1;elb001=3,5,7 | [2;elb512!=4 & 3;elb002=1]',
        {
            'class1': BoolOr, # outer class
            'class2': Filter, # inner left class
            'class3': BoolAnd, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '1;elb001=3,5,7 | 2;elb512!=4 & 3;elb002=1',
        {
            'class1': BoolAnd, # outer class
            'class2': BoolOr, # inner left class
            'class3': Filter, # inner right class
            'length': 2, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    (
        '(1;elb001=3,5,7)&(2;elb512!=4)&(3;elb002=1)',
        {
            'class1': BoolAnd, # outer class
            'class2': Filter,
            'class3': Filter,
            'length': 3, 
            'child1': Filter(question='1', item='elb001', operator='=', value='3,5,7'),
            'child2': Filter(question='2', item='elb512', operator='!=', value='4'),
            'child3': Filter(question='3', item='elb002', operator='=', value='1'),
         }
    ),
    
]) 
def test_filter_parser_boolean_2(test_input, expected_result):
    filters, _ = parser.parse(test_input, 1034)
    assert len(filters.children) == expected_result['length']

    assert isinstance(filters, expected_result['class1'])
    assert isinstance(filters.children[0], expected_result['class2'])
    assert isinstance(filters.children[1], expected_result['class3'])
   
    for filter, expected in zip(
        filters.flat_topo, [
            expected_result['child1'], 
            expected_result['child2'], 
            expected_result['child3']]):
        assert filter == expected


### Test exceptions
@pytest.mark.parametrize('test_input, expected_result', [
    ('3;elb0021', ParseException), 
    ('3:elb0021', ParseException),
    ('(3;elb0021 &', ParseException),
    ('5;elb0021=', ParseException),
    ('5;elb0021=h', ParseException),
    ('5;elb0021<elb001', ParseException),
    ('5;elb0021>3;elb001', ParseException),
    ('5;elb0021=23.', ParseException),
    ('5;elb0021=23.4', ParseException),
    ('5;elb0021={23}', ParseException),
    ('5;elb0021=(23, 24, 54)', ParseException),
    ('(1;elb001=3,5,7 | 2;elb512!=4)  3;elb002=1', ParseException),
    ('2;=2', ParseException),
    ('elb001=2', ParseException),
    ('F-2;elb001=2', ParseException),
    (';=2', ParseException),
    (';elb001=2', ParseException),
    (';elb001', ParseException),
    ('2;elb001-3', ParseException),
    ('2;elb001=3 & ()', ParseException),
])
def test_filter_parser_exceptions(test_input, expected_result):
    filters, exception = parser.parse(test_input, 4)
    assert (filters == None)
    assert isinstance(exception[0], expected_result)