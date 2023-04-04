from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from pydub import effects
import numpy as np
import librosa
import json
import click
from fuzzywuzzy import fuzz, process
from catshand.utility import loggergen
from pydub.silence import detect_nonsilent

def convert_to_wav(args):
    
    ipdir = Path(args.input_dir)
    prjdir = Path(args.prj_dir)
    opdir = prjdir.joinpath(ipdir.name + '_wav')
    opdir.mkdir(exist_ok=True, parents=True)
    opdir_p = prjdir.joinpath(ipdir.name + '_wav_processed')
    
    logger = loggergen(prjdir.joinpath('log'))
    matchname = args.match_name
    compressor = args.compressor
    loudness = args.loudness

    logger.info(f'args: {args}')

    suffixes = ['.mp3', '.wav', '.m4a']
    ipfilelist = []
    for suffix in suffixes:
        ipfilelist.extend(sorted(Path(ipdir).glob(str(Path('**').joinpath(f'*{suffix}')))))
    logger.info(f'ipfilelist: {ipfilelist}')

    if matchname & (not prjdir is None):
        config_path = prjdir.joinpath('config', 'config.json')
        with open(config_path) as f:
            config = json.load(f)
        logger.info(f'load config.json: {config_path}')

        host_dict_path = Path(__file__).parents[1].joinpath('config','hosts_dict.json')
        with open(host_dict_path) as f:
            host_dict = json.load(f)
        logger.info(f'load hosts_dict.json: {host_dict_path}')

        ipfilelist_names = [x.name for x in ipfilelist]
        print(ipfilelist_names)

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
        
        opfilelist = [Path(opdir).joinpath(x).with_suffix('.wav') for x in opfilelist_names_new]
        opfilelist_p = [Path(opdir_p).joinpath(x).with_suffix('.wav') for x in opfilelist_names_new]

    elif matchname & (prjdir is None):
        raise ValueError('prj_dir is not specified, cannot match name')

    else:
        opfilelist = [Path(opdir).joinpath(x.relative_to(ipdir)).with_suffix('.wav') for x in ipfilelist]
        opfilelist_p = [Path(opdir_p).joinpath(x.relative_to(ipdir)).with_suffix('.wav') for x in ipfilelist]

    logger.info(f'opfilelist: {opfilelist}')

    from catshand.postproc import remove_silence, match_target_amplitude
    bitrate = 32000
    
    sound_p_dict = {}
    
    for ipfile, opfile, opfile_p in tqdm(zip(ipfilelist, opfilelist, opfilelist_p)):    
        sound = AudioSegment.from_file(ipfile)
        logger.info(f'Frame rate: {sound.frame_rate}')
        sound.export(opfile, format="wav", bitrate=bitrate)
        logger.info(f'Export .wav file with bitrate {bitrate}: {opfile}')

        if loudness or compressor: 
            opdir_p.mkdir(exist_ok=True, parents=True)
            sound_p = sound
            if loudness: 
                logger.info(f'Apply silence removal')
                # sound_p_short = sound_p[:5000000] + sound_p[-5000000:]
                sound_p_downsample = sound_p.set_frame_rate(600)
                sound_as_short_nosilence = remove_silence(sound_p_downsample, min_silence_len = 500, silence_thresh = -50, logger = logger)
                logger.info(f'Finish silence removal')

                logger.info(f'Apply loudness adjustment')
                target_db = -24.0
                sound_p = match_target_amplitude(sound_p, sound_as_short_nosilence, target_db)
                logger.info(f'Finish loudness adjustment')
            if compressor:
                logger.info(f'Apply compressor')
                '''
                logger.info(f'run pydub effects.compress_dynamic_range')
                target_db = -20.0
                ratio = 2.0
                attack = 5 
                release = 50
                sound_p = effects.compress_dynamic_range(sound_p, threshold = target_db, ratio = ratio, attack = attack, release = release)
                '''
                logger.info(f'run librosa.mu_compress')
   
                sound_p_array = np.array(sound_p.get_array_of_samples()).astype(np.float32)/32768
                sound_p_array = librosa.mu_compress(sound_p_array, mu=2, quantize=False)
                sound_p_array = sound_p_array*32768
                sound_p_array = sound_p_array.astype(np.int16)

                sound_p = AudioSegment(
                                sound_p_array.tobytes(), 
                                frame_rate=bitrate,
                                sample_width=sound_p_array.dtype.itemsize, 
                                channels=1)
                
                logger.info(f'Finish compressor')
            
            if loudness: 
                logger.info(f'Apply silence removal')
                sound_p_downsample = sound_p.set_frame_rate(100)
                sound_as_short_nosilence = remove_silence(sound_p_downsample, min_silence_len = 500, silence_thresh = -50, logger = logger)
                logger.info(f'Finish silence removal')

                logger.info(f'Apply loudness adjustment')
                target_db = -19.0
                sound_p = match_target_amplitude(sound_p, sound_as_short_nosilence, target_db)
                logger.info(f'Finish loudness adjustment')
            

            sound_p.export(opfile_p, format="wav", bitrate=bitrate)
            logger.info(f'Export processed .wav file with bitrate {bitrate}: {opfile_p}')
            
    return

def add_subparser(subparsers):
    description = "convert_to_wav convert all files in a folder to wav format."
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('convert_to_wav', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-i', '--input_dir', type = str, required = True, help = 'input folders with aufio files (.mp3, .wav, and .m4a).')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-m', '--match_name', action='store_true', help = 'fuzzy match filename with hosts and guests')
    optional_group.add_argument('-c', '--compressor', action='store_true', help = 'apply compressor')
    optional_group.add_argument('-l', '--loudness', action='store_true', help = 'apply loudness adjustment')
    subparsers.set_defaults(func=convert_to_wav)
    return