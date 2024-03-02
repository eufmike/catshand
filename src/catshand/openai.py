import logging
import multiprocessing as mp
import os
import pickle
import re
import sys
import time
from pathlib import Path

import openai
import opencc
import pandas as pd
import tiktoken
from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import detect_nonsilent, split_on_silence
from tqdm import tqdm

mp.set_start_method("fork", force=True)

# Replace with your OpenAI API key
# openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],  # this is also the default, it can be omitted
)

# Speech to text ==========================


def import_audio_file(file_path):

    file_extension = str(file_path).split(".")[-1].lower()
    if file_extension == "mp3":
        audio = AudioSegment.from_mp3(file_path)
    elif file_extension == "wav":
        audio = AudioSegment.from_wav(file_path)
    else:
        raise Exception("Unsupported audio format")
    return audio


def section_audio(idx, audio, sections_time, opsegdir, tmpdir, sections_length_digit):
    section = audio[sections_time[0] : sections_time[1]]
    section.export(
        opsegdir.joinpath(f"s_{idx:0{sections_length_digit}}.wav"), format="wav"
    )
    return (idx, section)


def separate_sentences(
    audio, opsegdir, tmpdir, min_silence_len=500, silence_thresh=-40, threads=1
):

    audio_lowbr = audio.set_frame_rate(8000)

    tmp_pkl = tmpdir.joinpath(opsegdir.name).with_suffix(".pkl")
    if not tmp_pkl.is_file():
        sections_times = detect_nonsilent(
            audio_lowbr, min_silence_len=min_silence_len, silence_thresh=silence_thresh
        )
        with open(tmp_pkl, "wb") as f:
            pickle.dump(sections_times, f)
        print("save pkl")
    else:
        with open(tmp_pkl, "rb") as f:
            sections_times = pickle.load(f)
        print("load pkl")

    print(len(sections_times))
    sections_length_digit = len(str(len(sections_times)))
    threads = 1  # Don't use multiprocessing. It is slower.

    if threads > 1:
        pbar = tqdm(total=len(sections_times))
        results = []

        def pbar_update(result):
            results.append(result)
            pbar.update(1)

        pool = mp.Pool(threads)
        # sections = []
        for idx, sections_time in enumerate(sections_times):
            pool.apply_async(
                section_audio,
                args=(
                    idx,
                    audio,
                    sections_time,
                    opsegdir,
                    tmpdir,
                    sections_length_digit,
                ),
                callback=pbar_update,
            )
            # sections.append(section)
        pool.close()
        pool.join()

        sections = {}
        for value in results:
            idx, section = value
            sections[idx] = section

    else:
        sections = {}
        for idx, sections_time in tqdm(enumerate(sections_times)):
            _, section = section_audio(
                idx, audio, sections_time, opsegdir, tmpdir, sections_length_digit
            )
            sections[idx] = section

    return sections, sections_times


def _speech_to_text(idx, audio_section, opsegdir):
    # Save the section as a temporary WAV file
    temp_file = Path(opsegdir, f"temp_section_{idx}.wav")
    audio_section.export(temp_file, format="wav")
    audio_section = audio_section.set_frame_rate(16000)
    # Load the WAV file and convert to base64
    with open(temp_file, "rb") as f:
        # Perform speech-to-text using the OpenAI API
        try:
            # initial_prompt = "Transcribe this audio to tranditional Chinese and English. pause fillers/filled pauses and particles should be in Chinese."
            # initial_prompt = "本音檔是一個討論生物醫學研究、在美生活、求學生涯以及心理健康的對話。將本音檔產生繁體中# 文的逐字稿，音檔中的贅詞、填詞和語助詞應該用繁體中文表示。只有關鍵詞、人名以及專有名詞用英文表示。逐字稿不應# 該包含英文、繁體中文以外的字。少於兩秒的音檔只產生繁體中文。Hmm替代為嗯。"
            prompt = "This audio discusses biomedical research, experience in living abroad, and mental health. Please cerate a transcript of this audio mainly in traditional Chinese, only transcribe names, professional terms in both Traditional Chinese and English. Particals and filled pauses should be transcribed in Traditional Chinese. For example, Hmm should be replaced by 嗯."
            # response = openai.Audio.transcribe("whisper-1", f, initial_prompt=initial_prompt)
            response = client.audio.transcriptions.create(
                model="whisper-1", file=f, prompt=prompt
            )
            text = response.text
            print(text)
            # transcripts.append(text)

        except Exception as e:
            print("Error:", str(e))
            text = ""
            # transcripts.append("")

    # remove the temporary WAV file
    temp_file.unlink()

    return idx, text


def speech_to_text(audio_sections, sections_times, opsegdir, threads=1):
    print(threads)
    request_time = [time.time()]
    if threads > 1:
        pbar = tqdm(total=len(sections_times))
        results = []

        def pbar_update(result):
            results.append(result)
            pbar.update(1)

        pool = mp.Pool(threads)
        # sections = []
        for idx, sections_time in enumerate(sections_times):
            audio_section = audio_sections[idx]
            if len(request_time) < 50:
                request_time.append(time.time())
                pool.apply_async(
                    _speech_to_text,
                    args=(idx, audio_section, opsegdir),
                    callback=pbar_update,
                )
            else:
                while (time.time() - request_time[0]) < 60:
                    time.sleep(1)
                request_time.append(time.time())
                pool.apply_async(
                    _speech_to_text,
                    args=(idx, audio_section, opsegdir),
                    callback=pbar_update,
                )
                # sections.append(section)
                request_time.pop(0)
        pool.close()
        pool.join()

        transcripts_dict = {}
        for value in results:
            idx, text = value
            transcripts_dict[idx] = text

    else:
        transcripts_dict = {}
        for idx, sections_time in tqdm(enumerate(sections_times)):
            audio_section = audio_sections[idx]
            if len(request_time) < 50:
                request_time.append(time.time())
                _, text = _speech_to_text(idx, audio_section, opsegdir)
            else:
                while (time.time() - request_time[0]) < 60:
                    time.sleep(1)
                request_time.append(time.time())
                _, text = _speech_to_text(idx, audio_section, opsegdir)
                transcripts_dict[idx] = text
                request_time.pop(0)

    transcripts = []

    for idx, sections_tim in tqdm(enumerate(sections_times)):
        transcripts.append(transcripts_dict[idx])

    return transcripts


def export_to_csv(times, transcripts, output_file="output.csv"):
    # df = pd.DataFrame(columns=['start_time', 'end_time', 'transcript'])
    df = []
    for i, (start, end) in tqdm(enumerate(times)):
        tmp = {"start_time": start, "end_time": end, "transcript": transcripts[i]}
        df_tmp = pd.DataFrame(tmp, index=[i])
        df.append(df_tmp)
    df = pd.concat(df, axis=0, ignore_index=True)
    df.to_csv(output_file, index=False)


def process_audio_file(
    file_path,
    output_file,
    opsegdir,
    tmpdir,
    min_silence_len=400,
    silence_thresh=-40,
    threads=1,
):
    tmpdir.mkdir(parents=True, exist_ok=True)
    audio = import_audio_file(file_path)
    sections, sections_times = separate_sentences(
        audio,
        opsegdir,
        tmpdir,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        threads=threads,
    )
    transcripts = speech_to_text(sections, sections_times, opsegdir, threads=threads)
    export_to_csv(sections_times, transcripts, output_file)


# ==========================


def merge_tran_csv(csvdir, docdir, tag=""):
    csvdir = Path(csvdir)
    docdir = Path(docdir)

    df = []
    for file in tqdm(csvdir.glob("*.csv")):
        name = re.findall(r"(.+?)\.csv", str(file.name))[0]
        tmp = pd.read_csv(file)
        tmp.dropna(inplace=True)
        tmp.insert(0, "name", name)
        df.append(tmp)

    df = pd.concat(df, axis=0, ignore_index=False)
    df.reset_index(drop=False, inplace=True)

    # Define a function to format the timedelta as "HH:MM:SS"
    def format_timedelta(t):
        return "{:02d}:{:02d}:{:02d}".format(
            t.components.hours, t.components.minutes, t.components.seconds
        )

    timeconvertcols = ["start_time", "end_time"]
    x = 1
    for timeconvertcol in timeconvertcols:
        df[f"{timeconvertcol}_tmp"] = pd.to_timedelta(df[timeconvertcol], unit="ms")

        # Apply the formatting function to the timedelta column
        df.insert(
            x,
            f"{timeconvertcol}_format",
            df[f"{timeconvertcol}_tmp"].apply(format_timedelta),
        )
        df.drop(columns=[f"{timeconvertcol}_tmp"], inplace=True)
        x += 1

    df["duration"] = df["end_time"] - df["start_time"]
    df = df[df["duration"] > 500]

    # convert simplified chinese to traditional chinese
    converter = opencc.OpenCC("s2tw.json")
    df["transcript"] = df["transcript"].apply(converter.convert)

    # export a csv file with all the details
    df.sort_values(by=["start_time"], inplace=True, ignore_index=True)
    df.to_csv(docdir.joinpath(f"merge_detail{tag}.csv"), index=False, encoding="utf-16")

    # export a csv file for csv display
    df.drop(columns=["index", "duration", "start_time", "end_time"], inplace=True)
    df.to_csv(docdir.joinpath(f"merge{tag}.csv"), index=False, encoding="utf-16")

    return


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


def convert_csv_to_txt(docdir, txtdir, chunck_size=80):
    docdir = Path(docdir)
    csv_path = docdir.joinpath("merge.csv")
    df = pd.read_csv(csv_path, encoding="utf-16")

    txt_all_path = docdir.joinpath("merge.txt")

    sentences = []
    for i, row in df.iterrows():
        sentences.append(
            row["name"]
            + ": "
            + "timestamp "
            + row["start_time_format"]
            + ": "
            + row["transcript"]
        )

    with open(txt_all_path, "w", encoding="utf-16") as f:
        for sentence in sentences:
            f.write(sentence)
            f.write("\n")
    """
    sentences_chunk = list(divide_chunks(sentences, chunck_size))
    print(len(sentences_chunk))
    chunk_digit = len(str(len(sentences_chunk)))
    for i, sentences in tqdm(enumerate(sentences_chunk)):
        txt_path = txtdir.joinpath(f'merge_openai_{str(i+1).zfill(chunk_digit)}.txt')
        with open(txt_path, 'w', encoding='utf-16') as f:
            for sentence in sentences:
                f.write(sentence)
                f.write('\n')
    """
    return


def break_up_file_to_chunks(
    filename=None, response_all="", chunk_size=2000, overlap=100
):

    if len(response_all) == 0:
        with open(filename, "r", encoding="utf-16") as f:
            text = f.read()
    else:
        text = response_all

    encoding = tiktoken.get_encoding("gpt2")
    tokens = encoding.encode(text)
    num_tokens = len(tokens)

    chunks = []
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i : i + chunk_size]
        chunks.append(chunk)

    return chunks


def _consolidate_summary(idx, chunk, names, max_tokens, name_timestamp):
    encoding = tiktoken.get_encoding("gpt2")
    # messages = [{"role": "system", "content": "This is text summarization."}]
    if not names is None:
        names_str = "、".join(names)
        addnames_prompt = f"參與者有以下幾位：{names_str}。"
    else:
        addnames_prompt = ""

    if name_timestamp:
        nametimerule_prompt = (
            f"並且將人名以及timestamp放在摘要句子的開頭 ，（順序依次為人名、timestamp、摘要），"
            + f"例如：{names[0]}: timestamp 00:00:00: 這是摘要內容。"
        )
    else:
        nametimerule_prompt = (
            f"摘要內容需指出誰說的話，並把timestamp放在句尾"
            + f"例如：{names[0]}說的摘要內容部分一（00:00:00）{names[1]}說的摘要內容部分一（00:10:10） 。"
        )

    messages = [
        {
            "role": "system",
            "content": "你是中文重點摘要的助手",
            "role": "user",
            "content": f"這是一個podcast錄音的逐字稿。"
            + addnames_prompt
            + f"請針對內容製作繁體中文的重點摘要，"
            + nametimerule_prompt
            + ":\n",
        }
    ]

    prompt_request = "以下為內容: " + encoding.decode(chunk)
    messages.append({"role": "user", "content": prompt_request})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    prompt_response = response["choices"][0]["message"]["content"].strip()
    return idx, prompt_response


def _mp_consolidate_summary(chunks, names, max_tokens, name_timestamp, threads):
    if threads > 1:
        pbar = tqdm(total=len(chunks))
        results = []

        def pbar_update(result):
            results.append(result)
            pbar.update(1)

        pool = mp.Pool(threads)
        # sections = []
        for idx, chunk in enumerate(chunks):
            pool.apply_async(
                _consolidate_summary,
                args=(idx, chunk, names, max_tokens, name_timestamp),
                callback=pbar_update,
            )
        pool.close()
        pool.join()

        prompt_response_dict = {}
        for value in results:
            idx, prompt_response = value
            prompt_response_dict[idx] = prompt_response

    else:
        prompt_response_dict = {}
        for idx, chunk in tqdm(enumerate(chunks)):
            _, prompt_response = _consolidate_summary(
                idx, chunk, names, max_tokens, name_timestamp
            )
            prompt_response_dict[idx] = prompt_response

    response = []
    for i in range(len(chunks)):
        response.append(prompt_response_dict[i])
    return response


def consolidate_summary(
    ippath,
    names,
    max_tokens,
    threads=1,
    oppath=None,
    name_timestamp=True,
    max_total_tokens=None,
):

    if max_total_tokens is None:
        chunks = break_up_file_to_chunks(ippath)
        print(f"The length of chunks: {len(chunks)}")
        response = _mp_consolidate_summary(
            chunks, names, max_tokens, name_timestamp, threads
        )
    else:
        x = 1
        num_tokens = max_total_tokens + 1
        response_all = ""
        while num_tokens > max_total_tokens:
            chunks = break_up_file_to_chunks(ippath, response_all)
            print(f"The length of chunks: {len(chunks)}")

            response = _mp_consolidate_summary(
                chunks, names, max_tokens, name_timestamp, threads
            )
            response_all = " ".join(response)
            encoding = tiktoken.get_encoding("gpt2")
            tokens = encoding.encode(response_all)
            num_tokens = len(tokens)
            print(f"round: {x}, num_tokens: {num_tokens}")
            x += 1

    if not oppath is None:
        with open(oppath, "w", encoding="utf-16") as f:
            for i, response in tqdm(enumerate(response)):
                # f.write(f'Summany {i+1}:\n')
                f.write(response)
                f.write("\n")
    return response


def openai_text(txtpath, summary_path, names=None, threads=1):

    consolidate_summary(
        ippath=txtpath,
        oppath=txtpath.parent.joinpath("tmp_summary_01.txt"),
        names=names,
        max_tokens=300,
        threads=threads,
    )
    summary = consolidate_summary(
        ippath=txtpath.parent.joinpath("tmp_summary_01.txt"),
        names=names,
        max_tokens=2000,
        max_total_tokens=4000,
        name_timestamp=False,
        threads=threads,
    )

    with open(summary_path, "w", encoding="utf-16") as f:
        for i, paragraph in tqdm(enumerate(summary)):
            f.write(paragraph)
            f.write("\n")

    return
