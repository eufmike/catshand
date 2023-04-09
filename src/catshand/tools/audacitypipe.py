import os, sys, re, datetime
from pathlib import Path 
import argparse

def audacitypipe(args): 
    
    from catshand.audacitytool import audacitytool

    prj_path = args.prj_path
    ip_dir = args.input_dir

    audtl = audacitytool(prj_path, ip_dir)
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
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_path', help = 'input folder for editing projects')
    # required_group.add_argument('-m', '--mat_path', help = 'the folder of editing materials')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with wav files.')
    subparsers.set_defaults(func=audacitypipe)
    
    return

# if __name__ == "__main__":
#     add_subparser()