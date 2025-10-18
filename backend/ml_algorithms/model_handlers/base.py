import joblib
import io
from abc import ABC, abstractmethod
import pandas as pd


class BaseMLModel(ABC):
    """Базовый класс для всех ML-моделей."""

    feature_columns: list[str] = []
    model = None

    def __init__(self, df: pd.DataFrame, target_column: str, **kwargs):
        pass


    @abstractmethod
    def train(self, df: pd.DataFrame, target_column: str):
        """Обучает модель на данных."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: pd.DataFrame):
        """Делает предсказания."""
        raise NotImplementedError

    @abstractmethod
    def _feature_analyzer(self, df: pd.DataFrame):
        """Отбрасывает бесполезные фичи"""
        raise NotImplementedError


    def select_features(self, df: pd.DataFrame):
        """Отбирает нужные фичи и проверяет, что все они есть."""
        if not self.feature_columns:
            raise ValueError("feature_columns не заданы в подклассе модели.")
        missing = [f for f in self.feature_columns if f not in df.columns]
        if missing:
            raise KeyError(f"В данных отсутствуют нужные фичи: {missing}")
        df, selected_columns = self._feature_analyzer(df)
        self.feature_columns = selected_columns
        return df[self.feature_columns]


    def save(self, path: str | None = None):
        """Сохраняет модель в файл или возвращает байтовый буфер."""
        if self.model is None:
            raise ValueError("Невозможно сохранить: модель не обучена или не загружена.")
        buffer = io.BytesIO()
        joblib.dump(self.model, buffer)
        buffer.seek(0)
        if path:
            with open(path, "wb") as f:
                f.write(buffer.getvalue())
        return buffer

    @classmethod
    def load(cls, model_bytes):
        """Фабричный метод: создаёт экземпляр и подгружает модель."""
        instance = cls.__new__(cls)
        instance.model = joblib.load(model_bytes)
        if not hasattr(instance, "feature_columns"):
            instance.feature_columns = []
        return instance


    def get_features(self):
        return self.feature_columns