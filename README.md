# Description
soepdoku is a wrapper around pandas to facilitate the work with survey metadata from the Socio-Economic Panel (SOEP). The SOEP is long-running panel study that collects socio-economic data from about 20,000 German households every year. For more information, please visit https://paneldata.org/soep-core/.

# Installation
```
pip install soepdoku@git+https://git.soep.de/chalbmeier/soepdoku.git@0.1.3
```
# Usage
## Basic usage

```python
import soepdoku as soep

# Read
file = "./tests/SOEPmetadata/questionnaires/soep-core-2022-selfempl-simple/questions.csv"
data = soep.read_csv(file)

# Manipulate the data
print(data[['question', 'item', 'text']].head(5).to_string())

# Save
soep.write_csv(data, file)
```

```
  question        item                                                                                text
0       B1           1                                                             Organizational features
1    Text1       Text1  We start with questions about some of the organizational features of your company.
2        1  elb0301_v2         You have stated that you are self-employed. How did you found your company?
3        1          -1                                                      I cannot/do not want to answer
4       2a     elb0302                               With how many other people did you found the company?
```

## Filter parsing
soepdoku is equipped with a parser that recognizes the standard SOEP filter syntax. The parser detects errors in filter strings and stores parsed filters in filter objects facilitating the work.

```python
import soepdoku as soep

file = "./tests/SOEPmetadata/questionnaires/soep-core-2022-selfempl-simple/questions.csv"
quest = soep.read_csv(file, parse_filters=True)
```

```
Parsing of filters finished with errors.
Line 8: 1:elb0301_v2=2 Expected ';', found ':'  (at char 1), (line:1, col:2)
         ^
Line 25: 1;elb0301_v2 Expected valid operator: =,<,>,<=,>=,!=, found end of text  (at char 12), (line:1, col:13)
                     ^
```

Parsed filters are stored in a new column 'filter_parsed' as filter objects. Filter objects allow for straightforward access to the different components of a filter.

```python
file = "./tests/SOEPmetadata/questionnaires/soep-core-2022-selfempl-simple/questions.csv"
data = soep.read_csv(file, parse_filters=True)

filter = data.loc[4, 'filter_parsed']

print(filter)
print('Class:', type(filter))
print('Components:', filter.question, filter.item, filter.operator, filter.value)
```

```
1;elb0301_v2=2
Class: <class 'soepdoku.filter.Filter'>
Components: 1 elb0301_v2 = 2
```

Filters consisting of various filter objects are stored in boolean objects (BoolAnd, BoolOr). Their '.children' attribute provides access to the single filter objects, or in case of nested filters, to further boolean objects. The '.flat_topo' attribute ignores the logical hierarchy and returns a flat list of all filter objects that constitute a nested filter.   
```python 
filter = data.loc[17, 'filter_parsed']
print(filter)
print('Class:', type(filter))
print(filter.children)
```

```
1;elb0301_v2=2,4 & 4;betr_eigent=1
Class: <class 'soepdoku.filter.BoolAnd'>
[1;elb0301_v2=2,4, 4;betr_eigent=1]
```

## Automated translation
soepdoku contains a 'Translator' class for the purpose of quickly translating CSVs with the help of an online translation service. Currently, only DeepL is supported. The translation is rudimentary in the sense that each cell of a CSV is translated separately. This leads to cases where the same word is translated differently when it appears multiple times in different cells. Also, the disregard of the context can be relevant for translations of survey questions that comprise several items. Still, the provided translation is a good basis for a subsequent professional translation.

```python
import soepdoku as soep

file = "./tests/SOEPmetadata/datasets/selfempl2022-simple/v39/variables.csv"
data = soep.read_csv(file)

# Set up translation service
key = open('deepl_key_christoph.txt').read()
translator = soep.Translator(service='deepl', auth_key=key)

# Indicate source and target columns for translation
source_target = {'label_de': 'label'} 

# Optional glossary to force translation for specific words
glossary = {
    'Arbeitsprobe': 'work trial',
    'Anteil': 'share',
    'Rufbereitschaft': 'stand-by service',
    'Bereitschaftsdienst': 'on-call service',
    'VZ-Beschäft.': 'full-time employees',
    'Betriebsangebote': 'company benefits',
    'Kurzarbeit': 'Kurzarbeit',
}

# Translate
translator.translate(
    data,
    source_target=source_target,
    source_lang='DE',
    target_lang='EN-US',
    glossary=glossary,
    replace=False,
    missings=False,
)

soep.write_csv(data, file)

```

# Tests
Tests are written with pytest. Run them from a shell by typing:

```
pytest ./tests
```
