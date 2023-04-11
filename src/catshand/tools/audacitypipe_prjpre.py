import os, sys, re, datetime
from pathlib import Path 
import argparse
import click
import pandas as pd
from catshand.utility import loggergen 
from catshand.tools.prjsummary import prjsummary

def audacitypipe_prjpre(args): 
    
    from catshand.audacitytool import audacitytool

    prjdir = Path(args.prj_dir)
    ipdir = args.input_dir
    threads = args.threads

    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw_wav')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '_prjpre')

    tmp_dir = prjdir.joinpath('tmp_prjpre')

    audtl = audacitytool(prjdir, ipdir)
    audtl.importrecording(importall = True, add_offset = False, compressor = False)
    
    tmp_dir_wav = tmp_dir.joinpath('wav')
    tmp_dir_wav.mkdir(parents=True, exist_ok=True)
    if click.confirm('Please align audio files. Once finish, press Y', default=True):
        audtl.exportwav_seperate(tmp_dir_wav)

    parser = argparse.ArgumentParser()
    parser.add_argument('--prj_dir')
    parser.add_argument('--input_dir')
    parser.add_argument('--output_dir')
    parser.add_argument('--threads', type=int)

    tmp_dir_transcript = tmp_dir.joinpath('transcript')
    tmp_dir_transcript.mkdir(parents=True, exist_ok=True)
    
    args = parser.parse_args([
                    '--prj_dir', str(prjdir), 
                    '--input_dir', str(tmp_dir_wav), 
                    '--output_dir', str(tmp_dir_transcript),
                    '--threads', str(threads),
                    ])
    print(args)
    
    if click.confirm('Would you like to generate transcripts? ', default=True):
        prjsummary(args)

        df = pd.read_csv(tmp_dir_transcript.joinpath('doc', 'merge_detail.csv'), encoding='utf-16')
    
        sentences = []
        for i, row in df.iterrows():
            sentences.append(str(row['start_time']/1000) + '\t' + str(row['end_time']/1000) + '\t' + row['transcript'])
        
        txt_path = tmp_dir_transcript.joinpath('doc', 'aud_labels.txt')
        with open(txt_path, 'w', encoding='utf-16') as f:
            for sentence in sentences:
                f.write(sentence)
                f.write('\n')
        audtl.importlabel(txt_path)
    else: 
        if click.confirm('Would you like to open existing transcripts? ', default=True):
            txt_path = tmp_dir_transcript.joinpath('doc', 'aud_labels.txt')
            audtl.importlabel(txt_path)
    
    opdir.mkdir(parents=True, exist_ok=True)
    if click.confirm(f'Export wav files to {opdir}', default=True):
        audtl.exportwav_seperate(opdir, only_hostguest = True)

    return

def add_subparser(subparsers):
    description = 'audacitypipe_prjpre controls Audacity via macro PIPE.'
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('audacitypipe_prjpre', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', help = 'input folder for editing projects')
    # required_group.add_argument('-m', '--mat_path', help = 'the folder of editing materials')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with wav files.')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders for wav files.')
    optional_group.add_argument('-t', '--threads', dest='threads', type=int, default = 1)
    subparsers.set_defaults(func=audacitypipe_prjpre)
    
    return

# if __name__ == "__main__":
#     add_subparser()