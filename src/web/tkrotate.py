"""

"""
import argparse
import os.path
from tkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
import sys


class Rotate:
    def __init__(self):
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe = ttk.Frame(self.root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.canvas = Canvas(self.mainframe, width=800, height=800)
        self.canvas.grid()
        self.activefile = infilename
        self.basename = os.path.basename(infilename)
        self.outfilename = os.path.join(outdirname, self.basename)
        self.img = Image.open(self.activefile)
        self.photoimg = ImageTk.PhotoImage(image=self.img)
        self.img_on_canvas = self.canvas.create_image(10, 10,
                                                      image=self.photoimg,
                                                      anchor='nw')
        self.root.bind('<Down>', lambda e: self.rotate180())
        self.root.bind('<Left>', lambda e: self.rotate90())
        self.root.bind('<Right>', lambda e: self.rotate270())
        self.root.bind('<space>', lambda e: self.nextimg())
        self.root.mainloop()

    def rotate_n(self, degrees):
        self.canvas.delete('all')
        self.img = self.img.rotate(degrees, expand=True)
        self.photoimg = ImageTk.PhotoImage(image=self.img)
        self.canvas.itemconfig(self.img_on_canvas, image=self.photoimg)
        self.img_on_canvas = self.canvas.create_image(10, 10,
                                                      image=self.photoimg,
                                                      anchor='nw')
        # print('rotate')

        # sys.exit()

    def rotate180(self):
        self.rotate_n(180)

    def rotate90(self):
        self.rotate_n(90)

    def rotate270(self):
        self.rotate_n(270)

    def nextimg(self):
        print('nextimg')


def getargs():
    parser = argparse.ArgumentParser(description='''
    Display images and accept commands to rotate them.
        ''')
    parser.add_argument('infile', help='''
        The input image file''')
    parser.add_argument('outdir', help='''
        The output directory to contain the (possibly) rotated image.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    _args = parser.parse_args()
    if not os.path.isdir(_args.outdir):
        raise ValueError('Second parameter must be the output directory.')
    return _args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    args = getargs()
    infilename = args.infile
    outdirname = args.outdir
    Rotate()
