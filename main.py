
import sys, itertools, math, re, os
from os import listdir
from os.path import isfile, join
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

import neshex, mte

dir_path = os.path.dirname(os.path.realpath(__file__))

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
            writeHexString(f, "0x0021FE", t[1])
            writeHexString(f, "0x002218", t[2])
            writeHexString(f, "0x002222", t[3])
            writeHexString(f, "0x00223D", t[4])
            writeHexString(f, "0x002253", t[5])
            writeHexString(f, "0x00226E", t[6])

        f.close()

def patchROMScreen():
    global ROM
    if ROM != False:
        f = open(ROM, "r+b")
        t = vis_default.copy()

        i = 0
        for line in t:
            if len(line) < vis_maxchar[i]:
                dif = vis_maxchar[i] - len(line)
                if vis_alignment[i] == 'left':
                    t[i] = line + " "*dif
                elif vis_alignment[i] == 'center':
                    print(math.ceil(dif/2))
                    t[i] = " "*math.floor(dif/2) + line + " "*math.ceil(dif/2)
                elif vis_alignment[i] == 'right':
                    t[i] = " "*dif + line
                    print(repr(t[1]))
            t[i] = translate_string_to_hex(t[i])
            i += 1

        if s_editing.get() == 'Title':
            writeHexString(f, "0x000513", t[0])
            writeHexString(f, "0x00052B", t[1])
        elif s_editing.get() == 'Intro':
            writeHexString(f, "0x00067B", t[2])
            writeHexString(f, "0x00068D", t[3])
            writeHexString(f, "0x0006AC", t[4])
            writeHexString(f, "0x0006C9", t[5])
            writeHexString(f, "0x0006E6", t[6])
            writeHexString(f, "0x000703", t[7])
            writeHexString(f, "0x00071B", t[8])
        elif s_editing.get() == 'Ending':
            #writeHexString(f, "0x0021D5", t[0]) HEADER
            #writeHexString(f, "0x0021E0", t[0]) BODY
            #writeHexString(f, "0x0021FE", t[1])
            #writeHexString(f, "0x002218", t[2])
            #writeHexString(f, "0x002222", t[3])
            #writeHexString(f, "0x00223D", t[4])
            #writeHexString(f, "0x002253", t[5])
            #writeHexString(f, "0x00226E", t[6])
            pass

        f.close()

def patchROMAll():
    global ROM
    if ROM != False:
        f = open(ROM, "r+b")
        t = vis_default.copy()

        i = 0
        for line in t:
            if len(line) < vis_maxchar[i]:
                dif = vis_maxchar[i] - len(line)
                if vis_alignment[i] == 'left':
                    t[i] = line + " "*dif
                elif vis_alignment[i] == 'center':
                    print(math.ceil(dif/2))
                    t[i] = " "*math.floor(dif/2) + line + " "*math.ceil(dif/2)
                elif vis_alignment[i] == 'right':
                    t[i] = " "*dif + line
            t[i] = translate_string_to_hex(t[i])
            i += 1

        writeHexString(f, "0x000513", t[0])
        writeHexString(f, "0x00052B", t[1])
        writeHexString(f, "0x00067B", t[2])
        writeHexString(f, "0x00068D", t[3])
        writeHexString(f, "0x0006AC", t[4])
        writeHexString(f, "0x0006C9", t[5])
        writeHexString(f, "0x0006E6", t[6])
        writeHexString(f, "0x000703", t[7])
        writeHexString(f, "0x00071B", t[8])

        #writeHexString(f, "0x0021D5", t[0]) HEADER
        #writeHexString(f, "0x0021E0", t[0]) BODY
        #writeHexString(f, "0x0021FE", t[1])
        #writeHexString(f, "0x002218", t[2])
        #writeHexString(f, "0x002222", t[3])
        #writeHexString(f, "0x00223D", t[4])
        #writeHexString(f, "0x002253", t[5])
        #writeHexString(f, "0x00226E", t[6])

        f.close()

vis_curline = 1
vis_curpage = 1
vis_curindex = 0
sf = 3

vis_default = [
    " PUSH START BUTTON", "* 1986 NINTENDO",
    "EMERGENCY ORDER", "DEFEAT THE METROID OF",
    "THE PLANET ZEBETH AND", "DESTROY THE MOTHER BRAIN",
    "THE MECHANICAL LIFE VEIN", "GALAXY FEDERAL POLICE", "M510 ",
    "GREAT !!", "YOU FULFILED YOUR MISSION.",
    "IT WILL REVIVE PEACE IN ", "SPACE.",
    "BUT,IT MAY BE INVADED BY ", "THE OTHER METROID.",
    "PRAY FOR A TRUE PEACE IN ", "SPACE!"
    ]

vis_alignment = ["left", "left", "left", "left", "left", "left", "left", "left", "right", "left", "left", "left", "left", "left", "left", "left", "left"]
vis_maxchar = [21, 18, 15, 26, 26, 26, 26, 21, 18, 8, 26, 25, 6, 25, 18, 25, 6]
vis_offsetx = [56*sf, 72*sf, 64*sf, 32*sf, 32*sf, 32*sf, 32*sf, 56*sf, 72*sf, 104*sf, 24*sf, 24*sf, 16*sf, 24*sf, 16*sf, 24*sf, 16*sf]
vis_offsety = [128*sf, 144*sf, 24*sf, 56*sf, 72*sf, 88*sf, 104*sf, 128*sf, 144*sf, 16*sf, 40*sf, 56*sf, 72*sf, 88*sf, 104*sf, 120*sf, 136*sf]

def change_tab(evt):
    if str(n.index(n.select())) == "0":
        root.geometry('1036x768')
    elif str(n.index(n.select())) == "1":
        root.geometry('1036x224')

if __name__ == "__main__":
    ns = neshex.neshex("translation.ini")
    db = ns.db
    #img_letters = load_images()
    #vis_update_text()
    #root.mainloop()
    App = mte.MTEApp(dir_path)
