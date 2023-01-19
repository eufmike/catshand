import os, sys, re, datetime
from tqdm.auto import tqdm
from pathlib import Path 
# from catshand.audacitytool import audacitytool
import numpy as np
import argparse
import librosa
from scipy.io.wavfile import read, write
from pydub import AudioSegment
import soundfile

def main(ip_path, op_path, ext, target_fs):
    ip_path = Path(ip_path)
    if op_path is None: 
        op_path = ip_path.parent.joinpath(f'{ip_path.name}_export')
    else: 
        op_path = Path(op_path)
    
    op_path.mkdir(exist_ok = True)
    
    ipfilelist = sorted(ip_path.glob(str(Path('**').joinpath(f'*.{ext}'))))
    print(f'ipfilelist: {ipfilelist}')
    opfilelist = [op_path.joinpath(x.relative_to(ip_path)).with_suffix('.wav') for x in ipfilelist]
    print(f'opfilelist: {opfilelist}')
    
    for ipfile, opfile in tqdm(zip(ipfilelist, opfilelist)):
        
        if ext == 'wav': 
            opfile.parent.mkdir(exist_ok=True, parents=True)            
            fs, data = read(str(ipfile))

        elif ext == 'mp3':
            print(str(ipfile))
            audio = AudioSegment.from_mp3(ipfile)
            fs = audio.frame_rate
            data = np.array(audio.get_array_of_samples())
            
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