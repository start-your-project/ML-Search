from dataclasses import dataclass
from typing import Union

import numpy as np

from src.search_runtime.stages_handlers import TranslitHandler, CorrectionHandler, TextNormHandler
from src.search_runtime.entities import TfIdfModel, RankingEngine

@dataclass()
class SearchEngine:
    text_norm_h : TextNormHandler
    translit_h : TranslitHandler
    corrections_h: CorrectionHandler
    vectorizer: TfIdfModel
    ranking_engine: RankingEngine

    def get_distance(self, text_in: str) -> Union[np.ndarray, None]:
        # Нормализация
        text = self.text_norm_h.prepare_text(text_in)
        # Обработка русского транслита
        text = self.translit_h.add_translit(text)
        # Обработка опечаток
        text = self.corrections_h.apply(text)
        if not text:
            return None
        # Векторизация TF-IDF
        vec = self.vectorizer.vectorize([" ".join(text)])
        # Ранжирование
        sim_dist = self.ranking_engine.get_distance(vec)
        # Евристики
        sim_dist = self.ranking_engine.text_match_evr(text_in, sim_dist)
        return sim_dist

    def search(self, text_in: str) -> str:
        sim_dist = self.get_distance(text_in)
        if sim_dist is None:
            return "NAN"
        # Выбираем топ 1 профессию
        result = self.ranking_engine.get_result(sim_dist)
        return result

    def recommend(self, text_in: str, n) -> list[str]:
        sim_dist = self.get_distance(text_in)
        if sim_dist is None:
            return []
        result = self.ranking_engine.top_n(sim_dist, n)
        return result




