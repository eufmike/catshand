import os
import requests
from pathlib import Path
from catshand.utility import loggergen

cleanvoice_api_key = os.environ["CLEANVOICE_API_KEY"]


def cleanvoice(args):
    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw_short')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '00_Raw_short_cv')

    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')

    # create input file list
    ipfilelist = sorted(Path(ipdir).glob(str(Path('**').joinpath(f'*.wav'))))
    logger.info(f'ipfilelist: {ipfilelist}')
    for ipfile in ipfilelist:
        url = f'https://api.cleanvoice.ai/v1/upload?filename={ipfile.name}'
        headers = {'X-API-Key': cleanvoice_api_key}
        response = requests.post(url, headers=headers)
        signed_url = response.json()['signedUrl']
        print(signed_url)
        
        break
    return
def add_subparser(subparsers):
    description = "'cleanvoice' upload and download file to Cleanvoice (https://cleanvoice.ai)."
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('cleanvoice', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with aufio files (.mp3, .wav, and .m4a).')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders different from default')
    subparsers.set_defaults(func=cleanvoice)