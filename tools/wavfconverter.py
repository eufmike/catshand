import os, sys, re, datetime
from pathlib import Path 
# from catshand.audacitytool import audacitytool
import numpy as np
import librosa
from scipy.io.wavfile import read, write
import argparse

def main(ip_path, op_path, target_fs):
    ip_path = Path(ip_path)
    if op_path is None: 
        op_path = ip_path.parent.joinpath(f'{ip_path.name}_export')
    else: 
        op_path = Path(op_path)
        
    ipfilelist = sorted(ip_path.glob(str(Path('**').joinpath('*.wav'))))
    opfilelist = [op_path.joinpath(x.relative_to(ip_path)) for x in ipfilelist]
    print(opfilelist)
    
    for ipfile, opfile in zip(ipfilelist, opfilelist):
        opfile.parent.mkdir(exist_ok=True, parents=True)
        
        fs, data = read(str(ipfile))
        if data.ndim == 2:
            data = data[:, 0]                

        if data.dtype == 'int32':
            #data = data.astype(np.float32, order='C') / 2147483647
            data = data / 2147483647 * 32768
            data = data.astype(np.int16, order='C') 
            
        if fs != target_fs:
            data = data.astype('float')
            data = librosa.resample(data, orig_sr = fs, target_sr = target_fs)
            data = data.astype(np.int16, order='C') 
        
        write(opfile, target_fs, data)
        
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert wav format')
    parser.add_argument('-i', '--input_path', help = 'input folder of wavs')
    parser.add_argument('-o', '--output_path', help = 'output folder of wavs')
    parser.add_argument('-tfs', '--target_fs', default = 32000, help = 'target output fs')
    args = parser.parse_args()
    
    arg = {
        'ip_path': args.input_path,
        'op_path': args.output_path, 
        'target_fs': args.target_fs,
    }
    main(**arg)