from .vectorizer import TfIdfModel
from collections.abc import Callable
import numpy as np

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
        self.n_prof = len(self.professions)

        self.ban_list = np.array([])
        if (self.ban_list):
            self.mask[self.ban_list] = 0

    def get_distance(self, vec: np.ndarray):
        simularity_dist = self.dist_func(vec, self.corpus_vec)
        return simularity_dist[0]

    def apply_ban_list(self, dist: np.ndarray):
        return dist * self.mask

    def get_result(self, sim_dist: np.ndarray):
        return self.professions[sim_dist.argmax()], sim_dist.max()

    def top_n(self, sim_dist: np.ndarray, n: int = 5):
        n = min(n, len(sim_dist))
        indexes = sim_dist.argsort()[-n::]
        result = [self.professions[idx] for idx in indexes[::-1]]
        return result

