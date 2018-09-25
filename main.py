import sys, itertools
from tkinter import *

def load_db():
    dbfile = open("translation.ini").read()
    lines = dbfile.splitlines()[1:] #excluding the first line
    _db = {}
    for line in lines:
        key = line.split("=")
        _db[key[0]] = key[1]

    return _db

def translate_letter_to_char(_let):
    global db
    return list(db.keys())[list(db.values()).index(_let)]

def translate_letter_to_hex(_let):
    global db
    return db[_let]

def translate_string_to_char(_str):

    _newstring = ""
    _str = _str.split(" ")

    i = 0
    while i < len(_str):
        if len(_str[i]) == 2:
            _newstring += translate_letter_to_char(_str[i])
        i += 1

    return _newstring

def translate_string_to_hex(_str):

    _newstring = ""
    _str = _str.upper()

    i = 0
    while i < len(_str):
        _newstring += translate_letter_to_hex(_str[i]) + " "
        i += 1

    return _newstring

def parse_char():

    _toparse = input_char.get("1.0",END)
    _parsed = ""

    ln = 1
    for line in _toparse.splitlines():
        if len(line) > 0:
            _parsed += line[:26]
            ln += 1
        if ln > 4:
            break
        else:
            _parsed += "\n"

    input_char.delete("1.0",END)
    input_char.insert("1.0",_parsed)

def btn_tohex_clicked():
    parse_char()
    _toconv = input_char.get("1.0",END)
    _convertedhex = ""
    ln = 1
    for line in _toconv.splitlines():
        _hexline = translate_string_to_hex(line[:26])
        if len(line) < 26:
            for _ in itertools.repeat(None,26-len(line)):
                _hexline += "FF "
        ln += 1
        if ln == 2:
            _hexline += "FF FF "
        _convertedhex += _hexline + "\n"
    input_hex.delete("1.0",END)
    input_hex.insert("1.0",_convertedhex)

def btn_tochar_clicked():
    _toconv = input_hex.get("1.0",END)
    input_char.delete("1.0",END)
    input_char.insert("1.0",translate_string_to_hex(_toconv))

root = Tk()
root.title("Metroid: The HEX Gen")
root.resizable(False,False)
root.configure(padx=12, pady=12)

f_char = Frame(root)

l_char = Label(f_char, text="TEXT")
l_char.grid(row=1,column=1)
input_char = Text(f_char, height=4, padx=12, pady=12, width=28)
input_char.grid(row=2,column=1)

f_char.grid(row=1,column=1)

f_buttons = Frame(root)

b_tohex = Button(f_buttons, text=">", command=btn_tohex_clicked)
b_tohex.grid(row=1,column=1)
b_tochar = Button(f_buttons, text="<", command=btn_tochar_clicked)
b_tochar.grid(row=2,column=1)

f_buttons.grid(row=1,column=2)

f_hex = Frame(root)

l_hex = Label(f_hex, text="HEX")
l_hex.grid(row=1,column=1)
input_hex = Text(f_hex, height=4, padx=12, pady=12, width=84, wrap=NONE)
input_hex.grid(row=2,column=1)

f_hex.grid(row=1,column=3)

if __name__ == "__main__":
    db = load_db()
    root.mainloop()
