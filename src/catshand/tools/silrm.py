
from tqdm import tqdm
from pathlib import Path
from pydub import AudioSegment
from pydub import effects
import numpy as np
import librosa
import json
import click
import pickle
import multiprocessing as mp
mp.set_start_method('fork', force=True)
from fuzzywuzzy import fuzz, process
from catshand.utility import loggergen
from pydub.silence import detect_nonsilent
import matplotlib.pyplot as plt

def find_transition_indices(arr, side_of_edge = 'left'):
    if side_of_edge == 'left':
        return np.where ((arr[1:] - arr[:-1])==1)[0]
    elif side_of_edge == 'right':
        return np.where ((arr[1:] - arr[:-1])==-1)[0]

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

def segment2array(ipfilelist, maxlength, nonsilence_dict, buffer = 10):
        array_nosilence = np.zeros((len(ipfilelist), maxlength))
        for i, ipfile in enumerate(ipfilelist):
            sections_times = nonsilence_dict[ipfile]
            for start, end in sections_times:
                start_with_buffer = start - buffer
                end_with_buffer = end + buffer
                if start_with_buffer < 0: start_with_buffer = 0
                if end_with_buffer > maxlength: end_with_buffer = maxlength
                array_nosilence[i, start_with_buffer:end_with_buffer] = 1

        array_nosilence = np.max(array_nosilence, axis=0)
        return array_nosilence
 
def _detect_no_silence(ipfile, value, min_silence_len, silence_thresh, logger):
    ipaudio = value['audio']
    logger.info(f'Start detecting non-silence segments in{ipfile}')
    ipaudio_lowbr = ipaudio.set_frame_rate(16000)
    sections_times = detect_nonsilent(ipaudio_lowbr, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    
    logger.info(f'Finish detecting non-silence segments in{ipfile}')
    return ipfile, sections_times

def detect_no_silence(ipaudio_dict, min_silence_len, silence_thresh, threads, logger):

    # multiple processing
    if threads > 1:
        pbar = tqdm(total=len(ipaudio_dict.keys()))
        results = []
        def pbar_update(result):
            results.append(result)
            pbar.update(1)
        
        pool = mp.Pool(threads)
        # sections = []
        for ipfile, value in ipaudio_dict.items():
            pool.apply_async(_detect_no_silence, args=(ipfile, value, min_silence_len, silence_thresh, logger), callback=pbar_update)
        pool.close()
        pool.join()

        nonsilence_dict = {}
        for value in results:
            ipfile, sections_times = value
            nonsilence_dict[ipfile] = sections_times

    else:
        nonsilence_dict = {}
        for ipfile, value in tqdm(ipaudio_dict.items()):
            ipfile, sections_times = _detect_no_silence(ipfile, value, min_silence_len, silence_thresh, logger)
            nonsilence_dict[ipfile] = sections_times
        
    return nonsilence_dict

def _remove_silence(ipfile, ipaudio_dict, value, list_nosilence, random_silence, bitrate, logger):
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

def remove_silence(ipaudio_dict, list_nosilence, random_silence, bitrate, threads, logger):
    # multiple processing
    if threads > 1:
        pbar = tqdm(total=len(ipaudio_dict.keys()))
        results = []
        def pbar_update(result):
            results.append(result)
            pbar.update(1)
        
        pool = mp.Pool(threads)
        # sections = []
        for ipfile, value in ipaudio_dict.items():
            pool.apply_async(_remove_silence, args=(ipfile, ipaudio_dict, value, list_nosilence, random_silence, bitrate, logger), callback=pbar_update)
        pool.close()
        pool.join()

    else:
        for ipfile, value in tqdm(ipaudio_dict.items()):
            _remove_silence(ipfile, ipaudio_dict, value, list_nosilence, random_silence, bitrate, logger)
        
    return

def silrm(args):

    prjdir = Path(args.prj_dir)
    if not args.input_dir is None:
        ipdir = Path(args.input_dir)
    else:
        ipdir = prjdir.joinpath('00_Raw_wav_prjpre_wav')

    if not args.output_dir is None:
        opdir = Path(args.output_dir)
    else:
        opdir = prjdir.joinpath(ipdir.name + '_silrm')
    opdir.mkdir(exist_ok=True, parents=True)

    logdir = prjdir.joinpath('log')
    logdir.mkdir(exist_ok=True, parents=True)
    logger = loggergen(logdir)
    logger.info(f'args: {args}')
    
    pad_zero = args.pad_zero
    threads = args.threads
    
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

    min_silence_len=700
    silence_thresh=-60

    tmpdir = prjdir.joinpath('tmp')
    tmp_pkl = tmpdir.joinpath('nonsilence_dict.pkl')
    if not tmp_pkl.is_file():
        
        nonsilence_dict = detect_no_silence(ipaudio_dict, min_silence_len, silence_thresh, threads, logger)    
        tmpdir.mkdir(exist_ok=True, parents=True)
        with open(tmp_pkl, 'wb') as f:
            pickle.dump(nonsilence_dict, f)
        logger.info(f'Save non-silence segments to pkl file: {tmp_pkl}')
    else:
        with open(tmp_pkl, 'rb') as f:
            nonsilence_dict = pickle.load(f)
        logger.info(f'Load non-silence segments from previous processed pkl file: {tmp_pkl}')

    array_nosilence = segment2array(ipfilelist, maxlength, nonsilence_dict, buffer = 10)
    array_silence = 1 - array_nosilence

    # print(array_silence)
    list_nosilence = array2segment(array_nosilence)
    list_silence = array2segment(array_silence)
    
    list_silence_len = [x[1]-x[0] for x in list_silence]
    # plt.hist(list_silence_len, bins=100)
    # plt.show()

    # print(np.mean(list_silence_len))
    random_silence = np.random.randint(10, 200, size=len(list_nosilence)-1)
    remove_silence(ipaudio_dict, list_nosilence, random_silence, bitrate, threads, logger)

    return

def add_subparser(subparsers):
    description = "silrm removes silence in the audio files"
    subparsers = subparsers.add_parser('silrm', help=description)
    required_group = subparsers.add_argument_group('Required Arguments')
    required_group.add_argument('-p', '--prj_dir', type = str, required = True, help = 'directory for the project folder')
    optional_group = subparsers.add_argument_group('Optional Arguments')
    optional_group.add_argument('-i', '--input_dir', type = str, help = 'input folders with *.wav files.')
    optional_group.add_argument('-o', '--output_dir', type = str, help = 'output folders different from default')
    optional_group.add_argument('-pz', '--pad_zero', action='store_true', help = 'pad zero to the end of audio')
    optional_group.add_argument('-t', '--threads', dest='threads', type=int, default = 1)
    subparsers.set_defaults(func=silrm)
    return