# Tripod Cats' Little Helper (tclh)

1. pull this git repository

2. create conda env

    ```bash
    conda create -n tclh python=3.9
    ```

3. Installation

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4. Download test files from this [link](https://drive.google.com/drive/folders/1ZK2PGQHYUtQUZYW7GLx3O8Ukr5MvmnHe?usp=sharing)

5. Move to the directory of tclh

    ```bash
    python .\example\wavdivider.py -i <input_dir> -o <output_dir> -c .\example\split_test.csv
    ```
