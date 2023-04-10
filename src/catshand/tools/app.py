import os, sys, re, datetime
from pathlib import Path 
import argparse
from catshand.utility import loggergen 
from catshand.dash import app

def dashapp(args):
    myapp = app
    myapp.run_server(debug=False)
    
    return


def add_subparser(subparsers):
    description = 'app.py run Dash App to control Catshand.'
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('app', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_path', help = 'input folder for editing projects')
    # required_group.add_argument('-m', '--mat_path', help = 'the folder of editing materials')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with wav files.')
    subparsers.set_defaults(func=dashapp)
    
    return