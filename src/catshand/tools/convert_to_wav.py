from tqdm import tqdm
from pathlib import Path
import numpy as np
import librosa
import json
import click
import multiprocessing as mp
mp.set_start_method('fork', force=True)
from fuzzywuzzy import fuzz, process
from catshand.utility import loggergen
from catshand.postproc import remove_silence, match_target_amplitude
from pydub import AudioSegment
from pydub import effects
from pydub.silence import detect_nonsilent, split_on_silence
import noisereduce as nr

def matchname_opfilelist(ipfilelist, prjdir, logger):
    config_path = prjdir.joinpath('config', 'config.json')
    with open(config_path) as f:
        config = json.load(f)
    logger.info(f'load config.json: {config_path}')

    host_dict_path = Path(__file__).parents[1].joinpath('config','hosts_dict.json')
    with open(host_dict_path) as f:
        host_dict = json.load(f)
    logger.info(f'load hosts_dict.json: {host_dict_path}')

    ipfilelist_names = [x.name for x in ipfilelist]

    hosts = config['hosts']
    guests = config['guests']
    name_dict = {}
    hostname_options = []
    for host in hosts:
        for name_option in host_dict[host]:
            name_dict[name_option] = host
            hostname_options.append(name_option)

    for guest in guests:
        name_dict[guest] = guest
    names = hostname_options + guests

    opfilelist_names_new = []
    for ipfilelist_name in ipfilelist_names:
        results = process.extract(ipfilelist_name, names, scorer=fuzz.token_sort_ratio)
        opfilelist_names_new.append(name_dict[results[0][0]])    

    return opfilelist_names_new

def _effects(ipfile, opfile, opfile_noeffect, bitrate, logger, loudness, compressor, noisereduce, finetune):
    sound = AudioSegment.from_file(ipfile)
    logger.info(f'Frame rate: {sound.frame_rate}')
    
    if finetune: 
        opfile_noeffect.parent.mkdir(exist_ok=True, parents=True)
        sound.export(opfile_noeffect, format="wav", bitrate=bitrate)

    logger.info(f'Export .wav file with bitrate {bitrate}: {opfile}')

    effects_check = loudness or compressor or noisereduce
    if effects_check: 
        sound_p = sound

        if loudness: 
            target_db = -40.0
            logger.info(f'Apply loudness adjustment: {target_db}')
            sound_p_downsample = sound_p.set_frame_rate(100)
            sound_as_short_nosilence = remove_silence(sound_p_downsample, min_silence_len = 500, silence_thresh = -50)
            sound_p = match_target_amplitude(sound_p, sound_as_short_nosilence, target_db)
            logger.info(f'Finish loudness adjustment')

        if compressor:
            logger.info(f'Apply compressor')
            
            logger.info(f'run pydub effects.compress_dynamic_range')
            target_db = -12.0
            ratio = 2.0
            attack = 0.2
            release = 1
            sound_p = effects.compress_dynamic_range(sound_p, threshold = target_db, ratio = ratio, attack = attack, release = release)
            
            '''
            logger.info(f'run librosa.mu_compress')
            sound_p_array = np.array(sound_p.get_array_of_samples())            
            print(sound_p_array.max(), sound_p_array.min())
            sound_p_array = sound_p_array.astype(np.float32)/32768
            print(sound_p_array.max(), sound_p_array.min())
            sound_p_array = librosa.mu_compress(sound_p_array, quantize=False)
            print(sound_p_array.max(), sound_p_array.min())
            print(sound_p_array.dtype)
            sound_p_array = sound_p_array*32768
            sound_p_array = sound_p_array.astype(np.int16)

            sound_p = AudioSegment(
                            sound_p_array.tobytes(), 
                            frame_rate=bitrate,
                            sample_width=sound_p_array.dtype.itemsize, 
                            channels=1)
            '''
            logger.info(f'Finish compressor')

        if noisereduce:
            logger.info(f'Apply noise reduction')
            sound_p_array = np.array(sound_p.get_array_of_samples()).astype(np.float32)/32768
            sound_p_array = nr.reduce_noise(y = sound_p_array, sr=bitrate, n_std_thresh_stationary=1.5,stationary=True)
            sound_p_array = sound_p_array*32768
            sound_p_array = sound_p_array.astype(np.int16)

            sound_p = AudioSegment(
                            sound_p_array.tobytes(), 
                            frame_rate=bitrate,
                            sample_width=sound_p_array.dtype.itemsize, 
                            channels=1)
            logger.info(f'Finish noise reduction')
        
        if loudness: 
            target_db = -20.0
            logger.info(f'Apply loudness adjustment: {target_db}')
            sound_p_downsample = sound_p.set_frame_rate(100)
            sound_as_short_nosilence = remove_silence(sound_p_downsample, min_silence_len = 500, silence_thresh = -50)
            sound_p = match_target_amplitude(sound_p, sound_as_short_nosilence, target_db)
            logger.info(f'Finish loudness adjustment')
        
        sound_p.export(opfile, format="wav", bitrate=bitrate)
        logger.info(f'Export processed .wav file with bitrate {bitrate}: {opfile}')
    return 

def convert_to_wav(args):
    # load arguments
    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '_wav')

    opdir.mkdir(exist_ok=True, parents=True)
    opdir_wavnoeffect = prjdir.joinpath(opdir.name + '_noeffect')

    bitrate = args.bitrate
    matchname = args.match_name
    compressor = args.compressor
    loudness = args.loudness
    noisereduce = args.noisereduce
    finetune = args.finetune
    threads = args.threads

    logger = loggergen(prjdir.joinpath('log'))
    logger.info(f'args: {args}')

    # create input file list
    suffixes = ['.mp3', '.wav', '.m4a']
    ipfilelist = []
    for suffix in suffixes:
        ipfilelist.extend(sorted(Path(ipdir).glob(str(Path('**').joinpath(f'*{suffix}')))))
    logger.info(f'ipfilelist: {ipfilelist}')

    # create output file list
    if matchname & (not prjdir is None):
        opfilelist_names_new = matchname_opfilelist(ipfilelist, prjdir, logger)
        opfilelist = [Path(opdir).joinpath(x).with_suffix('.wav') for x in opfilelist_names_new]
        opfilelist_noeffect = [Path(opdir_wavnoeffect).joinpath(x).with_suffix('.wav') for x in opfilelist_names_new]
    elif matchname & (prjdir is None):
        raise ValueError('prj_dir is not specified, cannot match name')
    else:
        opfilelist = [Path(opdir).joinpath(x.relative_to(ipdir)).with_suffix('.wav') for x in ipfilelist]
        opfilelist_noeffect = [Path(opdir_wavnoeffect).joinpath(x.relative_to(ipdir)).with_suffix('.wav') for x in ipfilelist]

    logger.info(f'opfilelist: {opfilelist}')    
    
    # multiple processing
    if threads > 1:
        pbar = tqdm(total=len(ipfilelist))
        results = []
        def pbar_update(result):
            results.append(result)
            pbar.update(1)
        
        pool = mp.Pool(threads)
        # sections = []
        for ipfile, opfile, opfile_noeffect in zip(ipfilelist, opfilelist, opfilelist_noeffect):
            pool.apply_async(_effects, args=(ipfile, opfile, opfile_noeffect, bitrate, logger, loudness, compressor, noisereduce, finetune), callback=pbar_update)
        pool.close()
        pool.join()

    else:
        prompt_response_dict = {}
        for ipfile, opfile, opfile_noeffect in tqdm(zip(ipfilelist, opfilelist, opfilelist_noeffect)):
            _effects(ipfile, opfile, opfile_noeffect, bitrate, logger, loudness, compressor, noisereduce, finetune)
            
    return

def add_subparser(subparsers):
    description = "convert_to_wav convert all files in a folder to wav format."
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('convert_to_wav', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    required_group.add_argument('--bitrate', default = 32000, help = 'bitrate of export wav')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with aufio files (.mp3, .wav, and .m4a).')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders different from default')
    optional_group.add_argument('-m', '--match_name', action='store_true', help = 'fuzzy match filename with hosts and guests')
    optional_group.add_argument('-c', '--compressor', action='store_true', help = 'apply compressor')
    optional_group.add_argument('-l', '--loudness', action='store_true', help = 'apply loudness adjustment')
    optional_group.add_argument('-r', '--noisereduce', action='store_true', help = 'apply noise reduction')
    optional_group.add_argument('--finetune', action='store_true', help = 'export wav before effects')
    optional_group.add_argument('-t', '--threads', dest='threads', type=int, default = 1)
    subparsers.set_defaults(func=convert_to_wav)
    return