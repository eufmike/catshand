from pathlib import Path
from catshand.utility import timestamp2arrayidx, loggergen, timestampgen
from pydub import AudioSegment

def audiosplit(args):
    print(args)

    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw_wav_prjpre_wav_silrm')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '_splitted')
    opdir.mkdir(exist_ok = True, parents = True)

    filetype = args.input_format

    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')

    ipfllist = sorted(ipdir.glob(f'*{filetype}'))
    print(ipfllist)
    
    timestamps = ['00:00:00']
    if args.timestamps is None:
        timestamps.extend(timestampgen())
    else:
        timestamps.extend(args.timestamps)
        logger.info(f'Timestamps: {timestamps}')
    
    logger.info('Start spliting files...')
    
    for ipflpath in ipfllist:
        logger.info(f'input file: {ipflpath}')
        timepoint_ms = [timestamp2arrayidx(x) for x in timestamps]
        sound = AudioSegment.from_file(ipflpath)
        timepoint_ms.extend([len(sound)])
        for idx, time in enumerate(timestamps):
            oppath_tmp = opdir.joinpath(f'session_{str(idx + 1).zfill(2)}', ipflpath.name)
            oppath_tmp.parent.mkdir(exist_ok = True, parents = True)
            sound_tmp = sound[timepoint_ms[idx]:timepoint_ms[idx+1]]
            sound_tmp.export(oppath_tmp, format = 'wav')
    
    logger.info('Done')
    
    return

def add_subparser(subparsers):
    description = "audiosplit creates the project profile and prepare preprocessing materials."
    subparsers = subparsers.add_parser('audiosplit', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', type = str, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with *.wav files.')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders for divided *.wav files.')
    optional_group.add_argument('-ts', '--timestamps', nargs = '+', type = str, help = 'timestamps for splitting the audio files.')
    optional_group.add_argument('-if', '--input_format', type = str, default = '.wav', help = 'input file format')
    subparsers.set_defaults(func=audiosplit)
    return

# if __name__ == "__main__":
#     add_subparser()