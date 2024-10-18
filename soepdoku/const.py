from collections import OrderedDict

# A SOEP metadata database has the following tables/CSV files.
VALID_CSV_TYPES = {
    "questions",
    "answers",
    "variables",
    "variable_categories",
    "generations",
    "logical_variables",
    "codebook",
}

# Tables/CSV files have the following default columns.
CSV_TYPE_TO_COLS = {
    "questions": [
        "study",
        "questionnaire",
        "question",
        "item",
        "template.id",
        "text_de",
        "instruction_de",
        "text",
        "instruction",
        "scale",
        "answer_list",
        "range",
        "concept",
        "filter",
        "goto",
        "description_de",
        "description",
        "internalnotes",
        "scripternotes",
        "number",
        "old.template.id",
        "dataset",
        "var_fix",
    ],
    "answers": [
        "study",
        "questionnaire",
        "answer_list",
        "value",
        "label_de",
        "label",
    ],
    "variables": [
        "study",
        "dataset",
        "version",
        "variable",
        "template_id",
        "label",
        "label_de",
        "concept",
        "type",
        "description",
        "description_de",
        "minedition",
    ],
    "variable_categories": [
        "study",
        "dataset",
        "version",
        "variable",
        "value",
        "label",
        "label_de",
    ],
    "logical_variables": [
        "study",
        "dataset",
        "variable", 
        "concept", 
        "questionnaire", 
        "question", 
        "item"
    ],
    "generations": [
        "input_study", 
        "input_version",
        "input_dataset", 
        "input_variable",
        "output_variable",
        "output_dataset",
        "output_version",
        "output_study"
    ],
    "codebook": [
        "study",
        "dataset",
        "version",
        "section",
        "section_de",
        "variable",
        "variabletext",
        "group",
        "grouplabel",
        "sectext",
        "sectext_de",
        "waves",
        "years",
        "references",
        "contact",
        "only_labeled_vals",
    ]
}


# Tables have the following key/identifier columns.
QUESTIONS_KEYS = ['study', 'questionnaire', 'question', 'item']
LOGICALS_KEYS_IN = ['study', 'questionnaire', 'question', 'item']
LOGICALS_KEYS_OUT = ['dataset', 'variable']
GENERATIONS_KEYS_IN = ['input_dataset', 'input_variable']
GENERATIONS_KEYS_OUT = ['output_dataset', 'output_variable']
# Warning: .merge.merge_quest_log_gen() merges LOGICALS_KEYS_OUT[0] to GENERATIONS_KEYS_IN[0]
# and so forth. Do not change the order of keys or modify merge_quest_log_gen().

# These entries in the 'scales' column of table identify question items that have
# survey data attached them.
DATA_SCALES = ["bin", "int", "cat", "chr"]

# SOEP missing values with labels
SOEP_MISSINGS = OrderedDict({
    "-8": {
        'value': '-8',
        'label': 'Question not part of the survey program this year',
        'label_de': 'Frage in diesem Jahr nicht Teil des Frageprogramms'
        },
    "-7": {
        'value': '-7',
        'label': 'Only available in less restricted edition',
        'label_de': 'Nur in weniger eingeschraenkter Edition verfuegbar'
        },
    "-6": {
        'value': '-6',
        'label': 'Version of questionnaire with modified filtering',
        'label_de': 'Fragebogenversion mit geaenderter Filterfuehrung'
        },
    "-5": {
        'value': '-5',
        'label': 'Not included in this version of the questionnaire',
        'label_de': 'In Fragebogenversion nicht enthalten'
    },
    "-4": {
        'value': '-4',
        'label': 'Inadmissible multiple response',
        'label_de': 'Unzulaessige Mehrfachantwort'
    },
    "-3": {
        'value': '-3',
        'label': 'Answer improbable',
        'label_de': 'Nicht valide'
    },
    "-2": {
        'value': '-2',
        'label': 'Does not apply',
        'label_de': 'Trifft nicht zu'
    },
    "-1": {
        'value': '-1',
        'label': 'No answer',
        'label_de': 'Keine Angabe'
}})

# A translation of Pandas data types to SOEP data types.
TYPES_PANDAS_TO_SOEP = {
    'category': 'byte',
    'int8': 'byte', # Stata byte
    'int16': 'long', # Stata int
    'int32': 'long', # Stata long
    'int64': 'long', 
    'uint8': 'byte',
    'uint16': 'long',
    'uint32': 'long',
    'uint64': 'long',
    'float32': 'long', # Stata float?
    'float64': 'long', # Stata double?
    'string': 'str',
    'object': 'str',
    'boolean': 'str',
}