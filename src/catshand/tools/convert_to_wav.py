from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
import json
import click
from fuzzywuzzy import fuzz, process
from catshand.utility import loggergen

def convert_to_wav(args):
    
    ipdir = Path(args.input_dir)
    prjdir = Path(args.prj_dir)
    opdir = prjdir.joinpath(ipdir.name + '_wav')
    opdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(prjdir.joinpath('log'))
    matchname = args.match_name
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

    elif matchname & (prjdir is None):
        raise ValueError('prj_dir is not specified, cannot match name')

    else:
        opfilelist = [Path(opdir).joinpath(x.relative_to(ipdir)).with_suffix('.wav') for x in ipfilelist]

    logger.info(f'opfilelist: {opfilelist}')

    bitrate = "32k"
    for ipfile, opfile in tqdm(zip(ipfilelist, opfilelist)):    
        sound = AudioSegment.from_file(ipfile)
        sound.export(opfile, format="wav", bitrate=bitrate)
        logger.info(f'Export .wav file with bitrate {bitrate}: {opfile}')
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
    subparsers.set_defaults(func=convert_to_wav)
    return