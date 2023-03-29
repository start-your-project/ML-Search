from sklearn.metrics.pairwise import cosine_similarity
from .search_engine import SearchEngine, TfIdfModel
import numpy as np
from src.data import (
    read_data_paths_params,
    load_json,
    load_pickle
)
from src.runtime.stages_handlers import (
    TextNormHandler,
    CorrectionHandler,
    TranslitHandler
)
from src.runtime.entities import RankingEngine


CONFIG_PATH = "configs/search_config.yaml"

def get_search_engine(data_paths):
    text_norm_handler = TextNormHandler()
    all_words = load_json(data_paths.all_words_path)["all_words"]
    correction_handler = CorrectionHandler(np.array(all_words))
    alphabet = load_json(data_paths.alphabet_path)
    translit_handler = TranslitHandler(alphabet)
    prof_corpus = load_json(data_paths.professions_corpus_path)
    vectorizer = TfIdfModel(load_pickle(data_paths.vectorizer_path))
    ranking_engine = RankingEngine(prof_corpus, vectorizer, cosine_similarity)

    return SearchEngine(text_norm_handler, translit_handler, correction_handler, vectorizer, ranking_engine)


if __name__ == '__main__':
    data_paths = read_data_paths_params(CONFIG_PATH)

    search_engine = get_search_engine(data_paths)

    while True:
        text = input()
        print(search_engine.search(text))
