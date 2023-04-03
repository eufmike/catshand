import argparse
import logging

def prjgen(args):
    print(args)
    
    
    return

def add_subparser(subparsers):
    description = "prjgen creates the project folder"
    subparsers = subparsers.add_parser('prjgen', help=description)
    subparsers.add_argument('-p', '--project_dir', help = 'directory for the project folder')
    subparsers.add_argument('-n', '--project_name', help = 'project name (example: EP028)')
    subparsers.set_defaults(func=prjgen)
    return