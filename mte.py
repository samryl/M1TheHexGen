# This is where the GUI class is held.
import sys, itertools, math, re, os
from os import listdir
from os.path import isfile, join
from collections import OrderedDict
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class MTEApp():

    def __init__(self, dir_path):

        self.dir_path = dir_path

        self.ROM = False

        self.getROM()

        self._initOrganizers()
        ## INSERT READFROMROM() ##

        self.root = Tk()
        self.root.title("Metroid: The HEX Gen")
        self.root.resizable(False,False)
        self.root.geometry('1036x768')
        self.root.configure(padx=12, pady=12)

        self.f_visual = Frame(self.root)

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
        self.im_field.after(1000, self.vis_update_cursor)

        #self._initKeybinds()

        self.f_tools = Frame(self.f_visual)

        self.s_editing = StringVar(self.f_tools)
        texts = {'Intro', 'Title', 'Ending'}
        self.s_editing.set('Title')

        self.l_char = OptionMenu(self.f_tools, self.s_editing, *sorted(texts), command=self.vis_changepage)
        self.l_char.grid(row=1,column=1, pady=4)

        self.f_align = Frame(self.f_tools)

        self.l_alignment = Label(self.f_align, text="Alignment")
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

        self.f_file = Frame(self.f_tools)

        self.b_getfile = Button(self.f_file, text="...", command=self.getROM)
        self.b_getfile.grid(row=0,column=0, padx=2)

        self.e_filepath = Text(self.f_file, pady=5, width=22, wrap=NONE, height=1)
        self.e_filepath.config(state='disabled')
        self.e_filepath.grid(row=0,column=1)

        self.f_patchbuttons = Frame(self.f_file)
        self.b_patchscreen = Button(self.f_patchbuttons, text="Patch Screen", command=self.patchROMScreen)
        self.b_patchscreen.grid(row=1,column=0)
        self.b_patchall = Button(self.f_patchbuttons, text="Patch All", command=self.patchROMAll)
        self.b_patchall.grid(row=1,column=1, padx=4, pady=4)
        self.f_patchbuttons.grid(row=1,column=1)

        self.f_file.grid(row=4,column=1, pady=4)

        self.f_tools.grid(row=1,column=2,sticky=NW, padx=8)

        self.f_visual.grid(row=1,column=1)

        #self.root.mainloop()

        self.img_letters = self.load_images()

    def _initOrganizers(self):
        self.vis_curline = 1
        self.vis_curpage = 1
        self.vis_curindex = 0
        sf = 3

        self.vis_default = [
            " PUSH START BUTTON", "* 1986 NINTENDO",
            "EMERGENCY ORDER", "DEFEAT THE METROID OF",
            "THE PLANET ZEBETH AND", "DESTROY THE MOTHER BRAIN",
            "THE MECHANICAL LIFE VEIN", "GALAXY FEDERAL POLICE", "M510 ",
            "GREAT !!", "YOU FULFILED YOUR MISSION.",
            "IT WILL REVIVE PEACE IN ", "SPACE.",
            "BUT,IT MAY BE INVADED BY ", "THE OTHER METROID.",
            "PRAY FOR A TRUE PEACE IN ", "SPACE!"
            ]

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
        self.ROM = _romfile

    def vis_type(self, evt):
        if evt.char != "":
            strlist = list(self.vis_default[self.vis_curline])
            if self.vis_curindex < len(self.vis_default[self.vis_curline]):
                strlist[self.vis_curindex] = evt.char
            elif self.vis_curindex == len(self.vis_default[self.vis_curline]):
                strlist.append(evt.char)
            elif self.vis_curindex > len(self.vis_default[self.vis_curline]):
                dif = (self.vis_curindex - len(self.vis_default[self.vis_curline]))
                strlist.append(" "*dif + evt.char)
            self.vis_default[self.vis_curline] = "".join(strlist)
            if len(self.vis_default[self.vis_curline]) > self.vis_maxchar[self.vis_curline]:
                self.vis_default[self.vis_curline] = self.vis_default[self.vis_curline][:-1]
            self.vis_rightarrow(None)
            self.vis_update_text()

    def vis_changealignment(self, type):
        self.vis_alignment[self.vis_curline] = type
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
        if not self.vis_curindex > self.vis_maxchar[self.vis_curline]-1:
            self.vis_curindex += 1
        self.vis_update_text()

    def vis_homekey(self, evt):
        self.vis_curindex = 0
        self.vis_update_text()

    def vis_endkey(self, evt): # THIS ISN'T WORKING
        self.vis_curindex = self.vis_maxchar[vis_curline]-1
        self.vis_update_text()

    def vis_backspace(self, evt):
        strlist = list(self.vis_default[self.vis_curline])
        if not len(strlist) <= 0:
            strlist.pop(self.vis_curindex-1)
            self.vis_default[self.vis_curline] = "".join(strlist)
        self.vis_leftarrow(None)
        self.vis_update_text()

    def vis_getwhitespace(self, i):
        r = [0,0]
        dif = self.vis_maxchar[i] - len(self.vis_default[i])
        if self.vis_alignment[i] == 'left':
            r = [0,0]
        elif self.vis_alignment[i] == 'center':
            r = [math.floor(dif/2),math.ceil(dif/2)]
        elif self.vis_alignment[i] == 'right':
            r = [dif,0]
        return r

    def vis_update_cursor(self):
        if self.im_field.cursor_on:
            self.im_field.delete(self.im_field.vis_cursor)
            self.im_field.cursor_on = False
        else:
            self.im_field.vis_cursor = self.im_field.create_line(
                self.vis_offsetx[self.vis_curline] + self.vis_getwhitespace(self.vis_curline)[0]*12 + self.vis_curindex*24,
                self.vis_offsety[self.vis_curline]-3,
                self.vis_offsetx[self.vis_curline] + self.vis_getwhitespace(self.vis_curline)[0]*12 + self.vis_curindex*24,
                self.vis_offsety[self.vis_curline]+24, fill='white', activewidth=3)
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

        while i <= breakline:
            f = self.vis_default[i].replace("\t", "")
            reg = re.compile('[^a-zA-Z0-9\!\*\,\.\?\-\s]')
            f = reg.sub('', f)
            self.vis_default[i] = f
            t = 0

            if self.vis_alignment[i] == "left":
                _extra_offset = 0
            elif self.vis_alignment[i] == "center":
                _extra_offset = math.floor((self.vis_maxchar[i] - len(f)) / 2)*24
            elif self.vis_alignment[i] == "right":
                _extra_offset = (self.vis_maxchar[i] - len(f))*24

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

                self.im_field.create_image(self.vis_offsetx[i] + _extra_offset + t*24, self.vis_offsety[i], image=ph, anchor=NW)
                t += 1
            i += 1

        self.im_field.create_rectangle(self.vis_offsetx[self.vis_curline]-3,self.vis_offsety[self.vis_curline]-3,self.vis_offsetx[self.vis_curline]+24*self.vis_maxchar[self.vis_curline]+3,self.vis_offsety[self.vis_curline]+24,outline="red")
        self.im_field.update()
