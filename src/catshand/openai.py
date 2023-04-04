import os, sys, re
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import logging
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import openai
import opencc
import tiktoken

# Replace with your OpenAI API key
openai.api_key = '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'

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

def merge_tran_csv(csvdir, docdir, tag = ''):
    csvdir = Path(csvdir)
    docdir = Path(docdir)

    df = []
    for file in tqdm(csvdir.glob('*.csv')):
        name = re.findall(r'(.+?)\.csv', str(file.name))[0]
        tmp = pd.read_csv(file)
        tmp.dropna(inplace=True)
        tmp.insert(0, 'name', name)
        df.append(tmp)
    
    df = pd.concat(df, axis=0, ignore_index=False)
    df.reset_index(drop = False, inplace = True)

    # Define a function to format the timedelta as "HH:MM:SS"
    def format_timedelta(t):
        return '{:02d}:{:02d}:{:02d}'.format(t.components.hours, t.components.minutes, t.components.seconds)

    timeconvertcols = ['start_time', 'end_time']
    x = 1
    for timeconvertcol in timeconvertcols:
        df[f'{timeconvertcol}_tmp'] = pd.to_timedelta(df[timeconvertcol], unit='ms')
        
        # Apply the formatting function to the timedelta column
        df.insert(x, f'{timeconvertcol}_format', df[f'{timeconvertcol}_tmp'].apply(format_timedelta))
        df.drop(columns=[f'{timeconvertcol}_tmp'], inplace=True)
        x += 1

    df['duration'] = df['end_time'] - df['start_time']
    df = df[df['duration'] > 500]

    # convert simplified chinese to traditional chinese
    converter = opencc.OpenCC('s2tw.json')
    df['transcript'] = df['transcript'].apply(converter.convert)

    # export a csv file with all the details
    df.sort_values(by=['start_time'], inplace=True, ignore_index=True)
    df.to_csv(docdir.joinpath(f'merge_detail{tag}.csv'), index=False, encoding='utf-16')

    # export a csv file for csv display
    df.drop(columns=['index', 'duration', 'start_time', 'end_time'], inplace=True)
    df.to_csv(docdir.joinpath(f'merge{tag}.csv'), index=False, encoding='utf-16')

    return

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
 
def convert_csv_to_txt(docdir, txtdir, chunck_size = 80):
    docdir = Path(docdir)
    csv_path = docdir.joinpath('merge.csv')
    df = pd.read_csv(csv_path, encoding='utf-16')

    txt_all_path = docdir.joinpath('merge.txt')
    
    sentences = []
    for i, row in df.iterrows():
        sentences.append(row['name'] + ': ' + 'timestamp ' + row['start_time_format'] + ': ' + row['transcript'])
    
    with open(txt_all_path, 'w', encoding='utf-16') as f:
        for sentence in sentences:
            f.write(sentence)
            f.write('\n')
    '''
    sentences_chunk = list(divide_chunks(sentences, chunck_size))
    print(len(sentences_chunk))
    chunk_digit = len(str(len(sentences_chunk)))
    for i, sentences in tqdm(enumerate(sentences_chunk)):
        txt_path = txtdir.joinpath(f'merge_openai_{str(i+1).zfill(chunk_digit)}.txt')
        with open(txt_path, 'w', encoding='utf-16') as f:
            for sentence in sentences:
                f.write(sentence)
                f.write('\n')
    '''
    return

def break_up_file_to_chunks(filename, chunk_size=2000, overlap=100):

    encoding = tiktoken.get_encoding("gpt2")
    with open(filename, 'r', encoding='utf-16') as f:
        text = f.read()

    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    
    chunks = []
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

def consolidate_summary(txtpath, oppath, names, max_tokens):
    prompt_response = []

    chunks = break_up_file_to_chunks(txtpath)
    
    encoding = tiktoken.get_encoding("gpt2")
    chunks = break_up_file_to_chunks(txtpath)

    print(f"The length of chunks: {len(chunks)}")

    for i, chunk in tqdm(enumerate(chunks)):
        # messages = [{"role": "system", "content": "This is text summarization."}]
        if names is None: 
            messages = [{"role": "user", "content": f"這是一個podcast錄音的逐字稿。請針對內容製作繁體中文的重點摘要，並且將timestamp放在摘要句子的開頭:\n"}]
        else: 
            names_str = "、".join(names)
            messages = [{"role": "user", "content": f"這是一個podcast錄音的逐字稿。參與者有以下幾位：{names_str}請針對內容製作繁體中文的重點摘要，並且將人名以及timestamp放在摘要句子的開頭 （順序依次為人名、timestamp、摘要）:\n"}]

        prompt_request = "以下為內容: " + encoding.decode(chunk)
        messages.append({"role": "user", "content": prompt_request})

        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=.5,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        )
        
        prompt_response.append(response["choices"][0]["message"]['content'].strip())

    with open(oppath, "w", encoding='utf-16') as f:
        for i, response in tqdm(enumerate(prompt_response)):
            # f.write(f'Summany {i+1}:\n')
            f.write(response)
            f.write('\n')

    print(f"The length of chunks: {len(chunks)}")
    return 

def openai_text(txtpath, summary_path, names = None):

    consolidate_summary(txtpath, txtpath.parent.joinpath('tmp_summary_01.txt'), names = names, max_tokens = 300)
    consolidate_summary(txtpath.parent.joinpath('tmp_summary_01.txt'), txtpath.parent.joinpath('tmp_summary_02.txt'), names = names, max_tokens = 400)

    '''
    print(txtpath.parent.joinpath('tmp_summary_02.txt'))
    with open(txtpath.parent.joinpath('tmp_summary_02.txt'), 'r', encoding='utf-16') as f:
        prompt_response = f.read()
    
    prompt_request = f"濃縮以下的重點摘要並輸出繁體中文的內容： {prompt_response}"
    print(prompt_request)
    
    messages = [{"role": "user", "content": prompt_request}]
    # messages.append({"role": "user", "content": prompt_request})

    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=.5,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    )
    # meeting_summary = response["choices"][0]["text"].strip()
    meeting_summary = response["choices"][0]["message"]['content'].strip()
    print(meeting_summary)
    with open(summary_path, "w", encoding='utf-16') as f:
        f.write(meeting_summary)
    '''
    return