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
from catshand.openai import merge_tran_csv

# Replace with your OpenAI API key
openai.api_key = "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"

def import_audio_file(file_path):

    file_extension = str(file_path).split('.')[-1].lower()
    if file_extension == 'mp3':
        audio = AudioSegment.from_mp3(file_path)
    elif file_extension == 'wav':
        audio = AudioSegment.from_wav(file_path)
    else:
        raise Exception('Unsupported audio format')
    return audio

def separate_sentences(audio, min_silence_len=500, silence_thresh=-40):
    sections_times = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    sections = []
    for sections_time in tqdm(sections_times):
        section = audio[sections_time[0]:sections_time[1]]
        sections.append(section)

    print(len(sections))
    return sections, sections_times
    
def speech_to_text(audio_sections, opsegdir):
    transcripts = []

    sections_length = len(audio_sections)
    sections_length_digit = len(str(sections_length))

    for i, section in tqdm(enumerate(audio_sections)):
        # Save the section as a temporary WAV file
        temp_file = Path('./temp_section.wav')
        section.export(temp_file, format='wav')
        section.export(opsegdir.joinpath(f's_{i:0{sections_length_digit}}.wav'), format='wav')
        # Load the WAV file and convert to base64
        with open(temp_file, 'rb') as f:
            # Perform speech-to-text using the OpenAI API
            try:
                #initial_prompt = "Transcribe this audio to tranditional Chinese and English. pause fillers/filled pauses and particles should be in Chinese."
                # initial_prompt = "本音檔是一個討論生物醫學研究、在美生活、求學生涯以及心理健康的對話。將本音檔產生繁體中# 文的逐字稿，音檔中的贅詞、填詞和語助詞應該用繁體中文表示。只有關鍵詞、人名以及專有名詞用英文表示。逐字稿不應# 該包含英文、繁體中文以外的字。少於兩秒的音檔只產生繁體中文。Hmm替代為嗯。"
                initial_prompt = "This audio discusses biomedical research, experience in living abroad, and mental health. Please cerate a transcript of this audio mainly in traditional Chinese, only transcribe names, professional terms in both Traditional Chinese and English. Particals and filled pauses should be transcribed in Traditional Chinsese. For example, Hmm should be replaced by 嗯."
                response = openai.Audio.transcribe("whisper-1", f, initial_prompt=initial_prompt)
                text = response['text']
                print(text)
                transcripts.append(text)

            except Exception as e:
                print("Error:", str(e))
                transcripts.append("")
        
        # remove the temporary WAV file
        temp_file.unlink()

    return transcripts

def export_to_csv(times, transcripts, output_file='output.csv'):
    # df = pd.DataFrame(columns=['start_time', 'end_time', 'transcript'])
    df = []
    for i, (start, end) in tqdm(enumerate(times)):
        tmp = {'start_time': start, 'end_time': end, 'transcript': transcripts[i]}
        df_tmp = pd.DataFrame(tmp, index=[i])
        df.append(df_tmp)
    df = pd.concat(df, axis=0, ignore_index=True)
    df.to_csv(output_file, index=False)

def process_audio_file(file_path, output_file, opsegdir, min_silence_len=400, silence_thresh=-40):
    audio = import_audio_file(file_path)
    sections, times = separate_sentences(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    transcripts = speech_to_text(sections, opsegdir)
    export_to_csv(times, transcripts, output_file)

def prjsummary(args):
    ipdir = Path(args.input_dir)
    prjdir = Path(args.prj_dir)
    logger = loggergen(prjdir.joinpath('log'))
    
    opdir = prjdir.joinpath('transcription')
    csvdir = opdir.joinpath('csv')
    segdir = opdir.joinpath('wav')
    docdir = opdir.joinpath('doc')
    Path(opdir).mkdir(exist_ok=True, parents=True)

    for ipfile in tqdm(ipdir.glob('*.wav')):
        opfile = csvdir.joinpath(ipfile.relative_to(ipdir)).with_suffix('.csv')
        opsegdir = segdir.joinpath(ipfile.stem)
        opsegdir.mkdir(exist_ok=True, parents=True)
        logger.info(f'Processing Transcribe, save csv to : {opfile}')
        logger.info(f'Processing Transcribe, save wav files to : {opsegdir}')
        # process_audio_file(ipfile, opfile, opsegdir)

    logger.info(f'merge csv files to: {docdir}')
    docdir.mkdir(exist_ok=True, parents=True)
    merge_tran_csv(csvdir, docdir)
    
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