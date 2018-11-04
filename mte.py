# This is where the GUI class is held.


## ON TYPE, THIS SHOULD ALSO UPDATE THE RAW PART OF THE DICT, THEN WE DON'T HAVE TO TRANSLATE ON PATCH [ ]
## THE EDITOR WILL REIGN IN THE LENGTH OF THE STRINGS SO WE DON'T HAVE TO WORRY ABOUT OVERWRITING SOMETHING
## NEED TO DO THAT NEXT SO IT WILL PATCH CORRECTLY [ ]
## WE NEED TO MAKE THE GUI SPACE EDITOR AND SEPARATE EVERYTHING INTO BANKS [ ]


import sys, itertools, math, re, os, pprint, random, copy
from os import listdir
from os.path import isfile, join
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class ColorBlock():
    background1 = '#212121'
    background1hov = '#3d3d3d'
    background2 = '#303030'
    background2hov = '#4f4f4f'
    text = '#dbdbdb'
    texthov = '#f7f7f7'

class MTEApp():

    def __init__(self, dir_path, neshex):

        self.dir_path = dir_path

        self.pp = pprint.PrettyPrinter(indent=2)

        self.ns = neshex

        self._initOrganizers()

        self.root = Tk()
        self.root.title("Metroid: The HEX Gen")
        self.root.resizable(False,False)
        self.root.geometry('1018x700')
        self.root.configure(padx=12, pady=12, bg=ColorBlock.background1)

        self.f_visual = Frame(self.root, bg=ColorBlock.background1)

        self.img_letters = self.load_images()

        self.im_field = Canvas(self.f_visual, width=768, height=672)
        self.im_field.grid(row=1,column=1)
        self.im_field.focus_set()

        self.s_visualtext = StringVar()
        self.s_visualtext.set("test")
        self.im_field.cursor_on = True
        self.im_field.vis_cursor = self.im_field.create_line(self.vis_offsetx[self.vis_curline] + self.vis_maxchar[self.vis_curline]*24,
                                                             self.vis_offsety[self.vis_curline],
                                                             self.vis_offsetx[self.vis_curline] + self.vis_maxchar[self.vis_curline]*24,
                                                             self.vis_offsety[self.vis_curline]+24, fill='white')

        self._initKeybinds()

        self.f_tools = Frame(self.f_visual, bg=ColorBlock.background1)

        self.s_editing = StringVar(self.f_tools)
        texts = {'Intro', 'Title', 'Ending'}
        self.s_editing.set('Title')

        self.l_char = OptionMenu(self.f_tools, self.s_editing, *sorted(texts), command=self.vis_changepage)
        self.l_char.config(bg=ColorBlock.background1, fg=ColorBlock.text, activebackground=ColorBlock.background1hov, activeforeground=ColorBlock.texthov)
        self.l_char.grid(row=1,column=1, pady=4)

        self.f_align = Frame(self.f_tools, bg=ColorBlock.background1)

        self.l_alignment = Label(self.f_align, text="Alignment", bg=ColorBlock.background1, fg=ColorBlock.text, relief='flat')
        self.l_alignment.grid(row=1,column=1)

        self.f_alignb = Frame(self.f_align)

        self.im_lj = PhotoImage(master=self.f_alignb, file=self.dir_path + "/im/ico/leftj.png")
        self.im_cj = PhotoImage(master=self.f_alignb, file=self.dir_path + "/im/ico/centerj.png")
        self.im_rj = PhotoImage(master=self.f_alignb, file=self.dir_path + "/im/ico/rightj.png")

        self.b_leftj = Button(self.f_alignb, image=self.im_lj, command= lambda: self.vis_changealignment("left"))
        self.b_leftj.grid(row=1,column=0)
        self.b_centerj = Button(self.f_alignb, image=self.im_cj, command= lambda: self.vis_changealignment("center"))
        self.b_centerj.grid(row=1,column=1)
        self.b_rightj = Button(self.f_alignb, image=self.im_rj, command= lambda: self.vis_changealignment("right"))
        self.b_rightj.grid(row=1,column=2)

        self.f_alignb.grid(row=3,column=1,sticky=NW)

        self.f_align.grid(row=2,column=1,sticky=NW, pady=4)

        self.f_file = Frame(self.f_tools, bg=ColorBlock.background1)

        self.b_getfile = Button(self.f_file, text="...", command=self.getROM)
        self.b_getfile.grid(row=0,column=0, padx=2)

        self.e_filepath = Text(self.f_file, pady=5, width=22, wrap=NONE, height=1)
        self.e_filepath.config(state='disabled')
        self.e_filepath.grid(row=0,column=1)

        self.f_patchbuttons = Frame(self.f_file, bg=ColorBlock.background1)
        self.b_patchall = Button(self.f_patchbuttons, text="Patch All", command=self.patchROMAll)
        self.b_patchall.grid(row=1,column=1, padx=4, pady=4)
        self.f_patchbuttons.grid(row=1,column=1)

        self.f_utils = Frame(self.f_tools, bg=ColorBlock.background1)
        self.b_openlineeditor = Button(self.f_utils, text="Line Editor", command=self.openLineEditor)
        self.b_openlineeditor.grid(row=0,column=0)
        self.f_utils.grid(row=5,column=1)

        self.f_file.grid(row=4,column=1, pady=4)

        self.f_tools.grid(row=1,column=2,sticky=NW, padx=8)

        self.f_visual.grid(row=1,column=1)

        self.ROM = self.getROM()

        self.im_field.focus_force()

        self.vis_lines = self.readFromROM()

        self.im_field.after(1000, self.vis_update_cursor)
        self.im_field.bind("<Key>", self.vis_type)

        self.vis_update_text()

        self.root.mainloop()

    def _initOrganizers(self):

        self.vis_curline = 1
        self.vis_curpage = 1
        self.vis_curindex = 0

        sf = 3

        self.vis_default = {}

        #[
        #    " PUSH START BUTTON", "* 1986 NINTENDO",
        #    "EMERGENCY ORDER", "DEFEAT THE METROID OF",
        #    "THE PLANET ZEBETH AND", "DESTROY THE MOTHER BRAIN",
        #    "THE MECHANICAL LIFE VEIN", "GALAXY FEDERAL POLICE", "M510 ",
        #    "GREAT !!", "YOU FULFILED YOUR MISSION.",
        #    "IT WILL REVIVE PEACE IN ", "SPACE.",
        #    "BUT,IT MAY BE INVADED BY ", "THE OTHER METROID.",
        #    "PRAY FOR A TRUE PEACE IN ", "SPACE!"
        #    ]

        self.vis_alignment = ["left", "left", "left", "left", "left", "left", "left", "left", "right", "left", "left", "left", "left", "left", "left", "left", "left"]
        self.vis_maxchar = [21, 18, 15, 26, 26, 26, 26, 21, 18, 8, 26, 25, 6, 25, 18, 25, 6]
        self.vis_offsetx = [56*sf, 72*sf, 64*sf, 32*sf, 32*sf, 32*sf, 32*sf, 56*sf, 72*sf, 104*sf, 24*sf, 24*sf, 16*sf, 24*sf, 16*sf, 24*sf, 16*sf]
        self.vis_offsety = [128*sf, 144*sf, 24*sf, 56*sf, 72*sf, 88*sf, 104*sf, 128*sf, 144*sf, 16*sf, 40*sf, 56*sf, 72*sf, 88*sf, 104*sf, 120*sf, 136*sf]

    def _initKeybinds(self):
        self.im_field.bind("<Key>", self.vis_type)
        self.im_field.bind("<BackSpace>", self.vis_backspace)
        self.im_field.bind("<Tab>", self.vis_nextfield)
        self.im_field.bind("<Up>", self.vis_nextfield)
        self.im_field.bind("<Shift-Tab>", self.vis_backfield)
        self.im_field.bind("<Down>", self.vis_backfield)
        self.im_field.bind("<Left>", self.vis_leftarrow)
        self.im_field.bind("<Right>", self.vis_rightarrow)
        self.im_field.bind("<Home>", self.vis_homekey)
        self.im_field.bind("<End>", self.vis_endkey)

    def load_images(self):
        a = [f for f in listdir(self.dir_path + "/im/letters") if isfile(join(self.dir_path + "/im/letters", f))]
        i = {}
        for x in a:
            i[x] = PhotoImage(file=self.dir_path + "/im/letters/" + x)
        i["bg"] = PhotoImage(file=self.dir_path + "/im/1.png")
        i["bg2"] = PhotoImage(file=self.dir_path + "/im/2.png")
        i["bg3"] = PhotoImage(file=self.dir_path + "/im/3.png")
        return i

    def getROM(self):
        _romfile = filedialog.askopenfilename(initialdir=self.dir_path,title = "Select ROM")
        try: #in the case that the GUI is not built [i.e. on startup]
            self.e_filepath.config(state='normal')
            self.e_filepath.delete("1.0",END)
            self.e_filepath.insert("1.0",_romfile)
            self.e_filepath.config(state='disabled')
        except:
            print("GUI is not built, skipping field assignment.")
        return _romfile

    def readFromROM(self):
        f = open(self.ROM, "r+b")
        _lines = self.ns.readTitleLines(f)
        self.pp.pprint(_lines)
        f.close()
        return _lines

    def vis_type(self, evt):
        if evt.char != "":

            strlist = list(self.vis_lines[self.vis_curline]["text"])

            if self.vis_curindex < len(self.vis_lines[self.vis_curline]["text"]):
                strlist[self.vis_curindex] = evt.char
            elif self.vis_curindex == len(self.vis_lines[self.vis_curline]["text"]):
                strlist.append(evt.char)
            elif self.vis_curindex > len(self.vis_lines[self.vis_curline]["text"]):
                dif = (self.vis_curindex - len(self.vis_lines[self.vis_curline]["text"]))
                strlist.append(" "*dif + evt.char)
            self.vis_lines[self.vis_curline]["text"] = "".join(strlist)
            if len(self.vis_lines[self.vis_curline]["text"]) > self.vis_lines[self.vis_curline]["length"]:
                self.vis_lines[self.vis_curline]["text"] = self.vis_lines[self.vis_curline]["text"][:-1]
            self.vis_rightarrow(None)
            self.vis_update_text()

    def vis_changealignment(self, type):
        self.vis_lines[self.vis_curline]["alignment"] = type
        self.vis_update_text()

    def vis_changepage(self, evt):
        if evt == 'Title':
            self.vis_curpage = 1
            self.vis_curline = 0
        elif evt == 'Intro':
            self.vis_curpage = 2
            self.vis_curline = 2
        elif evt == 'Ending':
            self.vis_curpage = 3
            self.vis_curline = 9
        self.vis_update_text()

    def vis_nextfield(self, evt):
        self.vis_curline += 1
        if self.vis_curpage == 1:
            if self.vis_curline >= 2:
                self.vis_curline = 0
        elif self.vis_curpage == 2:
            if self.vis_curline >= 9:
                self.vis_curline = 2
        elif self.vis_curpage == 3:
            if self.vis_curline >= 17:
                self.vis_curline = 9

        self.vis_update_text()
        return 'break'

    def vis_backfield(self, evt):
        self.vis_curline -= 1
        if self.vis_curpage == 1:
            if self.vis_curline < 0:
                self.vis_curline = 1
        elif self.vis_curpage == 2:
            if self.vis_curline < 2:
                self.vis_curline = 8
        elif self.vis_curpage == 3:
            if self.vis_curline < 9:
                self.vis_curline = 16

        self.vis_update_text()
        return 'break'

    def vis_leftarrow(self, evt):
        if not self.vis_curindex <= 0:
            self.vis_curindex -= 1
        self.vis_update_text()

    def vis_rightarrow(self, evt):
        if not self.vis_curindex > self.vis_lines[self.vis_curline]["length"]-1:
            self.vis_curindex += 1
        self.vis_update_text()

    def vis_homekey(self, evt):
        self.vis_curindex = 0
        self.vis_update_text()

    def vis_endkey(self, evt):
        self.vis_curindex = len(self.vis_lines[self.vis_curline]["text"])
        self.vis_update_text()

    def vis_backspace(self, evt):
        strlist = list(self.vis_lines[self.vis_curline]["text"])
        if not len(strlist) <= 0:
            strlist.pop(self.vis_curindex-1)
            self.vis_lines[self.vis_curline]["text"] = "".join(strlist)
        self.vis_leftarrow(None)
        self.vis_update_text()

    def vis_getwhitespace(self, i):
        r = [0,0]
        dif = self.vis_lines[i]["length"] - len(self.vis_lines[i]["text"])
        if self.vis_lines[i]["alignment"] == 'left':
            r = [0,0]
        elif self.vis_lines[i]["alignment"] == 'center':
            r = [math.floor(dif/2),math.ceil(dif/2)]
        elif self.vis_lines[i]["alignment"] == 'right':
            r = [dif,0]
        return r

    def vis_update_cursor(self):
        if self.im_field.cursor_on:
            self.im_field.delete(self.im_field.vis_cursor)
            self.im_field.cursor_on = False
        else:
            self.im_field.vis_cursor = self.im_field.create_line(
                self.vis_lines[self.vis_curline]["x"]*24 + self.vis_getwhitespace(self.vis_curline)[0]*24 + self.vis_curindex*24,
                self.vis_lines[self.vis_curline]["y"]*24-3,
                self.vis_lines[self.vis_curline]["x"]*24 + self.vis_getwhitespace(self.vis_curline)[0]*24 + self.vis_curindex*24,
                self.vis_lines[self.vis_curline]["y"]*24+24, fill='white', activewidth=3)
            self.im_field.cursor_on = True
        self.im_field.after(500, self.vis_update_cursor)
        self.im_field.update()

    def vis_update_text(self):
        self.im_field.delete("all")

        if self.vis_curpage == 1:
            self.im_field.create_image(0, 0, image=self.img_letters["bg"], anchor=NW)
            i = 0
            breakline = 1
        elif self.vis_curpage == 2:
            self.im_field.create_image(0, 0, image=self.img_letters["bg2"], anchor=NW)
            i = 2
            breakline = 8
        elif self.vis_curpage == 3:
            self.im_field.create_image(0, 0, image=self.img_letters["bg3"], anchor=NW)
            i = 9
            breakline = 16

        i = 0
        for x in self.vis_lines: # for every line

            if (((self.vis_lines[i]["section"]-32)) // 4)+1 == self.vis_curpage: # if it's on the current screen

                # DRAW
                f = self.vis_lines[i]["text"].replace("\t", "")
                reg = re.compile('[^a-zA-Z0-9\!\*\,\.\?\-\s]')
                f = reg.sub('', f)
                self.vis_lines[i]["text"] = f

                if self.vis_lines[i]["alignment"] == "left":
                    _extra_offset = 0
                elif self.vis_lines[i]["alignment"] == "center":
                    _extra_offset = math.floor((self.vis_lines[i]["length"] - len(f)) / 2)*24
                elif self.vis_lines[i]["alignment"] == "right":
                    _extra_offset = (self.vis_lines[i]["length"] - len(f))*24

                t = 0
                for l in f:
                    if l == "?":
                        ph = self.img_letters["question.png"]
                    elif l == " ":
                        ph = self.img_letters["space.png"]
                    elif l == "*":
                        ph = self.img_letters["copyright.png"]
                    elif l == ".":
                        ph = self.img_letters["period.png"]
                    elif l == ",":
                        ph = self.img_letters["comma.png"]
                    elif l.islower():
                        ph = self.img_letters[l + "l.png"]
                    else:
                        ph = self.img_letters[l + ".png"]

                    self.im_field.create_image(self.vis_lines[i]["x"]*24 + _extra_offset + t*24, self.vis_lines[i]["y"]*24, image=ph, anchor=NW)
                    t += 1
            i += 1

        self.im_field.create_rectangle(
            self.vis_lines[self.vis_curline]["x"]*24-3,
            self.vis_lines[self.vis_curline]["y"]*24-3,
            self.vis_lines[self.vis_curline]["x"]*24+24*self.vis_lines[self.vis_curline]["length"]+3,
            self.vis_lines[self.vis_curline]["y"]*24+24,outline="red")
        print(self.vis_lines[self.vis_curline]["x"]*24-3,
        self.vis_lines[self.vis_curline]["y"]*24-3,
        self.vis_lines[self.vis_curline]["x"]*24+24*self.vis_lines[self.vis_curline]["length"]+3,
        self.vis_lines[self.vis_curline]["y"]*24+24)
        self.im_field.update()

    def patchROMAll(self):

        if self.ROM != False:

            f = open(self.ROM, "r+b")

            r = copy.deepcopy(self.vis_lines)
            t = []

            i = 0
            for _entry in r: # FOR EVERY LINE

                _line = _entry["text"]
                t.append(_line) # This SHOULD set the index to whatever i is since we're just going forward

                if len(_line) < r[i]["length"]:

                    _dif = r[i]["length"] - len(_line)

                    # ADD WHITESPACE
                    if r[i]["alignment"] == 'left':
                        t[i] = _line + " "*_dif
                    elif r[i]["alignment"] == 'center':
                        t[i] = " "*math.floor(_dif/2) + _line + " "*math.ceil(_dif/2)
                    elif r[i]["alignment"] == 'right':
                        t[i] = " "*_dif + _line

                r[i]["text"] = self.ns.translate_string_to_hex(t[i])
                t[i] = self.ns.translate_string_to_hex(t[i])

                i += 1

            self.pp.pprint(self.vis_lines)

            # BANK 1
            _writing_offset = "0x000510"
            _write_base = "0x000510"
            for _line in r:
                if _line["bank"] == 1:
                    if _line["writestart"] != _write_base: # if new writespace
                        _writing_offset = _line["writestart"]
                        _write_base = _line["writestart"]

                    self.ns.writeHexString(f, _writing_offset,
                        str(self.ns.pad_value(str(self.ns.encodeCoordinates(_line["x"], _line["y"], _line["screen"])[0][2:]))))
                    _writing_offset = hex(int(_writing_offset, base=16) + 1)

                    self.ns.writeHexString(f, _writing_offset,
                        str(self.ns.pad_value(str(self.ns.encodeCoordinates(_line["x"], _line["y"], _line["screen"])[1][2:]))))
                    _writing_offset = hex(int(_writing_offset, base=16) + 1)

                    self.ns.writeHexString(f, _writing_offset,
                        str(self.ns.pad_value(hex(_line["length"])[2:])))
                    _writing_offset = hex(int(_writing_offset, base=16) + 1)

                    self.ns.writeHexString(f, _writing_offset, _line["text"])
                    _writing_offset = hex(int(_writing_offset, base=16) + _line["length"])

            f.close()

    def openLineEditor(self):
        self.w_lineeditor = MTELineEditor(self)

class MTELineEditor(Toplevel):

    #### PRESPLAIN
    ##
    ## [√] This class will need access to the following objects from the parent class:
    ##  - vis_lines
    ##  - vis_curline
    ##
    ## [√] It will need to edit these as well
    ##
    ## [√] The code will draw a series of rectangles on a canvas object, keeping track of the X coordinate
    ## of each rectangle's beginning and end.
    ##
    ## [√] Left mouse click over the canvas will trigger code, which says basically:
    ## if(mouse.x within range of a beginning or end coord){
    ##     begin_drag()
    ## }
    ##
    ## [√] Once the drag is complete, the proper vis_lines entries will be adjusted to the proper values.
    ##
    ## [ ] There will also be a button which launches yet another dialog asking the length of the new string
    ## to be added. It will need to automatically guess the value based on space remaining (capped at 20).
    ##
    ## [ ] There will need to be a tab for each bank of text.
    ##
    ## [√] There will need to also be spinbox editors for length and content of the lines
    ##
    ## [ ] There will need to be a raw hex editor containing all the data from the bank
    ##
    ## [ ] There will need to be an editor for the X and Y coordinates which automatically updates the
    ## section and offset values
    ##
    ## [√] My tea is cold
    ##

    def __init__(self, master):

        Toplevel.__init__(self)

        self.title('MTE Line Editor')

        self.resizable(False,False)
        self.geometry('804x240')

        self.p = master

        self.f_main = Frame(self,padx=4,pady=4)

        self.f_data = Frame(self.f_main)

        self.l_plaintext = Label(self.f_data,text="Text: ")
        self.l_plaintext.grid(row=0,column=0,sticky=E)

        self.s_curtext = StringVar()
        self.s_curtext.set("")
        self.e_plaintext = Entry(self.f_data, textvariable=self.s_curtext, width=60)
        self.e_plaintext.grid(row=0,column=1,sticky=W)

        self.l_length = Label(self.f_data,text="Length: ")
        self.l_length.grid(row=1,column=0,sticky=E)

        self.l_curtext = StringVar()
        self.l_curtext.set("0")
        self.e_length = Spinbox(self.f_data, from_=0, to=32, width=2, textvariable=self.l_curtext)
        self.e_length.grid(row=1,column=1,sticky=W)
        self.e_length['state'] = DISABLED

        self.l_coords = Label(self.f_data,text="X/Y: ")
        self.l_coords.grid(row=2,column=0,sticky=E)

        self.f_coordsentry = Frame(self.f_data)

        self.s_coordsX = StringVar()
        self.s_coordsX.set("0")
        self.s_coordsY = StringVar()
        self.s_coordsY.set("0")
        self.e_coordsX = Spinbox(self.f_coordsentry, from_=0, to=32, width=2, textvariable=self.s_coordsX)
        self.e_coordsX.grid(row=0,column=0)
        self.e_coordsY = Spinbox(self.f_coordsentry, from_=0, to=32, width=2, textvariable=self.s_coordsY)
        self.e_coordsY.grid(row=0,column=1)

        self.f_coordsentry.grid(row=2,column=1,sticky=W)

        self.f_data.grid(row=0,column=0,sticky=W)

        _canvas_width = 800
        _canvas_height = 64
        self.c_lines = Canvas(self.f_main, width=_canvas_width, height=_canvas_height)
        self.c_lines.grid(row=1,column=0)
        self.c_lines.data = []
        _i = 0
        _n = 0
        colors = ["blue","orange","purple","pink","grey","black","yellow","teal","brown"]
        self.bank_lengths = [0,0,0]
        self.current_bank = 1

        for _line in self.p.vis_lines:
            self.c_lines.data.append({
                "x1": _i,
                "x2": _i+(_line["length"]/self.bank_length(1))*_canvas_width,
                "length": _line["length"],
                "index": _n,
                "text": _line["text"],
                "bank": _line["bank"],
                "color": colors[_n],
                "id": _line["id"],
                "xcoord": _line["x"],
                "ycoord": _line["y"]
            })
            self.bank_lengths[_line["bank"]-1] += 1
            _i += (_line["length"]/self.bank_length(1))*_canvas_width
            _n += 1

        self.c_lines.cevent = { "xoff": 0, "yoff": 0 }
        self.c_lines.selected = 0
        self.c_lines.mousexdiff = 0
        self.c_lines.lheight = _canvas_height
        self.c_lines.MOVINGRECT = None
        self.c_lines.MOVINGRECTLINE = None
        self.c_lines.MOVINGHOVERIND = None

        self.c_lines.bind("<Button 1>",self.lineclicked)
        #self.c_lines.bind("<B1-Motion>",self.linedrag)
        #self.c_lines.bind("<ButtonRelease-1>",self.linerelease)
        self.c_lines.bind("<Left>",self.vis_leftarrow)
        self.c_lines.bind("<Right>",self.vis_rightarrow)

        self.s_curtext.trace("w", self.vis_textchanged)
        self.s_coordsX.trace("w", self.vis_coordchangedX)
        self.s_coordsY.trace("w", self.vis_coordchangedY)

        self.f_main.grid(row=0,column=0,sticky=W)

        #self.c_lines.focus_set()

        self.vis_update_everything()

    def vis_coordchangedX(self, *args):
        self.c_lines.data[self.c_lines.selected]["xcoord"] = int(self.s_coordsX.get())

    def vis_coordchangedY(self, *args):
        self.c_lines.data[self.c_lines.selected]["ycoord"] = int(self.s_coordsY.get())

    def vis_textchanged(self, *args):
        self.c_lines.data[self.c_lines.selected]["text"] = self.s_curtext.get()

    def vis_rightarrow(self,event):
        self.c_lines.selected += 1
        if self.c_lines.selected >= self.bank_lengths[self.current_bank-1]:
            self.c_lines.selected = 0
        self.vis_update_everything()

    def vis_leftarrow(self,event):
        self.c_lines.selected -= 1
        if self.c_lines.selected < 0:
            self.c_lines.selected = self.bank_lengths[self.current_bank-1]-1
        self.vis_update_everything()

    def lineclicked(self,event):
        self.c_lines.mousexdiff = 0
        for _x in self.c_lines.data:
            if event.x < _x["x2"] and event.x > _x["x1"]:
                self.c_lines.selected = _x["index"]
                self.c_lines.cevent["xoff"] = event.x - _x["x1"]
                self.c_lines.cevent["yoff"] = event.y
                self.vis_update_everything()
                break

    def linedrag(self,event):

        self.c_lines.mousexdiff += event.x - self.c_lines.mousexdiff
        self.c_lines.delete(self.c_lines.MOVINGRECT)
        self.c_lines.delete(self.c_lines.MOVINGRECTLINE)
        self.c_lines.delete(self.c_lines.MOVINGHOVERIND)
        for _x in self.c_lines.data:
            if event.x < _x["x2"] and event.x >= _x["x1"]:
                self.c_lines.MOVINGHOVERIND = self.c_lines.create_line(_x["x1"]-2, 0, _x["x1"]-2, self.c_lines.lheight, fill="red", width=4)
                break
        self.c_lines.MOVINGRECT = self.c_lines.create_rectangle(
            event.x-self.c_lines.cevent["xoff"], event.y-self.c_lines.cevent["yoff"],
            event.x-self.c_lines.cevent["xoff"]+(self.c_lines.data[self.c_lines.selected]["x2"]-self.c_lines.data[self.c_lines.selected]["x1"]),
            event.y-self.c_lines.cevent["yoff"]+self.c_lines.lheight, fill="", outline="red", width=2)
        self.c_lines.MOVINGRECTLINE = self.c_lines.create_line(
            event.x-self.c_lines.cevent["xoff"], event.y-self.c_lines.cevent["yoff"],
            event.x-self.c_lines.cevent["xoff"]+(self.c_lines.data[self.c_lines.selected]["x2"]-self.c_lines.data[self.c_lines.selected]["x1"]),
            event.y-self.c_lines.cevent["yoff"]+self.c_lines.lheight, fill="red", width=2)

    def bank_length(self,bank):
        if bank == 1: return 226

    def linerelease(self,event):

        self.c_lines.delete(self.c_lines.MOVINGRECT)

        if self.c_lines.mousexdiff <= 4: return "break"

        self.c_lines.mousexdiff = 0

        for _x in self.c_lines.data:
            if event.x < _x["x2"] and event.x >= _x["x1"]:

                _ind = int(_x["index"]) # Get the current index of the matching line

                _cl = self.c_lines.data[self.c_lines.selected] # CURRENTLY SELECTED LINE
                self.c_lines.data.pop(self.c_lines.selected) # POP THE OLD LINE
                self.c_lines.data.insert(_ind, _cl) # INSERTS IT AT THE NEW INDEX (SHIFTING EVERYING TO THE RIGHT)

                _i = 0
                _n = 0
                for _a in self.c_lines.data: # RESET ALL INDEX VALUES
                    _a["index"] = _n
                    _a["x1"] = _i
                    _a["x2"] = _i+(_a["length"]/self.bank_length(1))*self.c_lines.winfo_width()
                    _n += 1
                    _i += (_a["length"]/self.bank_length(1))*self.c_lines.winfo_width()

                self.c_lines.selected = _ind
                break

        self.vis_update_everything()

    def vis_drawrectangle(self, x1, y1, x2, y2, color, outline='',width=0):
        self.c_lines.create_rectangle(x1,y1,x2,y2,fill=color,outline=outline,width=width)
        self.c_lines.update()

    def vis_drawgraph(self, bank, bank_length):
        _basewidth = self.c_lines.winfo_width()
        if _basewidth <= 1:
            _basewidth = 804

        _i = 0
        _n = 0
        while _n < len(self.c_lines.data):
            _line = self.c_lines.data[_n]
            if _line["bank"] == bank:
                self.vis_drawrectangle(
                    _i, 0,
                    _i+(_line["length"]/bank_length)*_basewidth, self.c_lines.lheight,
                    _line["color"]
                )
                _i += (_line["length"]/bank_length)*_basewidth
                _n += 1

    def clamp(self, minim, maxim, val):
        return max(minim, min(val, maxim))

    def vis_update_canvas(self):
        self.c_lines.delete(ALL)
        self.vis_drawgraph(1, self.bank_length(1))
        self.vis_drawrectangle(
            self.clamp(3,self.c_lines.winfo_width(),self.c_lines.data[self.c_lines.selected]["x1"]),
            3,
            self.c_lines.data[self.c_lines.selected]["x2"],
            self.c_lines.lheight, "", outline="red", width=2
        )

    def vis_update_everything(self):
        self.vis_update_canvas()
        self.l_curtext.set(self.c_lines.data[self.c_lines.selected]["length"])
        self.s_curtext.set(self.c_lines.data[self.c_lines.selected]["text"])
        self.s_coordsX.set(self.c_lines.data[self.c_lines.selected]["xcoord"])
        self.s_coordsY.set(self.c_lines.data[self.c_lines.selected]["ycoord"])

        for _line in self.c_lines.data:
            for _data in self.p.vis_lines:
                if _data["id"] == _line["id"]:
                    #print(_line["text"],_line["xcoord"],_line["ycoord"], _data["y"])
                    _data["length"] = _line["length"]
                    _data["text"] = _line["text"]
                    _data["x"] = _line["xcoord"]
                    _data["y"] = _line["ycoord"]

        self.p.im_field.update()
