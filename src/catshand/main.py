import argparse
from catshand.tools import prjpre, prjpost, audacitypipe, highlight, audmerger, linkparser

def main():
    parser = argparse.ArgumentParser(description='Main parser')
    subparsers = parser.add_subparsers(help='Subparsers help')

    prjpre.add_subparser(subparsers)
    prjpost.add_subparser(subparsers)
    audacitypipe.add_subparser(subparsers)
    audmerger.add_subparser(subparsers)
    highlight.add_subparser(subparsers)
    linkparser.add_subparser(subparsers)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()





