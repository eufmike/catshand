from pathlib import Path
import argparse
from catshand.utility import loggergen, configgen
from catshand.postproc import postproc
 
def audmerger(args):
    ip_path = args.input_dir
    op_path = args.output_dir
    prjconfig_path = args.prjconfig_path

    ip_path = Path(ip_path)
    op_path = Path(op_path)
    prjconfig_path = Path(prjconfig_path)
    
    if not prjconfig_path.is_file():
        configgen(prjconfig_path.parents[1])
    
    op_path.mkdir(exist_ok = True)
    
    logfld = ip_path.parent.joinpath('log')
    logfld.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logfld)
    
    logger.info('Merge wav files...')
    postproc_obj = postproc(prjconfig_path) 
    postproc_obj.filedict_gen(ip_path, op_path)
    postproc_obj.createmetadata()
    postproc_obj.wav2mergemono()
    logger.info('Done merging...')

    return

def add_subparser(subparsers):
    description = "audmerger merges audio files"
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('audmerger', help=description)
    subparsers.add_argument('-i', '--input_dir', help = 'input folders with *.wav files.')
    subparsers.add_argument('-o', '--output_dir', help = 'output folders for divided *.wav files.')
    subparsers.add_argument('-cfg', '--prjconfig_path', help = 'the project config')
    subparsers.set_defaults(func=audmerger)
    return

# if __name__ == "__main__":
#     main()