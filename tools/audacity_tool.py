import os, sys, re, datetime
from pathlib import Path 
from catshand.audacitytool import audacitytool
import argparse

def main(prj_path):
    audtl = audacitytool(prj_path)
    
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run audacity named-pipe tool')
    parser.add_argument('-i', '--prj_path', help = 'input folders for editing projects')
    args = parser.parse_args()
    
    arg = {
        'prj_path': args.prj_path,
    }
    main(**arg)