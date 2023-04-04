import os
from pathlib import Path
from tqdm import tqdm
import base64
import requests
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import pandas as pd
import openai
from catshand.utility import loggergen
from catshand.openai import process_audio_file, merge_tran_csv, convert_csv_to_txt, openai_text

def prjsummary(args):
    ipdir = Path(args.input_dir)
    prjdir = Path(args.prj_dir)
    logger = loggergen(prjdir.joinpath('log'))
    
    opdir = prjdir.joinpath('transcription')
    csvdir = opdir.joinpath('csv')
    segdir = opdir.joinpath('wav')
    docdir = opdir.joinpath('doc')
    txtdir = opdir.joinpath('txt')
    Path(opdir).mkdir(exist_ok=True, parents=True)

    names = []
    for ipfile in tqdm(ipdir.glob('*.wav')):
        opfile = csvdir.joinpath(ipfile.relative_to(ipdir)).with_suffix('.csv')
        names.append(ipfile.stem)
        opsegdir = segdir.joinpath(ipfile.stem)
        opsegdir.mkdir(exist_ok=True, parents=True)
        logger.info(f'Processing Transcribe, save csv to : {opfile}')
        logger.info(f'Processing Transcribe, save wav files to : {opsegdir}')
        process_audio_file(ipfile, opfile, opsegdir)
    print(names)
    logger.info(f'merge csv files to: {docdir}')
    docdir.mkdir(exist_ok=True, parents=True)
    txtdir.mkdir(exist_ok=True, parents=True)
    merge_tran_csv(csvdir, docdir)
    convert_csv_to_txt(docdir, txtdir)
    openai_text(docdir.joinpath('merge.txt'), docdir.joinpath('summary.txt'), names = names)

    return

def add_subparser(subparsers):
    description = "prjsummary creates the prejoct summary with transcript and time stamps"
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('prjsummary', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-i', '--input_dir', type = str, required = True, help = 'input folders with *.wav files.')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    subparsers.set_defaults(func=prjsummary)
    return