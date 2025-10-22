import joblib
import io
from abc import ABC, abstractmethod
import pandas as pd
import logging
import numpy as np
from sklearn.preprocessing import OneHotEncoder

class BaseMLModel(ABC):
    """Базовый класс для всех ML-моделей."""

    def __init__(self, target_column: str, feature_columns: list|None = None):
        """
        Args:
            target_column: Имя целевой переменной
            feature_columns: Список признаков (если None - возьмет все кроме target)
        """
        self.target_column = target_column
        self.feature_columns = feature_columns
        self.model = None
        self.is_fitted = False
        self.processed_feature_names = []

    def fit(self, df: pd.DataFrame) -> 'BaseMLModel':
        """Полный пайплайн обучения модели."""
        try:
            df_processed = self._prepare_data(df)
            X = df_processed[self.processed_feature_names]
            y = df_processed[self.target_column]
            self._train(X, y)
            
            self.is_fitted = True
            logging.info(f"Модель успешно обучена на {len(self.processed_feature_names)} признаках")
            return self
        except Exception as e:
            logging.error(f"Ошибка при обучении модели: {e}")
            raise

    @abstractmethod
    def _train(self, X: pd.DataFrame, y: pd.Series)->dict:
        """Внутренний метод обучения - реализуется в подклассах."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame]:
        """Делает предсказания."""
        raise NotImplementedError

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Подготовка данных: отбор признаков, кодирование."""
        if self.target_column not in df.columns:
            raise ValueError(f"Целевая переменная '{self.target_column}' не найдена в данных")

        if self.feature_columns is None:
            self.feature_columns = [col for col in df.columns if col != self.target_column]

        missing_features = [f for f in self.feature_columns if f not in df.columns]
        if missing_features:
            raise ValueError(f"Отсутствуют признаки: {missing_features}")

        working_df = df[self.feature_columns + [self.target_column]].copy()

        working_df, selected_columns = self._feature_analyzer(working_df)

        working_df = self._feature_encoder(working_df)

        self.processed_feature_names = [col for col in working_df.columns if col != self.target_column]

        return working_df

    def _feature_analyzer(self, df: pd.DataFrame, var_coef_threshold=0.05, correlation_threshold=0.75) -> tuple[pd.DataFrame, list]:
        """Отбрасывает бесполезные фичи, отбирает по коэффициенту вариации и корреляции пирсона"""
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
            
            if self.target_column not in final_columns:
                final_columns.append(self.target_column)
                
            return df[final_columns], final_columns
        except Exception as e:
            logging.error(e)
            return df, list(df.columns)

    def _feature_encoder(self, df: pd.DataFrame) -> pd.DataFrame:
        """Кодирует категориальные признаки как One-Hot-Encoder"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not categorical_columns:
            return df

        encoder = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
        X_encoded = encoder.fit_transform(df[categorical_columns])

        encoded_columns = encoder.get_feature_names_out(categorical_columns)
        X_encoded_df = pd.DataFrame(X_encoded, columns=encoded_columns, index=df.index)

        result_df = pd.concat([df[numeric_columns], X_encoded_df], axis=1)

        result_df[self.target_column] = df[self.target_column]
        
        logging.info(f"Закодировано {len(categorical_columns)} категориальных признаков в {X_encoded_df.shape[1]} бинарных колонок")

        return result_df

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
        """Возвращает список используемых признаков."""
        return self.processed_feature_names if self.is_fitted else self.feature_columns