import re
from dataclasses import dataclass
from typing import Dict

def is_eng(word: str) -> str:
    return re.fullmatch("[a-zA-Z]+", word)

def is_rus(word: str) -> str:
    return re.fullmatch("[а-яА-ЯЁё]+", word)

@dataclass()
class TranslitHandler:
    alphabet: Dict[str, str]

    def translit_word(self, word: str) -> str:
        new_word = ""
        for ch in word:
            new_word += self.alphabet[ch]
        return new_word

    def add_translit(self, txt: list[str]) -> list[str]:
        new_text = []
        n = len(txt)
        for i in range(n):
            word = txt[i]
            new_text.append(word)
            if is_rus(word):
                new_text.append(self.translit_word(word))
        return new_text