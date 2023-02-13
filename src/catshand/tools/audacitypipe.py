import os, sys, re, datetime
from pathlib import Path 
from catshand.audacitytool import audacitytool
import argparse

def audacitypipe(prj_path, mat_path):
    audtl = audacitytool(prj_path, mat_path)
    audtl.importrecording()
    audtl.importmaterial()
    audtl.importhighlight()
    audtl.addmusic(default_music = "Middle_01.wav")
    #audtl.midedit()
    return

def main():
    description = 'Auddacity_tool controls Audacity via macro PIPE.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--prj_path', help = 'input folder for editing projects')
    parser.add_argument('-m', '--mat_path', help = 'the folder of editing materials')
    args = parser.parse_args()
    
    arg = {
        'prj_path': args.prj_path,
        'prj_path': args.prj_path,
        
        'mat_path': args.mat_path, 
    }
    audacitypipe(**arg)
    return

if __name__ == "__main__":
    main()