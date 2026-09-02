import math
import re
from typing import List

class LocalEmbeddingEngine:
    DIMENSION = 128

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        vec = [0.0] * cls.DIMENSION
        words = re.findall(r'\w+', text.lower())
        if not words:
            return vec

        for word in words:
            h = hash(word) % cls.DIMENSION
            weight = 1.0
            if any(char.isdigit() for char in word):
                weight = 2.5
            elif word in ["revenue", "ebitda", "pat", "profit", "debt", "cash", "margin", "growth", "fy24", "fy23", "fy22"]:
                weight = 3.0
            vec[h] += weight

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 4) for v in vec]

        return vec

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return round(dot_product / (norm_a * norm_b), 4)
