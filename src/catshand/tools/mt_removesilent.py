
from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from pydub import effects
import numpy as np
import librosa
import json
import click
import pickle
from fuzzywuzzy import fuzz, process
from catshand.utility import loggergen
from pydub.silence import detect_nonsilent
import matplotlib.pyplot as plt

def find_transition_indices(arr, side_of_edge = 'left'):
    if side_of_edge == 'left':
        return np.where ((arr[1:] - arr[:-1])==1)[0]
    elif side_of_edge == 'right':
        return np.where ((arr[1:] - arr[:-1])==-1)[0]

def mt_removesilent(args):
    ipdir = Path(args.input_dir)
    prjdir = Path(args.prj_dir)
    opdir = prjdir.joinpath(ipdir.name + '_sil_removal')
    opdir.mkdir(exist_ok=True, parents=True)
    
    logger = loggergen(prjdir.joinpath('log'))
    pad_zero = args.pad_zero
    
    ipfilelist = sorted(Path(ipdir).glob(str(Path('**').joinpath(f'*.wav'))))
    opfilelist = [opdir.joinpath(x.relative_to(ipdir)) for x in ipfilelist]
    
    bitrate = 32000

    ipaudio_dict = {}
    maxlength = 0
    for ipfile, opfile in zip(ipfilelist, opfilelist):
        ipaudio = AudioSegment.from_wav(ipfile)
        ipaudio_dict[ipfile] = {}
        ipaudio_dict[ipfile]['audio'] = ipaudio
        ipaudio_dict[ipfile]['length'] = len(ipaudio)
        ipaudio_dict[ipfile]['opfile'] = opfile

        if len(ipaudio) > maxlength:
            maxlength = len(ipaudio)

    for ipfile, value in ipaudio_dict.items():
        ipaudio = value['audio']
        if pad_zero:
            silence = AudioSegment.silent(duration=maxlength-len(ipaudio))
            ipaudio_padded = ipaudio + silence
            ipaudio_dict[ipfile]['audio'] = ipaudio_padded
        ipaudio_dict[ipfile]['new_length'] = len(ipaudio_padded)

    min_silence_len=500
    silence_thresh=-40

    tmpdir = prjdir.joinpath('tmp')
    tmp_pkl = tmpdir.joinpath('nonsilence_dict.pkl')
    if not tmp_pkl.is_file():
        nonsilence_dict = {}
        for ipfile, value in tqdm(ipaudio_dict.items()):
            ipaudio = value['audio']
            logger.info(f'Start detecting non-silence segments in{ipfile}')
            sections_times = detect_nonsilent(ipaudio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
            nonsilence_dict[ipfile] = sections_times
            logger.info(f'Finish detecting non-silence segments in{ipfile}')
        
        tmpdir.mkdir(exist_ok=True, parents=True)
        
        with open(tmp_pkl, 'wb') as f:
            pickle.dump(nonsilence_dict, f)
        logger.info(f'Save non-silence segments to pkl file: {tmp_pkl}')
    else:
        with open(tmp_pkl, 'rb') as f:
            nonsilence_dict = pickle.load(f)
        logger.info(f'Load non-silence segments from previous processed pkl file: {tmp_pkl}')

    # print(nonsilence_dict)
    array_nosilence = np.zeros((len(ipfilelist), maxlength))
    for i, ipfile in enumerate(ipfilelist):
        sections_times = nonsilence_dict[ipfile]
        for start, end in sections_times:
            array_nosilence[i, start:end] = 1
    array_nosilence = np.max(array_nosilence, axis=0)
    # print(array_nosilence)
    
    array_silence = 1 - array_nosilence
    # print(array_silence)
    list_nosilence = array2segment(array_nosilence)
    list_silence = array2segment(array_silence)
    # print(list_silence[:10])
    # print(list_nosilence)
    # print(len(list_nosilence))
    
    list_silence_len = [x[1]-x[0] for x in list_silence]
    # plt.hist(list_silence_len, bins=100)
    # plt.show()

    # print(np.mean(list_silence_len))
    random_silence = np.random.randint(10, 400, size=len(list_nosilence)-1)
    
    for ipfile, value in ipaudio_dict.items():
        logger.info(f'processing {ipfile}')
        ipaudio = value['audio']
        sections = []
        for i, sections_time in tqdm(enumerate(list_nosilence)):
            section = ipaudio[sections_time[0]:sections_time[1]]
            sections.append(section)
            if i < len(list_nosilence)-1:
                silence = AudioSegment.silent(duration=random_silence[i])
                sections.append(silence)
            
        all = sum(sections)
        opfile = ipaudio_dict[ipfile]['opfile']
        logger.info(f'saving {opfile}')
        all.export(opfile, format='wav', bitrate=bitrate)
    return

def array2segment(array):
    start_indices = find_transition_indices(array, side_of_edge = 'left')
    end_indices = find_transition_indices(array, side_of_edge = 'right')

    if start_indices[0] > end_indices[0]:
        start_indices = np.concatenate(([0], start_indices))

    if len(start_indices) != len(end_indices):
        min_len = min(len(start_indices), len(end_indices))
        start_indices = start_indices[:min_len]
        end_indices = end_indices[:min_len]

    list_op = []
    for start, end in zip(start_indices, end_indices):
        list_op.append([start, end])

    return list_op

def add_subparser(subparsers):
    description = "mt_removesilent removes silence in the audio files"
    subparsers = subparsers.add_parser('mt_removesilent', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-i', '--input_dir', type = str, required = True, help = 'input folders with *.wav files.')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-pz', '--pad_zero', action='store_true', help = 'pad zero to the end of audio')
    subparsers.set_defaults(func=mt_removesilent)
    return