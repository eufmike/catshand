# Cat's Hand (catshand)

Cat's Hand is a toolbox designed for audio editing and production in the team of Tripod Cat's Podcast. Cat's Hand (catshand) is named after the Japanese idiom "猫の手も借りたい", which means "so busy someone wants to borrow even the paw of a cat."

## Installation

1. pull this git repository
2. move to the directory of catshand
3. create conda environment

    ```shell
    conda create -n catshand python=3.9
    ## catshand can be replaced by your-own-env-name
    ```

4. Change conda env 

    ```shell
    conda activate catshand
    ```

5. Install dependency
    
    for Mac User
    ```shell
    pip install -r ./requirement_core.txt
    ```
    for Windows User
    ```shell
    pip install -r ./requirement_win.txt
    ```

6. Install ffmpeg
    
    ```shell
    conda install -c conda-forge ffmpeg
    ```

7. Installation

    ```shell
    pip install -e .
    ```

8. Download test files from this [link](https://drive.google.com/drive/folders/1ZK2PGQHYUtQUZYW7GLx3O8Ukr5MvmnHe?usp=sharing)

## Function

### 1. *.wav divider

#### Demo

```shell
catshand prjpre -i <input_dir> -o <output_dir> -c ./src/catshand/tools/split_test.csv
```

By changing the *.csv file, users can define timestamps for spliting wav files in the input directory. The timestamp format is HH:MM:SS.

#### Notes

1. This code is designed for single channel signed 16-bit.

2. Exported rates can be different between files, while output rate will be the same as input rate.

### 2. Podcast Url Parser
# currently down

```bash
catshand linkparser
# return
Export:
Apple: https://tinyurl.com/2y3yp4xs
Google: https://tinyurl.com/2ynkqvl4
Spotify: https://tinyurl.com/29ms2asr
Kkbox: https://tinyurl.com/2aae45g3
```

### 3. Convert to Wav Format

#### Demo

1. Download test files [Link](https://drive.google.com/drive/folders/14T52ACyoYR1IxLtU7rNCz6J1y8pjzUCL?usp=sharing)

2. Transfer a folder to a temperary directory

3. Run the following command

    ```shell
    catshand prjpost -i <input_dir>
    ```

4. Options

- `-i`: define input dir

- `-e`: define output dir; default = None

- `-tfs`: target sampling rate; default = 32000

## Processing Steps

- Download finalized edited audio from Google Drive
- Rename all session to 01, 02, 03...
- Rename all fileanmes by hosts' and guests' name. Ensure the naming fashion is the same as config.json

- run prjpost on postedit wavs

    ```shell
    catshand prjpost -i C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_raw
    ```

- run wav files merger audmerger.py

    ```shell
    catshand audmerger -i 'C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_raw_export\' -o 'C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_merged\' -cfg C:\Users\michaelshih\Documents\Podcast_tmp\EP024\config\config.json
    ```

- Download hightlight from Google Drive, current only support wav
- Rename the filename to `highlight.wav`
- run postedit on the hightlight

    ```shell
    catshand prjpost -i C:\Users\michaelshih\Documents\Podcast_tmp\EP024\highlight -o C:\Users\michaelshih\Documents\Podcast_tmp\EP024\highlight_export --ext 'wav'
    ```

- run Audacity macro tool audacitypipe

    ```shell
    catshand audacitypipe -i C:\Users\michaelshih\Documents\Podcast_tmp\EP025 -m Z:\sc2.shih\Drive\Podcast\Edit\material
    ``` 