def timestamp2arrayidx(timestamp, fs):
    timestamp_list = timestamp.split(':')
    hr = int(timestamp_list[0])
    min = int(timestamp_list[1])
    sec = int(timestamp_list[2])
    #print(f'hr: {hr}, min:{min}, sec:{sec}')
    sec_total = hr*60*60 + min*60 + sec
    return sec_total * fs

def wavcut(arrayidx_list_ip, wav_data):
    #print(wav_data.shape)
    arrayidx_list = [0]
    arrayidx_list.extend(arrayidx_list_ip)
    
    arrayidx_list = sorted(arrayidx_list)
    if arrayidx_list[-1] > wav_data.shape[1]:
        raise Exception("The largest time stamp cannot be larger than the maximum length of input audio file.") 
    
    # print(arrayidx_list)
    arrayidx_list.append(wav_data.shape[1])
    # print(arrayidx_list)
    
    wav_data_list = []
    
    for idx in range(len(arrayidx_list) - 1):
        start_idx = arrayidx_list[idx]
        end_idx = arrayidx_list[idx + 1]
        wav_data_list.append(wav_data[:, start_idx:end_idx])
    return wav_data_list