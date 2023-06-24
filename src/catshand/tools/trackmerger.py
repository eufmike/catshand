from pathlib import Path
from catshand.utility import loggergen
import numpy as np
from pydub import AudioSegment

def volume_spatial(amount_audio, size = 3):
    adjust_volume = np.linspace(-1, 1, amount_audio)
    adjust_volume = adjust_volume * size
    return adjust_volume

def trackmerger(args):
    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw_wav_prjpre_wav_silrm')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath('merged')
    
    opdir.mkdir(exist_ok=True, parents=True)

    stereo = args.stereo
    spatial = args.spatial
    volumn_adj = args.volume_adjustment

    if not volumn_adj is None:
        if len(volumn_adj) == 1:
            volumn_adj_arr = list(int(volumn_adj[0]))*3
        elif len(volumn_adj) == 3:
            volumn_adj_arr = [int(x) for x in volumn_adj]
        else: 
            raise ValueError('volumn_adj should be either 1 or 3 values')
    else:
        volumn_adj_arr = None
    print(volumn_adj_arr)

    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')

    ipfilelist = sorted(Path(ipdir).glob(str(Path('**').joinpath(f'*.wav'))))
    logger.info(f'ipfilelist: {ipfilelist}')

    parent_ipdirs = list(set([x.parent for x in ipfilelist]))
    parent_ipdirs = sorted(parent_ipdirs)
    parent_oppaths = [opdir.joinpath(f'{x.name}_merged.wav') for x in parent_ipdirs]

    for parent_ipdir, parent_oppath in zip(parent_ipdirs, parent_oppaths):
        print(parent_ipdir)
        print(parent_oppath)
        child_ipfilelist = sorted(Path(parent_ipdir).glob(str(Path('**').joinpath(f'*.wav'))))
        print(child_ipfilelist)

        amount_audio = len(child_ipfilelist)
        left_adjust_volume = list(volume_spatial(amount_audio, size = 1))
        right_adjust_volume = list(-volume_spatial(amount_audio, size = 1))
        print(left_adjust_volume)
        print(right_adjust_volume)

        track = AudioSegment.from_wav(child_ipfilelist[0])
        audio_len = len(track)
        logger.info(f'audio_len: {audio_len}')
        track_all = AudioSegment.silent(duration=audio_len)

        if stereo:
            track_all = track_all.set_channels(2) 

        track_all_idv = []
        for idx, ipfile in enumerate(child_ipfilelist): 
            track_tmp = AudioSegment.from_wav(ipfile)
            if not volumn_adj is None:
                track_tmp = track_tmp + volumn_adj_arr[idx]
            if stereo:
                track_tmp = track_tmp.set_channels(2)
                if spatial:
                    print(left_adjust_volume[idx], right_adjust_volume[idx])
                    track_tmp = track_tmp.apply_gain_stereo(left_adjust_volume[idx], right_adjust_volume[idx])
                
                    
            track_all_idv.append(track_tmp)
            track_all = track_all.overlay(track_tmp)
            
        opfilename = 'track_all'
        if stereo:
            opfilename = opfilename + '_stereo'
            if spatial:
                opfilename = opfilename + '_spatial'
        track_all.export(parent_oppath, format="wav")
        
    # if spatial:
    #     for ipfile, track_idv in zip(ipfilelist, track_all_idv):
    #         opfilename = opdir.joinpath(ipfile.name)
    #         track_idv.export(opdir.joinpath(opfilename).with_suffix('.wav'), format="wav")
    
    return

def add_subparser(subparsers):
    description = "trackmerger convert all files in a folder to wav format."
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('trackmerger', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with audio files (.mp3, .wav, and .m4a).')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders different from default')
    optional_group.add_argument('-s', '--stereo', action='store_true', help = 'export a stereo file')
    optional_group.add_argument('-sp', '--spatial', action='store_true', help = 'applied spatial effect')
    optional_group.add_argument('-v', '--volume_adjustment', type = str, nargs = '+', help = 'applied volume percentage matrix')
    subparsers.set_defaults(func=trackmerger)
    return