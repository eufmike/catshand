import os, re
import pandas as pd
from pathlib import Path
import catshand
import argparse
import numpy as np
from catshand.utility import timestamp2arrayidx, wavcut, loggergen, configgen
from scipy.io.wavfile import read, write

def prjpre(args):
    print(args)
    logger = loggergen(prj_dir.joinpath('log'))

    ip_path = args.input_dir
    op_path = args.output_dir
    csv_path = args.csv
    filetype = '.wav'
    
    ip_path = Path(ip_path)
    op_path = Path(op_path)
    csv_path = Path(csv_path)
    
    ipfllist = sorted(ip_path.glob(f'*{filetype}'))
    df_split = pd.read_csv(csv_path)
    
    op_path.mkdir(exist_ok = True, parents = True)
    for idx in range(len(df_split)+1):
        tmp_opfld = op_path.joinpath(f'session_{str(idx+1).zfill(2)}')
        tmp_opfld.mkdir(exist_ok = True)
    
    logger.info('Start spliting files...')

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

def add_subparser(subparsers):
    description = "prjpreprocess creates the project profile and prepare preprocessing materials."
    # parser = argparse.ArgumentParser(description=description)
    subparsers = subparsers.add_parser('prjpre', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-i', '--input_dir', help = 'input folders with *.wav files.')
    required_group.add_argument('-o', '--output_dir', help = 'output folders for divided *.wav files.')
    required_group.add_argument('-c', '--csv', help = 'csv files with time stamps')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-p', '--prj_dir', type = str, help = 'directory for the project folder')
    subparsers.set_defaults(func=prjpre)
    return

# if __name__ == "__main__":
#     add_subparser()