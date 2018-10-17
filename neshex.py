class neshex:

    def __init__(self, translationfile):
        """Initializes the neshex database and properties"""
        self.db = self.load_db(translationfile)

    def load_db(self, file):
        """
        Initializes the neshex translation array from a file.
        The first line of this file denotes the language of the translation,
        which is enclosed in brackets in the following format: [LANGUAGE].
        Each entry in the translation file is on its own line and is in the
        following format: LETTER=HEX. Ex: A=0A
        """

        _dbfile = open(file).read()
        _lines = _dbfile.splitlines()[1:] #excluding the first line
        _db = {}

        for _line in _lines:

            _key = _line.split("=")
            _db[_key[0]] = _key[1]

        return _db

    def translate_letter_to_char(self, _let):
        """Translates a single alphanumeric character, upper or lower case, into a hex value based on the translation array."""

        return list(self.db.keys())[list(self.db.values()).index(_let)]

    def translate_letter_to_hex(self, _let):
        """Translates a single, 1-byte hex value into an alphanumeric character based on the translation array."""

        return self.db[_let]

    def translate_string_to_char(self, _str):
        """Translates an alphanumeric string into a string of hex values based on the translation array."""

        _newstring = ""
        _str = _str.split(" ")

        i = 0
        while i < len(_str):

            if len(_str[i]) == 2:

                _newstring += self.translate_letter_to_char(_str[i].replace("\n",""))

            i += 1

        return _newstring

    def translate_string_to_hex(self, _str):
        """Translates a string of hex values into an alphanumeric string based on the translation array."""

        _newstring = ""

        i = 0
        while i < len(_str):

            _newstring += self.translate_letter_to_hex(_str[i]) + " "

            i += 1

        return _newstring

    def writeHexString(self, file, start_addr, string):
        """
        Writes a string of hex values to a given file at the given address.
        For writing in ROM files, the file should be in overwrite bytes mode (r+b).
        Any file opened using patchROM() will be opened correctly.
        """

        offset = int(start_addr, base=16)

        file.seek(offset)
        file.write(bytearray.fromhex(string))

        return True

    def get_line_length(self, e):
        """
        Gets the line length of a particular line on the title screens.
        NOTE: This function will become obsolete with version 1.0.
        """
        e = s_editing.get()
        if e == 'Intro: Body':
            return 26
        elif e == 'Intro: Signature':
            return 21
        elif e == 'Intro: Signature 2':
            return 18
        elif e == 'Intro: Header':
            return 15
        elif e == 'Title: Press Play':
            return 21
        elif e == 'Title: Copyright':
            return 18
        elif e == 'Ending: Header':
            return 8
        elif e == 'Ending: Body':
            return 21

    def get_max_lines(self, e):
        """
        Gets the number of lines in a particular section on the title screens.
        NOTE: This function will become obsolete with version 1.0.
        """
        e = s_editing.get()
        if e == 'Intro: Body':
            return 4
        elif e == 'Intro: Signature':
            return 1
        elif e == 'Intro: Signature 2':
            return 1
        elif e == 'Intro: Header':
            return 1
        elif e == 'Title: Press Play':
            return 1
        elif e == 'Title: Copyright':
            return 1
        elif e == 'Ending: Header':
            return 1
        elif e == 'Ending: Body':
            return 8

    def get_ending_line_len(self, ln):
        """
        Gets the line length of a particular line on the ending screen.
        NOTE: This function will become obsolete with version 1.0.
        """
        if ln == 1:
            return 26
        elif ln == 2:
            return 23
        elif ln == 3:
            return 6
        elif ln == 4:
            return 24
        elif ln == 5:
            return 17
        elif ln == 6:
            return 24
        elif ln == 7:
            return 6
        else:
            return 1
