import os, re
import pandas as pd
from pathlib import Path
import catshand
import argparse
import numpy as np
from catshand.utility import timestamp2arrayidx, wavcut
from scipy.io.wavfile import read, write

def main(ip_path, op_path, csv_path,
         filetype = '.wav'):
    print(f'ip_path: {ip_path}') 
    print(f'op_path: {op_path}')
    print(f'csv_path: {csv_path}')
    
    ip_path = Path(ip_path)
    op_path = Path(op_path)
    csv_path = Path(csv_path)
    
    ipfllist = sorted(ip_path.glob(f'*{filetype}'))
    df_split = pd.read_csv(csv_path)
    
    op_path.mkdir(exist_ok = True, parents = True)
    for idx in range(len(df_split)+1):
        tmp_opfld = op_path.joinpath(f'session_{str(idx+1).zfill(2)}')
        tmp_opfld.mkdir(exist_ok = True)
    
    print('Start spliting files...')
    for ipflpath in ipfllist:
        print(f'input file: {ipflpath}')
        fs_tmp, data_tmp = read(str(ipflpath))
        data_tmp = np.expand_dims(data_tmp, axis = 0)
        timestamp = df_split['timestamp']
        # print(timestamp)
        arrayidx = [timestamp2arrayidx(x, fs_tmp) for x in timestamp]
        # print(arrayidx)
        splitdata_list = wavcut(arrayidx, data_tmp)
        for idx, splitdata_tmp in enumerate(splitdata_list):
            opfilename = re.sub(filetype, f'_{str(idx + 1).zfill(2)}{filetype}', ipflpath.name)
            oppath_tmp =  op_path.joinpath(f'session_{str(idx + 1).zfill(2)}', opfilename)
            write(filename = oppath_tmp, 
                  data = splitdata_tmp.T, rate = fs_tmp)
    print('Done')         
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='divide wav files with given time stamp')
    parser.add_argument('-i', '--input_dir', help = 'input folders with *.wav files.')
    parser.add_argument('-o', '--output_dir', help = 'output folders for divided *.wav files.')
    parser.add_argument('-c', '--csv', help = 'csv files with time stamps')
    args = parser.parse_args()
    
    arg = {
        'ip_path': args.input_dir,
        'op_path': args.output_dir,
        'csv_path': args.csv,
    }
    
    main(**arg)