from .regression import LinearRegressionModel
from .base import BaseMLModel

from .regression import PolynomialRegressionModel, KNNRegressionModel, GradientBoostingRegressionModel, RandomForestModel
from .classification import LogisticRegressionModel, SVMClassificationModel, KNNClassificationModel, RandomForestClassificationModel, GradientBoostingClassificationModel
from .clusterization import KMeansClusterModel, DensityClusterModel
from typing import Iterable

import pandas as pd

MODEL_REGISTRY = {
    # === Regression ===
    "linear_regression": LinearRegressionModel,
    "polynomial_regression": PolynomialRegressionModel,
    "knn_regression": KNNRegressionModel,
    "gradient_boosting_regression": GradientBoostingRegressionModel,
    "random_forest_regression": RandomForestModel,

    # === Classification ===
    "logistic_regression": LogisticRegressionModel,
    "support_vector_machine_classification": SVMClassificationModel,
    "knn_classification": KNNClassificationModel,
    "random_forest_classification": RandomForestClassificationModel,
    "gradient_boosting_classification": GradientBoostingClassificationModel,

    # === Clusterization ===
    "kmeans_clusterization": KMeansClusterModel,
    "density_clusterization": DensityClusterModel,
}


def get_model(
    model_type: str,
    feature_columns: Iterable,
    target_column: str,
    df: pd.DataFrame
) -> BaseMLModel:
    """Возвращает инстанс нужной ML-модели по её типу."""
    try:
        model_class = MODEL_REGISTRY[model_type]
    except KeyError:
        raise ValueError(
            f"❌ Unknown model type: '{model_type}'. "
            f"Available: {list(MODEL_REGISTRY.keys())}")
    return model_class(
        feature_columns = feature_columns,
        target_column = target_column,
        df = df
    )
