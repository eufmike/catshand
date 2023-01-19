import os, sys, re, datetime
from pathlib import Path 
# from catshand.audacitytool import audacitytool
import numpy as np
import argparse
import librosa
from scipy.io.wavfile import read, write
from catshand.postproc import highlightproc
from pydub import AudioSegment

def main(ip_path, op_path, ext, target_fs):
    ip_path = Path(ip_path)
    if op_path is None: 
        op_path = ip_path.parent.joinpath(f'{ip_path.name}_export')
    else: 
        op_path = Path(op_path)
        
    print(f'ipfilelist: {ip_path}')
    print(f'opfilelist: {op_path}')
    
    if ext == 'wav': 
        op_path.parent.mkdir(exist_ok=True, parents=True)
        highlightproc(ip_path, op_path, target_fs = 32000)
                
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert wav format')
    parser.add_argument('-i', '--input_path', help = 'input folder for audio files')
    parser.add_argument('-o', '--output_path', help = 'output folder of wavs')
    parser.add_argument('-e', '--ext', default='wav', help = 'extension of audio files')
    parser.add_argument('-tfs', '--target_fs', default = 32000, help = 'target output fs')
    args = parser.parse_args()
    
    arg = {
        'ip_path': args.input_path,
        'op_path': args.output_path,
        'ext': args.ext,
        'target_fs': args.target_fs,
    }
    main(**arg)