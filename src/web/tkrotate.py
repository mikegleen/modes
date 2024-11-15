"""

"""
import argparse
import os.path
from tkinter import *

import PIL
from PIL import ImageTk, Image
from tkinter import ttk
import sys

# The canvas must be square
CANVAS_SIZE = 800


class Rotate:
    def __init__(self):
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe = ttk.Frame(self.root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky="nsew")
        self.canvas = Canvas(self.mainframe, width=CANVAS_SIZE,
                             height=CANVAS_SIZE)
        self.canvas.grid()
        self.infiles = iter(sorted(os.listdir(indirname)))
        # init vars here to stop PyCharm whining
        self.activefile = None
        self.inpath = self.outpath = None
        self.img = self.display_img = self.photoimg = None
        self.init_img()
        self.root.bind('<Down>', lambda e: self.rotate180())
        self.root.bind('<Left>', lambda e: self.rotate90())
        self.root.bind('<Right>', lambda e: self.rotate270())
        self.root.bind('<space>', lambda e: self.nextimg())
        self.root.mainloop()

    def init_img(self):
        """
        Iterate over the files in the input directory until we find one we
        can open.
        :return: self.img contains the new image. If none is found, exit.
        """
        while True:
            try:
                self.activefile = next(self.infiles)
            except StopIteration:
                print('Exiting.')
                sys.exit()
            self.inpath = os.path.join(indirname, self.activefile)
            self.outpath = os.path.join(outdirname, self.activefile)
            try:
                self.img = Image.open(self.inpath)
            except PIL.UnidentifiedImageError:
                print('Skipping:', self.inpath)
                continue
            self.rotate_n(0)
            break

    def rotate_n(self, degrees):
        if degrees:  # degrees == 0 if called from __init__
            self.img = self.img.rotate(degrees, expand=True)
        self.display_img = self.img.copy()
        self.display_img.thumbnail((CANVAS_SIZE - 100, CANVAS_SIZE - 100))
        self.photoimg = ImageTk.PhotoImage(image=self.display_img)
        self.canvas.create_image(10, 10, image=self.photoimg, anchor='nw')

    def rotate180(self):
        self.rotate_n(180)

    def rotate90(self):
        self.rotate_n(90)

    def rotate270(self):
        self.rotate_n(270)

    def nextimg(self):
        """
        Save the current image and load the next one.
        :return: Image loaded and displayed or exit if no more images
        """
        self.img.save(self.outpath, quality=100)  # , subsampling=0)
        self.canvas.delete('all')
        print(f'nextimg: {self.activefile}')
        self.init_img()


def getargs():
    parser = argparse.ArgumentParser(description='''
    Display images and accept commands to rotate them.
        ''')
    parser.add_argument('indir', help='''
        The input directory''')
    parser.add_argument('outdir', help='''
        The output directory to contain the (possibly) rotated image.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    _args = parser.parse_args()
    if not os.path.isdir(_args.indir):
        raise ValueError('First parameter must be the input directory.')
    if not os.path.isdir(_args.outdir):
        raise ValueError('Second parameter must be the output directory.')
    return _args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    args = getargs()
    indirname = args.indir
    outdirname = args.outdir
    Rotate()
