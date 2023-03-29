from dataclasses import dataclass
from src.runtime.stages_handlers import TranslitHandler, CorrectionHandler, TextNormHandler
from src.runtime.entities import TfIdfModel, RankingEngine

@dataclass()
class SearchEngine:
    text_norm_h : TextNormHandler
    translit_h : TranslitHandler
    corrections_h: CorrectionHandler
    vectorizer: TfIdfModel
    ranking_engine: RankingEngine

    def search(self, text_in: str) -> str:
        # Нормализация
        text = self.text_norm_h.prepare_text(text_in)
        # Обработка русского транслита
        text = self.translit_h.add_translit(text)
        # Обработка опечаток
        text = self.corrections_h.apply(text)
        # Векторизация TF-IDF
        vec = self.vectorizer.vectorize([" ".join(text)])
        # Ранжирование
        dist_matr = self.ranking_engine.get_closest(vec)
        # Евристики
        matr = self.ranking_engine.text_match_evr(text_in, dist_matr)
        # Выбираем топ 1 профессию
        result = self.ranking_engine.get_result(matr)

        return result

