# Tripod Cats' Little Helper (tclh)

## Installation

1. pull this git repository
2. move to the directory of tclh
3. create conda environment

    ```bash
    conda create -n tclh python=3.9
    ```

4. Installation

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

5. Download test files from this [link](https://drive.google.com/drive/folders/1ZK2PGQHYUtQUZYW7GLx3O8Ukr5MvmnHe?usp=sharing)

6. run the example

    ```bash
    python .\example\wavdivider.py -i <input_dir> -o <output_dir> -c .\example\split_test.csv
    ```

By changing the *.csv file, users can define timestamps for spliting wav files in the input directory. The timestamp format is HH:MM:SS.

## Limitation

1. This code is designed for single channel signed 16-bit.

2. Exported rates can be different between files, while output rate will be the same as input rate. 