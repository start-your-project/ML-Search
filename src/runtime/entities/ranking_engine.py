from sklearn.feature_extraction.text import TfidfVectorizer
from .vectorizer import TfIdfModel
import Levenshtein
from collections.abc import Callable
import numpy as np
import copy

class RankingEngine:

    def __init__(
            self, prof_corpus: dict[str, str],
            vectorizer: TfIdfModel,
            sim_metric: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ):
        self.corpus = list(prof_corpus.values())
        self.professions = list(prof_corpus.keys())
        self.corpus_vec = vectorizer.vectorize(self.corpus)
        self.dist_func = sim_metric
        self.mask = np.ones(len(prof_corpus))
        self.mask[13] = 0
        self.mask[26] = 0
        self.n_prof = len(self.professions)

    def get_distance(self, vec: np.ndarray):
        simularity_dist = self.dist_func(vec, self.corpus_vec) * self.mask
        return simularity_dist[0]

    def text_match_evr(self, text_in: str, matr: np.ndarray):
        new_matr = copy.deepcopy(matr)
        if len(text_in) > 5:
            for i in range(self.n_prof):
                new_matr[i] += 1 / max(Levenshtein.distance(text_in, self.professions[i]), 1)
        return new_matr

    def get_result(self, sim_dist: np.ndarray):
        return self.professions[sim_dist.argmax()]

    def top_n(self, sim_dist: np.ndarray, n: int = 5):
        n = min(n, len(sim_dist))
        indexes = sim_dist.argsort()[-n::]
        result = [self.professions[idx] for idx in indexes[::-1]]
        return result

