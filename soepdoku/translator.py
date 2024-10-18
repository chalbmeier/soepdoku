class Translator:
    """Provides methods to translate metadata with third party translation APIs.
    """    

    def __init__(self, service=None, auth_key=None, **kwargs):
        """Set up for translation

        Args:
            service (str, optional): A translation service. Currently, only 'deepl' is supported. 
                Defaults to None.
            auth_key (str, optional): Authentication key for selected translation service. Defaults to None.

        Raises:
            ValueError: If an unsupported translation service is selected.
        """
        
        self.service = service
        self.auth_key = auth_key

        if service == "deepl":
            import deepl
            self.translator = deepl.Translator(self.auth_key, **kwargs)
            self.translate_text = self.translator.translate_text

        else:
            raise ValueError(
                "Please provide a valid translation service. Currently, deepl is supported."
            )

    def translate(
            self,
            df,
            source_lang='DE',
            target_lang='EN-US',
            replace=False,
            missings=False,
            source_target=None,
            glossary=None,
            **kwargs
        ):
        """Translates specified columns of a dataframe row by row.

        Args:
            df (DataFrame): DataFrame with text to be translated.
            source_lang (str, optional): Source language. Defaults to 'DE'.
            target_lang (str, optional): Target language. Defaults to 'EN-US'.
            replace (bool, optional): If True, existing text in target is replaced. Defaults to False.
            missings (bool, optional): If True, value labels of SOEP-style missing values are translated.
                Defaults to False.
            source_target (dict, optional): Dictionary of source and target columns.
                Ex.: {'label_de': 'label'}. Defaults to None.
            glossary (dict, optional): Dictionary of terms that shall be translated as specified.
                glossary = {'Arbeitsprobe': 'work trial','Anteil': 'share'}. Defaults to None.

        Raises:
            ValueError: If source_target is not provided.
            KeyError: If source_target is not in dataframe.columns.
        """        

        # Check arguments
        if source_target == None:
            raise ValueError("Provide argument 'source_target'.")

        for source, target in source_target.items():
            if source not in df.columns:
                raise KeyError()
            if target not in df.columns:
                raise KeyError()
        
        # Set up glossary
        if glossary is not None:
            if self.service=='deepl':
                glos = self.translator.create_glossary(
                    "Glossary",
                    source_lang,
                    target_lang,
                    glossary
                )
        else:
            glos = None

        for i in df.index:
            for source, target in source_target.items():

                text = df.at[i, source]
                if self.translatable(text, df.loc[i], source, target, replace, missings):
                    
                    try:
                        result = ""
                        result = self.translate_text(
                            text,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            glossary=glos,
                        )
                    except:
                        pass
                    else:
                        df.at[i, target] = result
                       
                    

    def translatable(self, text, row, source, target, replace, missings):
        """Tests if 'text' from a dataframe 'row' shall be translated based on the provided options.

        Args:
            text (str): String to be translated.
            row (Series): A pandas Series with characteristics relating to 'text'.
            source (str): Source column of 'text' in 'row'.
            target (str): Target column for translation in 'row'.
            replace (bool): If True and there is text in target column, function returns True.
            missings (bool): If True and row contains a label of SOEP-style missing value, function returns True.

        Returns:
            _type_: _description_
        """

        
        # Case: Emtpy text
        if self.is_empty(text):
            return False
        
        # Case: Target contains text and option replace==False
        target_text = row[target]
        if (not self.is_empty(target_text)) & (replace==False):
            return False

        # Case: text is value label of SOEP missing value and option missings=False
        if ('value' in row.index) & (target in ['label', 'label_de']) & (missings==False):
            try:
                value = int(row['value'])
            except:
                pass
            else: 
                if value<0:
                    return False
        return True

    def is_empty(self, string):
        return string.strip()==""