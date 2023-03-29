import json
import pickle
from dataclasses import dataclass
from marshmallow_dataclass import class_schema
import yaml

@dataclass()
class DataPaths:
    all_words_path: str
    alphabet_path: str
    professions_corpus_path: str
    translations_path: str
    vectorizer_path: str

DataPathsSchema = class_schema(DataPaths)

def read_data_paths_params(path: str) -> DataPaths:
    with open(path, "r") as file:
        schema = DataPathsSchema()
        return schema.load(yaml.safe_load(file))

def load_json(name):
    with open(name, 'r') as file:
        return json.load(file)

def load_pickle(name):
    with open(name, 'rb') as file:
        return pickle.load(file)