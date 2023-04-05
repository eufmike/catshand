import argparse
from catshand.tools import audio2wav, prjgen, prjpre, prjpost, audacitypipe, highlight, audmerger, linkparser, prjsummary, mt_removesilent, cleanvoice

def main():
    description = "Cat's Hand (catshand) is a toolbox designed for audio editing and production in the team of Tripod Cat's Podcast. Cat's Hand (catshand) is named after the Japanese idiom \"猫の手も借りたい\", which means \"so busy someone wants to borrow even the paw of a cat.\""
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='Subparsers help')

    prjgen.add_subparser(subparsers)
    audio2wav.add_subparser(subparsers)
    mt_removesilent.add_subparser(subparsers)
    prjsummary.add_subparser(subparsers)
    cleanvoice.add_subparser(subparsers)
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





