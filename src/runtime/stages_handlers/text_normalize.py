import re
import nltk
import pymorphy2
from dataclasses import dataclass


@dataclass()
class TextNormHandler:
    morph = pymorphy2.MorphAnalyzer()

    def lemmatize(self, text: str) -> str:
        words = text.split()
        res = list()
        for word in words:
            p = self.morph.parse(word)[0]
            res.append(p.normal_form)
        return " ".join(res)


    def prepare_text(self, text: str) -> list[str]:
        print(text)
        text = text.lower()
        # Удаление пунктуации
        text = re.sub("[^0-9A-Za-zа-яА-ЯЁё\+# ]", " ", text)
        # Stop words
        rus = nltk.corpus.stopwords.words('russian')
        eng = nltk.corpus.stopwords.words('english')
        text = " ".join([elem for elem in text.split() if elem not in rus and elem not in eng])
        print(f"after del stopwords :{text}")
        # Лемматизация
        text = self.lemmatize(text)
        print(f"after lemmatize :{text}")
        return text.split()