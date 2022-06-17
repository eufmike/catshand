# Cat's Hand (catshand)

Cat's Hand is a toolbox designed for audio editing and production in the team of Tripod Cat's Podcast. Cat's Hand (catshand) is named after the Japanese idiom "猫の手も借りたい", which means "so busy someone wants to borrow even the paw of a cat."

## Installation

1. pull this git repository
2. move to the directory of catshand
3. create conda environment

    ```bash
    conda create -n catshand python=3.9
    ```

4. Installation

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

5. Download test files from this [link](https://drive.google.com/drive/folders/1ZK2PGQHYUtQUZYW7GLx3O8Ukr5MvmnHe?usp=sharing)

## Function


### 1. *.wav divider

```bash
python .\tools\wavdivider.py -i <input_dir> -o <output_dir> -c .\tools\split_test.csv
```

By changing the *.csv file, users can define timestamps for spliting wav files in the input directory. The timestamp format is HH:MM:SS.

## Notes

1. This code is designed for single channel signed 16-bit.

2. Exported rates can be different between files, while output rate will be the same as input rate. 

### 2. Podcast Url Parser

```bash
python .\tools\linkparser.py
# return
Export:
Apple: https://tinyurl.com/2y3yp4xs
Google: https://tinyurl.com/2ynkqvl4
Spotify: https://tinyurl.com/29ms2asr
Kkbox: https://tinyurl.com/2aae45g3
```