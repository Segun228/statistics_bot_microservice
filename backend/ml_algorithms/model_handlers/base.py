import joblib
import io
from abc import ABC, abstractmethod
import pandas as pd
import logging
from math import sqrt
import numpy as np
from sklearn.preprocessing import OneHotEncoder

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


    def _feature_analyzer(self, df: pd.DataFrame, var_coef_threshold=0.05, correlation_threshold=0.75)->tuple[pd.DataFrame, list]:
        """Отбрасывает бесполезные фичи, отбирает по коэфициенту вариации и корелляции пирсона"""
        try:
            df = df.dropna()
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if not numeric_columns:
                logging.warning("В данных нет числовых признаков")
                return df, list(df.columns)

            final_columns = []
            for col in numeric_columns:
                mean = df[col].mean()
                standart_deviation = df[col].std()
                if standart_deviation == 0:
                    continue
                elif mean == 0:
                    final_columns.append(col)
                    continue
                varince_coef = standart_deviation / mean
                if varince_coef >= var_coef_threshold:
                    final_columns.append(col)

            if not final_columns:
                logging.warning("Все признаки отфильтрованы по коэффициенту вариации")
                return df, list(df.columns)

            corr_df_pearson = df[final_columns].corr()
            corr_df_spearman = df[final_columns].corr(method="spearman")
            high_cor_column = []
            for i in range(len(corr_df_pearson.columns)):
                for j in range(i + 1, len(corr_df_pearson.columns)):
                    corr_value = corr_df_pearson.iloc[i, j]
                    spearman_corr_value = corr_df_spearman.iloc[i, j]
                    if abs(float(corr_value)) > correlation_threshold or abs(float(spearman_corr_value)) > correlation_threshold:
                        col1 = corr_df_pearson.columns[i]
                        col2 = corr_df_pearson.columns[j]
                        var1 = df[col1].var()
                        var2 = df[col2].var()
                        
                        if var1 > var2:
                            high_cor_column.append(col2)
                        else:
                            high_cor_column.append(col1)
            high_cor_column = set(high_cor_column)
            for col in high_cor_column:
                final_columns.remove(col)
            final_columns.extend(categorical_columns)
            return df[final_columns], final_columns
        except Exception as e:
            logging.error(e)
            return df, list(df.columns)


    def _feature_encoder(self, df: pd.DataFrame)->pd.DataFrame:
        """Кодирует категориальные признаки как One-Hot-Encoder

        Args:
            df (pd.DataFrame)

        Returns:
            tuple[pd.DataFrame, list]
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        encoder = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
        X_encoded = encoder.fit_transform(df[categorical_columns])

        encoded_columns = encoder.get_feature_names_out(categorical_columns)
        X_encoded_df = pd.DataFrame(X_encoded, columns=encoded_columns, index=df.index)

        result_df = pd.concat([df[numeric_columns], X_encoded_df], axis=1)
        logging.info(f"Закодировано {len(categorical_columns)} категориальных признаков в {X_encoded_df.shape[1]} бинарных колонок")

        return result_df


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