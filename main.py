
import sys, itertools, math
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

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
    global dbe
    return list(db.keys())[list(db.values()).index(_let)]

def translate_letter_to_hex(_let):
    global db
    global dbe
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
    _str = _str#.upper()

    i = 0
    while i < len(_str):
        _newstring += translate_letter_to_hex(_str[i]) + " "
        i += 1

    return _newstring

def get_line_length():
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

def get_max_lines():
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
        return 6

def get_ending_line_len(ln):
    print(ln)
    if ln == 1:
        return 19
    elif ln == 2:
        return 21
    elif ln == 3:
        return 18
    elif ln == 4:
        return 11
    elif ln == 5:
        return 18
    elif ln == 6:
        return 6
    else:
        return 1

def parse_char():

    _toparse = input_char.get("1.0",END)
    _parsed = ""

    _line_len = get_line_length()
    _max_lines = get_max_lines()

    ln = 1
    for line in _toparse.splitlines():
        if len(line) > 0:

            if s_editing.get() == 'Ending: Body':
                _parsed += line[:get_ending_line_len(ln)]

            else:
                _parsed += line[:_line_len]

            ln += 1

        if ln > _max_lines:
            break
        else:
            _parsed += "\n"

    while len(_parsed.splitlines()) < _max_lines:
        _parsed += "\n"

    while len(_parsed.splitlines()) > _max_lines:
        _parsed = _parsed[:-1]

    input_char.delete("1.0",END)
    input_char.insert("1.0",_parsed)

def btn_tohex_clicked():
    parse_char()
    _toconv = input_char.get("1.0",END)
    _convertedhex = ""

    _line_len = get_line_length()
    _max_lines = get_max_lines()

    ln = 1
    _justification = s_centered.get()
    for line in _toconv.splitlines():
        if s_editing.get() == 'Ending: Body':
            _line_len = get_ending_line_len(ln)
        _hexline = translate_string_to_hex(line[:_line_len])
        if len(line) < _line_len:
            if _justification != "centered": # left or right justification
                for _ in itertools.repeat(None,_line_len-len(line)):
                    if _justification == "left":
                        _hexline += "FF "
                    elif _justification == "right":
                        _hexline = "FF " + _hexline
            else: # centered text
                for _ in range(math.floor(_line_len/2)-math.floor(len(line)/2)):
                    _hexline = "FF " + _hexline
                for _ in range(math.ceil(_line_len/2)-math.ceil(len(line)/2)):
                    _hexline += "FF "
        ln += 1
        if ln > _max_lines+1:
            break

        if s_editing.get() == 'Intro: Body ': #Remove last space to activate
            if ln == 2:
                _hexline += "FF FF "

        _convertedhex += _hexline + "\n"

    input_hex.delete("1.0",END)
    input_hex.insert("1.0",_convertedhex)

def btn_tochar_clicked():
    _toconv = input_hex.get("1.0",END)
    input_char.delete("1.0",END)
    input_char.insert("1.0",translate_string_to_hex(_toconv))

def getROM():
    global ROM
    romfile = filedialog.askopenfilename(initialdir = dir_path,title = "Select ROM")
    e_filepath.config(state='normal')
    e_filepath.delete("1.0",END)
    e_filepath.insert("1.0",romfile)
    e_filepath.config(state='disabled')
    ROM = romfile

def writeHexString(file, start_addr, string):
    offset = int(start_addr, base=16)
    file.seek(offset)
    file.write(bytearray.fromhex(string))
    return True

def patchROM():
    global ROM
    if ROM != False:
        f = open(ROM, "r+b")
        t = input_hex.get("1.0",END).replace(" ","").splitlines()
        e = s_editing.get()

        if e == 'Intro: Body':
            writeHexString(f, "0x00068D", t[0])
            writeHexString(f, "0x0006AC", t[1])
            writeHexString(f, "0x0006C9", t[2])
            writeHexString(f, "0x0006E6", t[3])
        elif e == 'Intro: Signature':
            writeHexString(f, "0x000703", t[0])
        elif e == 'Intro: Signature 2':
            writeHexString(f, "0x00071B", t[0])
        elif e == 'Intro: Header':
            writeHexString(f, "0x00067B", t[0])
        elif e == 'Title: Press Play':
            writeHexString(f, "0x000513", t[0])
        elif e == 'Title: Copyright':
            writeHexString(f, "0x00052B", t[0])
        elif e == 'Ending: Header':
            writeHexString(f, "0x0021D5", t[0])
        elif e == 'Ending: Body':
            writeHexString(f, "0x0021E0", t[0])
            #writeHexString(f, "0x0021FE", t[1])
            #writeHexString(f, "0x002122", t[2])
            #writeHexString(f, "0x00213D", t[3])
            #writeHexString(f, "0x002153", t[4])
            #writeHexString(f, "0x00216E", t[5])

        f.close()

ROM = False

root = Tk()
root.title("Metroid: The HEX Gen")
root.resizable(False,False)
root.configure(padx=12, pady=12)

f_char = Frame(root)

s_editing = StringVar(root)
texts = {'Intro: Header', 'Intro: Body', 'Intro: Signature', 'Intro: Signature 2', 'Title: Press Play', 'Title: Copyright', 'Ending: Header', 'Ending: Body'}
s_editing.set('Intro: Body')

l_char = OptionMenu(f_char, s_editing, *sorted(texts))
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

f_justify = Frame(root)

s_centered = StringVar()
s_centered.set("left")

b = Radiobutton(f_justify, text="Left", variable=s_centered, value="left")
b.grid(row=2, column=1)
b = Radiobutton(f_justify, text="Centered", variable=s_centered, value="centered")
b.grid(row=2, column=2)
b = Radiobutton(f_justify, text="Right", variable=s_centered, value="right")
b.grid(row=2, column=3)

f_justify.grid(row=2,column=1)

f_file = Frame(root)

e_filepath = Text(f_file, pady=5, width=22, wrap=NONE, height=1)
e_filepath.config(state='disabled')
e_filepath.grid(row=0,column=1)

b_getfile = Button(f_file, text="...", command=getROM)
b_getfile.grid(row=0,column=0)

f_file.grid(row=3,column=1)

b_patch = Button(root, text="Patch", command=patchROM)
b_patch.grid(row=3,column=3)

if __name__ == "__main__":
    db = load_db()
    root.mainloop()
