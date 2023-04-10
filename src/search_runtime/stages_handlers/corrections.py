import numpy as np
import Levenshtein
from dataclasses import dataclass
from typing import Union
dist_lev_vec = np.vectorize(Levenshtein.distance)

@dataclass()
class CorrectionHandler:
    all_words: np.ndarray[str]
    max_d: int = 3

    def get_closest(self, word: str) -> Union[str, None]:
        top_n = 20
        dist_all = dist_lev_vec(word, self.all_words)
        dist = dist_all.min()
        if dist > self.max_d or dist > len(word) // 2:
            return None

        index = dist_all.argmin()
        closest_index = np.argsort(dist_all)[:top_n]
        top_words = self.all_words[closest_index]
        top_dists = dist_all[closest_index]

        if len(word) > 4:  # Учитываем если слово полностью входит в другое
            for i, elem in enumerate(top_words):
                if word in elem:
                    top_dists[i] /= 2
        index_top = top_dists.argmin()
        return top_words[index_top]

    def apply(self, txt: list[str]) -> list[str]:
        new_txt = []
        for elem in txt:
            if elem in self.all_words:
                new_txt.append(elem)
            else:
                closest = self.get_closest(elem)
                if closest:
                    new_txt.append(closest)
        return new_txt