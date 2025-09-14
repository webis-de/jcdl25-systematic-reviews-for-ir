import os
import glob
import json
from papermage import Document
from pybtex.database.input import bibtex
from tqdm import tqdm

NON_IMPORTANT_FILES = ['log.txt', 'dblp_bibtex_cache.txt', 'config.json']


def load_txt_file(file):
    """
    Returns the contents of a txt-file.

    Args:
        file: Path to the txt-file to load.

    Returns:
        String with the contents of the txt-file.
    """
    with open(file, encoding="utf8") as f:
        contents = f.readlines()
    contents = ''.join(str(x) for x in contents)
    return contents

def load_bib_file(file):
    """
    Returns the contents of a bib-file.

    Args:
        file: Path to the bib-file to load.

    Returns:
        The contents of the bib-file as a BibliographyData object.
    """
    parser = bibtex.Parser()
    bib_data = parser.parse_file(file)
    return bib_data

def load_json_file(file):
    """
    Returns the contents of a json-file created with papermage.

    Args:
        file: Path to the json-file to load.

    Returns:
        Papermage document with the contents of the json-file.
    """
    with open(file, encoding="utf8") as f:
        try:
            doc_dict = json.load(f)
            doc = Document.from_json(doc_dict)
        except:
            return None
    return doc

def get_all_txt_files(ir_anthology_data_path):
    """
    Returns the contents of all txt-files.

    Args:
        ir_anthology_data_path: Path to the files.

    Returns:
        Dict with filename -> file-content.
    """
    path = ir_anthology_data_path
    print("Collecting txt files...")
    conf_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/conf/**/*.txt', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    jrnl_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/jrnl/**/*.txt', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    files = conf_files + jrnl_files
    files = {file: load_txt_file(file) for file in tqdm(files, desc="Loading txt-files...")}
    return files

def get_all_bib_files(ir_anthology_data_path):
    """
    Returns the contents of all bib-files.

    Args:
        ir_anthology_data_path: Path to the files.

    Returns:
        Dict with filename -> bib-content.
    """
    path = ir_anthology_data_path
    print("Collecting bib files...")
    conf_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/conf/**/*.bib', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    jrnl_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/jrnl/**/*.bib', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    files = conf_files + jrnl_files
    files = {file: load_bib_file(file) for file in tqdm(files, desc="Loading bib-files...")}
    return files

def get_all_json_files(ir_anthology_data_path):
    """
    Returns the contents of all json-files.

    Args:
        ir_anthology_data_path: Path to the files.

    Returns:
        Dict with filename -> json-content.
    """
    path = ir_anthology_data_path
    print("Collecting json files...")
    conf_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/conf/**/*.json', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    jrnl_files = [file.replace("\\", "/") for file in glob.glob(f'{path}/jrnl/**/*.json', recursive = True) if not (os.path.basename(file) in NON_IMPORTANT_FILES)]
    files = conf_files + jrnl_files
    files = {file: load_json_file(file) for file in tqdm(files, desc="Loading json-files...")}
    return files

def get_all_files(data_path):
    """
    Returns a dict with the merged bib- and txt-files content.

    Returns:
        Dict with bib_id -> Dict with data from bib-file (bib-data) and data from txt-file (full-text).
    """
    bibs = get_all_bib_files(data_path)
    txts = get_all_txt_files(data_path)
    #jsons = get_all_json_files(data_path)

    files = {}

    for file in tqdm(bibs, desc="Process bibs..."):
        txt_files = {k.split("/")[-1][:-4]: v for k, v in txts.items() if file.split("/")[:-1] == k.split("/")[:-1]}
        #json_files = {k.split("/")[-1][:-4]: v for k, v in jsons.items() if file.split("/")[:-1] == k.split("/")[:-1]}
        for i in tqdm(range(len(bibs[file].entries)), desc="Process entries in this bib..."):
            entry = list(bibs[file].entries)[i]
            bib_data = bibs[file].entries[entry]
            bib_id = bib_data.key
            if bib_id in txt_files:
                json_file = load_json_file("/".join(file.split("/")[:-1]) + "/" + bib_id + ".json")
            else:
                json_file = None
            files[bib_id] = {
                "bib-data": bib_data,
                "full-text": txt_files[bib_id] if bib_id in txt_files else "",
                "json-data": {
                    "abstract": "".join([e.text for e in json_file.get_layer("abstracts").entities])
                } if json_file else ""
            }
    
    return files
