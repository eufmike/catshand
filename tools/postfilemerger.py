import os, re, sys
import pandas as pd
from pathlib import Path
import catshand
import json
import argparse
import numpy as np
from catshand.utility import timestamp2arrayidx, wavcut, loggergen
from catshand.postproc import postproc
from scipy.io.wavfile import read, write

 
def main(ip_path, op_path, csv_path, prjconfig_path):
    
    ip_path = Path(ip_path)
    op_path = Path(op_path)
    #csv_path = Path(csv_path)
    prjconfig_path = Path(prjconfig_path)
    
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='divide wav files with given time stamp')
    parser.add_argument('-i', '--input_dir', help = 'input folders with *.wav files.')
    parser.add_argument('-o', '--output_dir', help = 'output folders for divided *.wav files.')
    parser.add_argument('-c', '--csv', help = 'csv files with time stamps')
    parser.add_argument('-cfg', '--prjconfig_path', help = 'the project config')
    args = parser.parse_args()
    
    arg = { 
        'ip_path': args.input_dir,
        'op_path': args.output_dir,
        'csv_path': args.csv,
        'prjconfig_path': args.prjconfig_path,
    }
    
    main(**arg)