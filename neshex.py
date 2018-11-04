import uuid

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
        _str = _str.upper().split(" ")

        if len(_str) == 1:
            _str = ' '.join(a+b for a,b in zip(_str[0][::2], _str[0][1::2]))
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

    def readHexString(self, file, start_addr, length):
        """
        Reads a string of hex values from a given file starting at the given address.
        """

        offset = int(start_addr, base=16)

        file.seek(offset)
        _string = file.read(length)

        return _string

    def splitHexLines(self, _string, _flags):
        """
        Splits a string of hex values (without spaces) into lines based on _flags, each
        of which serve as a 'line break.'
        """

        _breakpoints = []
        _result = []

        i = 0
        for f in _flags:
            _flags[i] = str(f)
            i += 1

        i = 0
        while i <= len(_string):
            if _string[i:(i+2)] in _flags:
                _breakpoints.append(i)
                i += int(_string[i+4:i+6], base=16)*2 + 4
            i += 2

        i = 0
        for x in _breakpoints:
            if i == len(_breakpoints)-1:
                _result.append(_string[_breakpoints[i]:])
            else:
                _result.append(_string[_breakpoints[i]:_breakpoints[i+1]])
            i += 1

        return _result

    def convertCoordinates(self, section, offset):
        """
        Converts two signature bytes to x and y screen coordinates.
        """

        offset = int(offset, base=16)
        section = (int(section, base=16) - 32) - 4*((int(section, base=16) - 32) // 4)

        _x = 0
        _y = 0

        _y = (8*(section)) + ((offset // 32)-1)

        _x = offset % 32

        return [_x, _y]

    def encodeCoordinates(self, x, y, screen):
        """
        Converts x and y screen coordinates to two signature bytes
        """

        _section = ((y + 1) // 8) + 32 + 4*(screen - 1)

        _extralines = (y + 1) % 8

        _offset = x + _extralines*32

        return [hex(_section), hex(_offset)]

    def readTitleLines(self, file):
        """
        Reads the title, intro, and ending text data in bytes from the ROM and translates it
        into an alphanumeric string.
        """

        ## NOTE: These ought to be sorted based on their X/Y bits, not based on their location in the ROM. This will allow us an unlimited amount of lines per screen, space permitting. [√]

        _lines = []

        _title = self.readHexString(file, "0x000510", 45).hex()
        _title = self.splitHexLines(_title, list(range(20,27)))

        i = 0
        _roffset = int("0x000510", base=16)
        for _line in _title:
            _title[i] = {
                "location": _roffset,
                "section" : int(_title[i][0:2], base=16),
                "offset" : int(_title[i][2:4], base=16),
                "length" : int(_title[i][4:6], base=16),
                "x" : self.convertCoordinates(_title[i][0:2],_title[i][2:4])[0],
                "y" : self.convertCoordinates(_title[i][0:2],_title[i][2:4])[1],
                "raw" : _title[i][6:],
                "text" : self.translate_string_to_char(_title[i][6:]).rstrip(),
                "bank": 1,
                "writestart": "0x000510",
                "alignment" : "left",
                "screen": 1, # TEMPORARY
                "id": uuid.uuid4().hex[:6].upper()}
            _roffset += _title[i]["length"]
            i += 1

        _intro = self.readHexString(file, "0x000678", 181).hex()
        _intro = self.splitHexLines(_intro, list(range(20,27)))

        i = 0
        _roffset = int("0x000678", base=16)
        for _line in _intro:
            _intro[i] = {
                "location": _roffset,
                "section" : int(_intro[i][0:2], base=16),
                "offset" : int(_intro[i][2:4], base=16),
                "length" : int(_intro[i][4:6], base=16),
                "x" : self.convertCoordinates(_intro[i][0:2],_intro[i][2:4])[0],
                "y" : self.convertCoordinates(_intro[i][0:2],_intro[i][2:4])[1],
                "raw" : _intro[i][6:],
                "text" : self.translate_string_to_char(_intro[i][6:]),
                "bank": 1,
                "writestart": "0x000678",
                "alignment" : "left",
                "screen": 2, # TEMPORARY
                "id": uuid.uuid4().hex[:6].upper()}
            _roffset += _intro[i]["length"]
            i += 1

        #_ending = self.readHexString(file, "0x0021D5", 45).hex()
        #_ending = self.splitHexLines(_ending, [20, 21, 22])

        _lines.extend(_title)
        _lines.extend(_intro)
        #_lines.extend(_ending)

        return _lines

    def pad_value(self, v):
        while len(v) <= 1:
            v = "0" + v
        return v

    def get_line_length(self, e):
        """
        Gets the line length of a particular line on the title screens.
        NOTE: This function will become obsolete with version 1.0, since it will read this data from the ROM.
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
        NOTE: This function will become obsolete with version 1.0, since it will read this data from the ROM.
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
        NOTE: This function will become obsolete with version 1.0, since it will read this data from the ROM.
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
