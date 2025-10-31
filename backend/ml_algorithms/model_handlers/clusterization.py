from .base import BaseMLModel
from .base import BaseMLModel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.neighbors import KNeighborsRegressor
import joblib
import logging
from math import sqrt
from uuid import uuid1
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from typing import Tuple, BinaryIO
from os import name
from typing import Dict, List
import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import zipfile
import io
import matplotlib as mplb
mplb.use('Agg')
import matplotlib.pyplot as plt
import logging
from pprint import pprint
from django.http.response import HttpResponseBadRequest, HttpResponse
from rest_framework.response import Response
import json
from django.forms.models import model_to_dict

from api.models import Distribution
from typing import Iterable
import uuid
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from typing import Any
from abc import abstractmethod
from sklearn.preprocessing import OneHotEncoder
from typing import Tuple, Dict
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans, DBSCAN, OPTICS


def find_elbow_point_auto(wcss):
    """Простая и надежная версия"""
    if len(wcss) < 3:
        return 2
    improvements = [(wcss[i-1] - wcss[i]) / wcss[i-1] for i in range(1, len(wcss))]

    for k in range(1, len(improvements)):
        if improvements[k] < 0.10:
            candidate1 = k + 1
            break
    else:
        candidate1 = 2

    if len(wcss) >= 4:
        first_diff = np.diff(wcss)
        second_diff = np.diff(first_diff)
        candidate2 = np.argmin(second_diff) + 2 if len(second_diff) > 0 else 2
        candidate2 = min(candidate2, 4)
    else:
        candidate2 = 2
    candidate3 = max(2, len(wcss) // 2)
    return min(candidate1, candidate2, candidate3)


class BaseClusterModel(BaseMLModel):
    """Базовый класс для кластеризационных моделей."""
    def __init__(self, feature_columns: list|None = None, *args, **kwargs):
        self.feature_columns = feature_columns
        self.model = None
        self.is_fitted = False
        self.processed_feature_names = []
        self.best_params = None
        self.n_clusters = None

    def fit(self, df: pd.DataFrame, drop_features = False, *args, **kwargs) -> Tuple['BaseMLModel', dict|None, io.BytesIO|None]:
        """Полный пайплайн обучения модели."""
        try:
            df_processed = self._prepare_data(df, drop_features=drop_features)
            X = df_processed[self.processed_feature_names]
            response, img_zip = self._train(X)
            self.is_fitted = True
            logging.info(f"Модель успешно обучена на {len(self.processed_feature_names)} признаках")
            return self, response, img_zip
        except Exception as e:
            logging.error(f"Ошибка при обучении модели: {e}")
            raise

    def refit(self, df: pd.DataFrame, *args, **kwargs) -> Tuple['BaseMLModel', dict|None, io.BytesIO|None]:
        """Полный пайплайн  реобучения модели."""
        try:
            self.is_fitted = False
            df_processed = self._prepare_data(df)
            X = df_processed[self.processed_feature_names]
            response, img_zip = self._train(X)
            self.model = None
            self.is_fitted = False
            logging.info(f"Модель успешно реобучена на {len(self.processed_feature_names)} признаках")
            return self, response, img_zip
        except Exception as e:
            logging.error(f"Ошибка при обучении модели: {e}")
            raise

    @abstractmethod
    def _train(self, X: pd.DataFrame, *args, **kwargs)->Tuple[dict|None, io.BytesIO|None]:
        """Внутренний метод обучения - реализуется в подклассах."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: pd.DataFrame, *args, **kwargs)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]:
        """Делает предсказания."""
        raise NotImplementedError

    def _prepare_data(self, df: pd.DataFrame, drop_features = False, *args, **kwargs) -> pd.DataFrame:
        """Подготовка данных: отбор признаков, кодирование."""
        if self.target_column not in df.columns:
            raise ValueError(f"Целевая переменная '{self.target_column}' не найдена в данных")

        if self.feature_columns is None:
            self.feature_columns = [col for col in df.columns if col != self.target_column]

        missing_features = [f for f in self.feature_columns if f not in df.columns]
        if missing_features:
            raise ValueError(f"Отсутствуют признаки: {missing_features}")

        working_df = df[self.feature_columns + [self.target_column]].copy()

        if drop_features:
            working_df, selected_columns = self._feature_analyzer(working_df)

        working_df = self._feature_encoder(working_df)

        self.processed_feature_names = [col for col in working_df.columns if col != self.target_column]

        return working_df
    
    def _feature_analyzer(self, df: pd.DataFrame, var_coef_threshold=0.01, correlation_threshold=0.8, *args, **kwargs) -> tuple[pd.DataFrame, list]:
        """Отбрасывает бесполезные фичи, отбирает по коэффициенту вариации и корреляции пирсона"""
        try:
            df = df.dropna()

            feature_columns = [col for col in df.columns if col != self.target_column]
            
            numeric_columns = [col for col in feature_columns if np.issubdtype(df[col].dtype, np.number)]
            categorical_columns = [col for col in feature_columns if col not in numeric_columns]
            
            if not numeric_columns:
                logging.warning("В данных нет числовых признаков")
                return df, [self.target_column] + feature_columns

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
                return df, [self.target_column] + feature_columns

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
            
            final_columns_with_target = final_columns + [self.target_column]
            
            return df[final_columns_with_target], final_columns_with_target
            
        except Exception as e:
            logging.error(e)
            return df, list(df.columns)

    def _feature_encoder(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
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

        logging.info(f"Закодировано {len(categorical_columns)} категориальных признаков в {X_encoded_df.shape[1]} бинарных колонок")

        return result_df

    def save(self, path: str | None = None, *args, **kwargs):
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
    def load(cls, model_bytes, *args, **kwargs):
        """Фабричный метод для загрузки полного объекта."""
        loaded_obj = joblib.load(model_bytes)
        instance = cls.__new__(cls)
        instance.__dict__.update(loaded_obj.__dict__)
        return instance

    def get_features(self, *args, **kwargs):
        """Возвращает список используемых признаков."""
        return self.processed_feature_names if self.is_fitted else self.feature_columns

    @classmethod
    def reborn(
        cls,
        feature_columns: list,
        model,
        processed_feature_names: list,
        *args, **kwargs
    ):
        """Создает новый инстанс класса с готовой моделью."""
        instance = cls.__new__(cls)
        instance.feature_columns = feature_columns
        instance.model = model
        instance.is_fitted = True
        instance.processed_feature_names = processed_feature_names
        instance.best_params = instance.model.named_steps.get('model').get_params()
        return instance

    def _calculate_metrics(self, X: pd.DataFrame, labels: np.ndarray, *args, **kwargs) -> dict:
        """Вычисляет метрики качества кластеризации."""
        if len(np.unique(labels)) < 2:
            return {
                'silhouette_score': -1,
                'calinski_harabasz_score': -1, 
                'davies_bouldin_score': float('inf'),
                'n_clusters': len(np.unique(labels))
            }
        
        return {
            'silhouette_score': silhouette_score(X, labels),
            'calinski_harabasz_score': calinski_harabasz_score(X, labels),
            'davies_bouldin_score': davies_bouldin_score(X, labels),
            'n_clusters': len(np.unique(labels)),
            'cluster_sizes': np.bincount(labels[labels >= 0])  # Игнорируем шум (-1)
        }


def build_clusterization_plots(
    X,
    cluster_labels, 
    features,
    cluster_name: str = "Clusters",
    max_features_for_pairplot: int = 6,
    max_scatter_plots: int = 20,
    *args, **kwargs
) -> io.BytesIO | None:
    """Creates comprehensive visualization for clustering results."""
    try:
        if (X is None or cluster_labels is None) or \
            (hasattr(X, 'empty') and X.empty) or \
            (hasattr(cluster_labels, 'size') and cluster_labels.size == 0):
            raise ValueError("Invalid input data provided")

        if hasattr(cluster_labels, 'flatten'):
            cluster_labels = cluster_labels.flatten()

        unique_clusters = np.unique(cluster_labels)
        n_clusters = len(unique_clusters)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(12, 6))
            cluster_counts = np.bincount(cluster_labels[cluster_labels >= 0])
            cluster_ids = np.arange(len(cluster_counts))
            bars = plt.bar(cluster_ids, cluster_counts, color='skyblue', alpha=0.7)
            plt.title(f"Distribution of Clusters (Total: {n_clusters} clusters)")
            plt.xlabel("Cluster ID")
            plt.ylabel("Number of Points")
            plt.grid(True, alpha=0.3)
            for bar, count in zip(bars, cluster_counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(count), ha='center', va='bottom')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            zipf.writestr("cluster_distribution.png", buf.getvalue())


            plt.figure(figsize=(10, 6))
            metrics_text = f"""
            Clustering Results Summary:

            • Number of clusters: {n_clusters}
            • Total points: {len(cluster_labels)}
            • Cluster sizes: {dict(zip(cluster_ids, cluster_counts))}
            • Noise points: {np.sum(cluster_labels == -1) if -1 in cluster_labels else 0}
            
            Features used: {len(features)}
            """

            plt.text(0.1, 0.5, metrics_text, fontsize=12, va='center', 
                    fontfamily='monospace', linespacing=1.5)
            plt.axis('off')
            plt.title("Clustering Summary")

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            zipf.writestr("clustering_summary.png", buf.getvalue())

            numeric_features = []
            if hasattr(X, 'select_dtypes'):
                numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
            else:
                numeric_features = [f for f in features if f in getattr(X, 'columns', [])]

            plot_combinations = []
            for i, feat1 in enumerate(numeric_features):
                for j, feat2 in enumerate(numeric_features):
                    if i < j and len(plot_combinations) < max_scatter_plots:
                        plot_combinations.append((feat1, feat2))
            logging.info(f"Generating {len(plot_combinations)} scatter plots...")
            for feature_1, feature_2 in plot_combinations[:max_scatter_plots]:
                try:
                    plt.figure(figsize=(10, 7))
                    if -1 in cluster_labels:
                        noise_mask = cluster_labels == -1
                        plt.scatter(X[feature_1][noise_mask], X[feature_2][noise_mask],
                            c='gray', alpha=0.3, s=30, label='Noise', marker='x')
                        cluster_mask = ~noise_mask
                        scatter = plt.scatter(X[feature_1][cluster_mask], X[feature_2][cluster_mask],
                            c=cluster_labels[cluster_mask], cmap='viridis',
                            alpha=0.7, s=50)
                    else:
                        scatter = plt.scatter(X[feature_1], X[feature_2],
                                            c=cluster_labels, cmap='viridis',
                                            alpha=0.7, s=50)
                    plt.title(f'{feature_1} vs {feature_2} by {cluster_name}')
                    plt.xlabel(feature_1)
                    plt.ylabel(feature_2)
                    if -1 in cluster_labels:
                        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    else:
                        plt.colorbar(scatter, label=cluster_name)
                    plt.grid(True, alpha=0.3)
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    filename = f"scatter_{feature_1}_vs_{feature_2}.png".replace(' ', '_')
                    zipf.writestr(filename, buf.getvalue())
                except Exception as scatter_error:
                    logging.warning(f"Could not create scatter plot for {feature_1}, {feature_2}: {scatter_error}")
                    continue
            if len(numeric_features) >= 2:
                try:
                    pairplot_features = numeric_features[:max_features_for_pairplot]
                    if len(pairplot_features) >= 2:
                        pairplot_df = X[pairplot_features].copy()
                        pairplot_df[cluster_name] = cluster_labels
                        if n_clusters <= 10:
                            plt.figure(figsize=(15, 12))
                            pairplot = sns.pairplot(
                                pairplot_df, 
                                hue=cluster_name,
                                palette='viridis' if n_clusters <= 8 else 'tab20',
                                diag_kind='hist',
                                plot_kws={'alpha': 0.7, 's': 30}
                            )
                            pairplot.fig.suptitle(f'Pairplot of Features by {cluster_name}', y=1.02)
                            buf = io.BytesIO()
                            pairplot.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                            plt.close('all')
                            buf.seek(0)
                            zipf.writestr("feature_pairplot.png", buf.getvalue())
                        else:
                            logging.warning(f"Too many clusters ({n_clusters}) for pairplot")
                except Exception as pairplot_error:
                    logging.warning(f"Could not create pairplot: {pairplot_error}")
            try:
                if len(numeric_features) > 1:
                    correlation_matrix = X[numeric_features].corr()
                    
                    plt.figure(figsize=(12, 10))
                    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # Верхний треугольник
                    
                    sns.heatmap(
                        correlation_matrix, 
                        annot=True, 
                        fmt='.2f', 
                        cmap='coolwarm', 
                        center=0,
                        square=True,
                        mask=mask
                    )
                    plt.title('Feature Correlation Matrix')
                    plt.xticks(rotation=45, ha='right')
                    plt.yticks(rotation=0)
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    zipf.writestr("correlation_matrix.png", buf.getvalue())
                    
            except Exception as corr_error:
                logging.warning(f"Could not create correlation matrix: {corr_error}")
            try:
                if len(numeric_features) >= 2:
                    from sklearn.decomposition import PCA
                    from sklearn.preprocessing import StandardScaler
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X[numeric_features])

                    pca = PCA(n_components=2)
                    X_pca = pca.fit_transform(X_scaled)
                    
                    plt.figure(figsize=(10, 7))
                    if -1 in cluster_labels:
                        noise_mask = cluster_labels == -1
                        plt.scatter(X_pca[noise_mask, 0], X_pca[noise_mask, 1],
                            c='gray', alpha=0.3, s=30, label='Noise', marker='x')
                        cluster_mask = ~noise_mask
                        scatter = plt.scatter(X_pca[cluster_mask, 0], X_pca[cluster_mask, 1],
                                            c=cluster_labels[cluster_mask], cmap='viridis',
                                            alpha=0.7, s=50)
                    else:
                        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1],
                                            c=cluster_labels, cmap='viridis',
                                            alpha=0.7, s=50)
                    plt.title(f'PCA Projection (Variance: {pca.explained_variance_ratio_.sum():.2f})')
                    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
                    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
                    if -1 in cluster_labels:
                        plt.legend()
                    else:
                        plt.colorbar(scatter, label=cluster_name)
                    plt.grid(True, alpha=0.3)
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    zipf.writestr("pca_projection.png", buf.getvalue())
            except Exception as pca_error:
                logging.warning(f"Could not create PCA projection: {pca_error}")
        zip_buffer.seek(0)
        total_plots = 3 + len(plot_combinations) 
        logging.info(f"Generated ZIP with {total_plots} clustering plots")
        return zip_buffer
    except Exception as e:
        logging.error(f"Error building clustering plots: {e}")
        return None


class KMeansClusterModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, *args, **kwargs)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            if not self.is_fitted or not self.model:
                X_train = X
                self.feature_columns = X.columns
                wcss = []
                k_range = range(1, 12)

                for k in k_range:
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    kmeans.fit(X)
                    wcss.append(kmeans.inertia_)

                k_clusters = find_elbow_point_auto(wcss)
                self.n_clusters = k_clusters
                best_pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('model', KMeans(n_clusters=k_clusters))
                ])
                best_pipeline.fit(X_train)
                self.is_fitted = True
                self.model = best_pipeline
                return {
                    "Status":"ok",
                    "Number of clusters":self.n_clusters
                }, None
            else:
                X_train, X_test = train_test_split(
                    X,
                    random_state=42
                )
                self.model = self.model.fit(X = X_train)
                y_test = self.model.predict(X_test)
                zip_buffer = build_clusterization_plots(
                    X = X_test,
                    cluster_labels = y_test,
                    features = X.columns,
                )
                return {
                    "Status":"ok",
                    "Number of clusters": self.n_clusters,
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

    def predict(self, X: pd.DataFrame, *args, **kwargs)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            target = self.target_column
            features = self.feature_columns
            if not features:
                raise ValueError("The model has no determined features or has not beet fit yet")
            given_columns = X.columns
            if X.empty or X is None:
                raise Exception("Improper dataframe given")
            for col in features:
                if col not in given_columns:
                    raise ValueError("Could not find an essential column")
            result_taret = np.array(self.model.predict(X[features])).reshape(-1, 1)
            X_extended = X.copy()
            X_extended[target] = result_taret
            return (
                result_taret, 
                X_extended, 
                build_clusterization_plots(
                    X = X,
                    cluster_labels = result_taret,
                    features = X.columns,
                ))
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)





class DensityClusterModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, *args, **kwargs)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            if not self.is_fitted or not self.model:
                X_train = X
                self.feature_columns = X.columns
                from sklearn.neighbors import NearestNeighbors
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_train)
                nbrs = NearestNeighbors(n_neighbors=5)
                nbrs.fit(X_scaled)
                distances, indices = nbrs.kneighbors(X_scaled)
                k_distances = np.sort(distances[:, -1])
                eps = np.percentile(k_distances, 90)
                min_samples = max(5, min(15, len(X_train) // 20))
                best_pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('model', DBSCAN(eps=eps, min_samples=min_samples))
                ])
                best_pipeline.fit(X_train)
                dbscan_model = best_pipeline.named_steps['model']
                labels = dbscan_model.labels_
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                self.is_fitted = True
                self.model = best_pipeline
                self.n_clusters = n_clusters
                
                return {
                    "Status":"ok",
                    "Number of clusters": n_clusters,
                    "eps": round(eps, 3),
                    "min_samples": min_samples
                }, None
            else:
                X_train, X_test = train_test_split(
                    X,
                    random_state=42
                )
                self.model = self.model.fit(X = X_train)
                dbscan_model = self.model.named_steps['model']
                y_test = dbscan_model.labels_
                
                zip_buffer = build_clusterization_plots(
                    X = X_test,
                    cluster_labels = y_test,
                    features = X.columns,
                )
                return {
                    "Status":"ok",
                    "Number of clusters": self.n_clusters,
                }, zip_buffer
                
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

    def predict(self, X: pd.DataFrame, *args, **kwargs)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            target = self.target_column
            features = self.feature_columns
            if not features:
                raise ValueError("The model has no determined features or has not beet fit yet")
            given_columns = X.columns
            if X.empty or X is None:
                raise Exception("Improper dataframe given")
            for col in features:
                if col not in given_columns:
                    raise ValueError("Could not find an essential column")
            X_subset = X[features]
            self.model.fit(X_subset)
            dbscan_model = self.model.named_steps['model']
            result_target = dbscan_model.labels_
            
            X_extended = X.copy()
            X_extended[target] = result_target
            return (
                result_target, 
                X_extended, 
                build_clusterization_plots(
                    X = X,
                    cluster_labels = result_target,
                    features = X.columns,
                ))
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)