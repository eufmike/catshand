from pathlib import Path
import argparse
from catshand.utility import loggergen, configgen
from catshand.postproc import postproc
 
def audmerger(args):
    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('03_Editing_02_wav')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '_merged')

    opdir.mkdir(exist_ok=True, parents=True)
    prjconfig_path = prjdir.joinpath('config', 'config.json')
    loudness = args.loudness
    threads = args.threads
    
    if not prjconfig_path.is_file():
        configgen(prjconfig_path.parents[1])
    
    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')
    
    logger.info('Merge wav files...')
    postproc_obj = postproc(prjconfig_path) 
    postproc_obj.filedict_gen(ipdir, opdir)
    postproc_obj.createmetadata()
    postproc_obj.wav2mergemono(target_fs = 32000, loudness = loudness, threads = threads)
    logger.info('Done merging...')

    return

def add_subparser(subparsers):
    description = "audmerger merges audio files"
    subparsers = subparsers.add_parser('audmerger', help=description)
    required_group = subparsers.add_argument_group('Required Arguments') 
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with wav files to be merged.')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders for merged wav files.')
    optional_group.add_argument('-l', '--loudness', action='store_true', help = 'apply loudness adjustment')
    optional_group.add_argument('-t', '--threads', dest='threads', type=int, default = 1)
    # subparsers.add_argument('-cfg', '--prjconfig_path', help = 'the project config')
    subparsers.set_defaults(func=audmerger)
    return

# if __name__ == "__main__":
#     main()