class ConsoleHandler:

    """Formats error objects and prints them in the console."""

    def __init__(self):
        pass

    def emit(self, error):
        """Formats an error and prints it in the console.

        Arguments:
            error : ParseException()
        """
      
        first_part = f"Line {error.source_line}: "
        print(first_part + f"{error.pstr} {error.msg}")
        print((len(first_part) + error.loc) * " " + "^")
