from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

@dataclass()
class TfIdfModel:
    vectorizer: TfidfVectorizer

    def vectorize(self, txt: list[str]) -> np.ndarray:
        return self.vectorizer.transform(txt)