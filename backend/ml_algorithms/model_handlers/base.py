import joblib
import io
from abc import ABC, abstractmethod


class BaseMLModel(ABC):
    """Базовый класс для всех моделей."""

    def __init__(self, **kwargs):
        self.model = None

    @abstractmethod
    def train(self, X, y):
        """Обучает модель."""
        pass

    @abstractmethod
    def predict(self, X):
        """Делает предсказания."""
        pass

    def save(self, path: str|None = None):
        """Сохраняет модель на диск."""
        if path is not None:
            joblib.dump(self.model, path)
        buffer = io.BytesIO()
        joblib.dump(self.model, buffer)
        buffer.seek(0)
        return buffer

    @classmethod
    def load(cls, model_bytes):
        """Фабричный метод: создаёт объект и подгружает модель."""
        instance = cls.__new__(cls)
        instance.model = joblib.load(model_bytes)
        return instance