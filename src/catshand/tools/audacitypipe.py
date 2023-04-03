import os, sys, re, datetime
from pathlib import Path 
import argparse

def audacitypipe(args): 
    
    from catshand.audacitytool import audacitytool

    prj_path = args.prj_path
    mat_path = args.mat_path

    audtl = audacitytool(prj_path, mat_path)
    audtl.importrecording()
    audtl.importmaterial()
    audtl.importhighlight()
    audtl.addmusic(default_music = "Middle_01.wav")
    #audtl.midedit()
    return

def add_subparser(subparsers):
    description = 'Auddacity_tool controls Audacity via macro PIPE.'
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('audacitypipe', help=description)
    subparsers.add_argument('-i', '--prj_path', help = 'input folder for editing projects')
    subparsers.add_argument('-m', '--mat_path', help = 'the folder of editing materials')
    subparsers.set_defaults(func=audacitypipe)
    # args = subparsers.parse_args()
    return

# if __name__ == "__main__":
#     add_subparser()