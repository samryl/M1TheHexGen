
import sys, itertools, math, re, os
from os import listdir
from os.path import isfile, join
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

dir_path = os.path.dirname(os.path.realpath(__file__))

def load_db():
    dbfile = open("translation.ini").read()
    lines = dbfile.splitlines()[1:] #excluding the first line
    _db = {}
    for line in lines:
        key = line.split("=")
        _db[key[0]] = key[1]

    return _db

def load_images():
    a = [f for f in listdir(dir_path + "/im/letters") if isfile(join(dir_path + "/im/letters", f))]
    i = {}
    for x in a:
        i[x] = PhotoImage(file=dir_path + "/im/letters/" + x)
    i["bg"] = PhotoImage(file=dir_path + "/im/1.png")
    i["bg2"] = PhotoImage(file=dir_path + "/im/2.png")
    i["bg3"] = PhotoImage(file=dir_path + "/im/3.png")
    return i

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
            print(_newstring)
            _newstring += translate_letter_to_char(_str[i].replace("\n",""))
        i += 1

    return _newstring

def translate_string_to_hex(_str):

    _newstring = ""

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
        return 8

def get_ending_line_len(ln):
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

def vis_update_text():
    im_field.delete("all")

    if vis_curpage == 1:
        im_field.create_image(0, 0, image=img_letters["bg"], anchor=NW)
        i = 0
        breakline = 1
    elif vis_curpage == 2:
        im_field.create_image(0, 0, image=img_letters["bg2"], anchor=NW)
        i = 2
        breakline = 8
    elif vis_curpage == 3:
        im_field.create_image(0, 0, image=img_letters["bg3"], anchor=NW)
        i = 9
        breakline = 16

    while i <= breakline:
        f = vis_default[i].replace("\t", "")
        reg = re.compile('[^a-zA-Z0-9\!\*\,\.\?\-\s]')
        f = reg.sub('', f)
        vis_default[i] = f
        t = 0

        if vis_alignment[i] == "left":
            _extra_offset = 0
        elif vis_alignment[i] == "center":
            _extra_offset = math.floor((vis_maxchar[i] - len(f)) / 2)*24
        elif vis_alignment[i] == "right":
            _extra_offset = (vis_maxchar[i] - len(f))*24

        for l in f:
            if l == "?":
                ph = img_letters["question.png"]
            elif l == " ":
                ph = img_letters["space.png"]
            elif l == "*":
                ph = img_letters["copyright.png"]
            elif l == ".":
                ph = img_letters["period.png"]
            elif l == ",":
                ph = img_letters["comma.png"]
            elif l.islower():
                ph = img_letters[l + "l.png"]
            else:
                ph = img_letters[l + ".png"]

            im_field.create_image(vis_offsetx[i] + _extra_offset + t*24, vis_offsety[i], image=ph, anchor=NW)
            t += 1
        i += 1

    im_field.create_rectangle(vis_offsetx[vis_curline]-3,vis_offsety[vis_curline]-3,vis_offsetx[vis_curline]+24*vis_maxchar[vis_curline]+3,vis_offsety[vis_curline]+24,outline="red")
    im_field.update()

vis_curline = 1
vis_curpage = 1
sf = 3

vis_default = [
    " PUSH START BUTTON", "* 1986 NINTENDO",
    "EMERGENCY ORDER", "DEFEAT THE METROID OF",
    "THE PLANET ZEBETH AND", "DESTROY THE MOTHER BRAIN",
    "THE MECHANICAL LIFE VEIN", "GALAXY FEDERAL POLICE", "M510 ",
    "GREAT !!", "YOU FULFILED YOUR MISSION.",
    "IT WILL REVIVE PEACE IN ", "SPACE.",
    "BUT,IT MAY BE INVADED BY ", "THE OTHER METROID.",
    "PRAY FOR A TRUE PEACE IN ", "SPACE!"]

vis_alignment = ["left", "left", "left", "left", "left", "left", "left", "left", "right", "left", "left", "left", "left", "left", "left", "left", "left"]
vis_maxchar = [21, 18, 15, 26, 26, 26, 26, 21, 18, 8, 26, 25, 6, 25, 18, 25, 6]
vis_offsetx = [56*sf, 72*sf, 64*sf, 32*sf, 32*sf, 32*sf, 32*sf, 56*sf, 72*sf, 104*sf, 24*sf, 24*sf, 16*sf, 24*sf, 16*sf, 24*sf, 16*sf]
vis_offsety = [128*sf, 144*sf, 24*sf, 56*sf, 72*sf, 88*sf, 104*sf, 128*sf, 144*sf, 16*sf, 40*sf, 56*sf, 72*sf, 88*sf, 104*sf, 120*sf, 136*sf]

def vis_type(evt):
    if evt.char != "":
        vis_default[vis_curline] += evt.char
        if len(vis_default[vis_curline]) > vis_maxchar[vis_curline]:
            vis_default[vis_curline] = vis_default[vis_curline][:-1]
        vis_update_text()

def vis_changealignment(type):
    vis_alignment[vis_curline] = type
    vis_update_text()

def vis_changepage(evt):
    global vis_curpage
    global vis_curline
    if evt == 'Title':
        vis_curpage = 1
        vis_curline = 0
    elif evt == 'Intro':
        vis_curpage = 2
        vis_curline = 2
    elif evt == 'Ending':
        vis_curpage = 3
        vis_curline = 9
    vis_update_text()

def vis_nextfield(evt):
    global vis_curline
    vis_curline += 1
    if vis_curpage == 1:
        if vis_curline >= 2:
            vis_curline = 0
    elif vis_curpage == 2:
        if vis_curline >= 9:
            vis_curline = 2
    elif vis_curpage == 3:
        if vis_curline >= 17:
            vis_curline = 9

    vis_update_text()
    return 'break'

def vis_backfield(evt):
    global vis_curline
    vis_curline -= 1
    if vis_curpage == 1:
        if vis_curline < 0:
            vis_curline = 1
    elif vis_curpage == 2:
        if vis_curline < 2:
            vis_curline = 8
    elif vis_curpage == 3:
        if vis_curline < 9:
            vis_curline = 16

    vis_update_text()
    return 'break'

def vis_backspace(evt):
    vis_default[vis_curline] = vis_default[vis_curline][:-1]
    vis_update_text()

def change_tab(evt):
    if str(n.index(n.select())) == "0":
        root.geometry('1036x768')
    elif str(n.index(n.select())) == "1":
        root.geometry('1036x224')

def vis_getwhitespace(i):
    r = [0,0]
    dif = vis_maxchar[i] - len(vis_default[i])
    if vis_alignment[i] == 'left':
        r = [0,0]
    elif vis_alignment[i] == 'center':
        r = [math.floor(dif/2),math.ceil(dif/2)]
    elif vis_alignment[i] == 'right':
        r = [dif,0]
    return r

def vis_update_cursor():
    if im_field.cursor_on:
        im_field.delete(im_field.vis_cursor)
        im_field.cursor_on = False
    else:
        im_field.vis_cursor = im_field.create_line(
            vis_offsetx[vis_curline] + len(vis_default[vis_curline])*24 + vis_getwhitespace(vis_curline)[0]*24,
            vis_offsety[vis_curline]-3,
            vis_offsetx[vis_curline] + len(vis_default[vis_curline])*24 + vis_getwhitespace(vis_curline)[0]*24,
            vis_offsety[vis_curline]+24, fill='white', activewidth=3)
        im_field.cursor_on = True
    im_field.after(500, vis_update_cursor)
    im_field.update()

ROM = False

root = Tk()
root.title("Metroid: The HEX Gen")
root.resizable(False,False)
root.geometry('1036x768')
root.configure(padx=12, pady=12)

f_visual = Frame(root)

im_field = Canvas(f_visual, width=768, height=672)
im_field.grid(row=1,column=1)
im_field.focus_set()

s_visualtext = StringVar()
s_visualtext.set("test")
im_field.cursor_on = True
im_field.vis_cursor = im_field.create_line(vis_offsetx[vis_curline] + vis_maxchar[vis_curline]*24, vis_offsety[vis_curline], vis_offsetx[vis_curline] + vis_maxchar[vis_curline]*24, vis_offsety[vis_curline]+24, fill='white')
im_field.after(1000, vis_update_cursor)
im_field.bind("<Key>", vis_type)
im_field.bind("<BackSpace>", vis_backspace)
im_field.bind("<Tab>", vis_nextfield)
im_field.bind("<Up>", vis_nextfield)
im_field.bind("<Shift-Tab>", vis_backfield)
im_field.bind("<Down>", vis_backfield)

f_tools = Frame(f_visual)

s_editing = StringVar(f_tools)
texts = {'Intro', 'Title', 'Ending'}
s_editing.set('Title')

l_char = OptionMenu(f_tools, s_editing, *sorted(texts), command=vis_changepage)
l_char.grid(row=1,column=1, pady=4)

f_align = Frame(f_tools)

l_alignment = Label(f_align, text="Alignment")
l_alignment.grid(row=1,column=1)

f_alignb = Frame(f_align)

im_lj = PhotoImage(file=dir_path + "/im/ico/leftj.png")
im_cj = PhotoImage(file=dir_path + "/im/ico/centerj.png")
im_rj = PhotoImage(file=dir_path + "/im/ico/rightj.png")

b_leftj = Button(f_alignb, image=im_lj, command= lambda: vis_changealignment("left"))
b_leftj.grid(row=1,column=0)
b_centerj = Button(f_alignb, image=im_cj, command= lambda: vis_changealignment("center"))
b_centerj.grid(row=1,column=1)
b_rightj = Button(f_alignb, image=im_rj, command= lambda: vis_changealignment("right"))
b_rightj.grid(row=1,column=2)

f_alignb.grid(row=3,column=1,sticky=NW)

f_align.grid(row=2,column=1,sticky=NW, pady=4)

f_file = Frame(f_tools)

b_getfile = Button(f_file, text="...", command=getROM)
b_getfile.grid(row=0,column=0, padx=2)

e_filepath = Text(f_file, pady=5, width=22, wrap=NONE, height=1)
e_filepath.config(state='disabled')
e_filepath.grid(row=0,column=1)

f_patchbuttons = Frame(f_file)
b_patchscreen = Button(f_patchbuttons, text="Patch Screen", command=patchROMScreen)
b_patchscreen.grid(row=1,column=0)
b_patchall = Button(f_patchbuttons, text="Patch All", command=patchROMAll)
b_patchall.grid(row=1,column=1, padx=4, pady=4)
f_patchbuttons.grid(row=1,column=1)

f_file.grid(row=3,column=1, pady=4)

f_tools.grid(row=1,column=2,sticky=NW, padx=8)

f_visual.grid(row=1,column=1)

if __name__ == "__main__":
    db = load_db()
    img_letters = load_images()
    vis_update_text()
    root.mainloop()
