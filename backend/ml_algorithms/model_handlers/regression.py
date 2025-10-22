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
import joblib
import logging
from math import sqrt

class LinearRegressionModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->dict:
        try:
            """Внутренний метод обучения"""
            if not self.is_fitted or not self.model:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )


                pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
                    ('model', Ridge(random_state=42))
                ])

                pipeline.fit(X_train, y_train)

                y_pred = pipeline.predict(X_test)

                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                print(f"MSE: {mse:.4f}")
                print(f"RMSE: {np.sqrt(mse):.4f}")
                print(f"MAE: {mae:.4f}")
                print(f"R²: {r2:.4f}")


                param_grid = {
                    'poly__degree': [1, 2],
                    'model__alpha': [0.0001, 0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10, 50, 100, 200],
                    'model__solver': ['auto', 'svd', 'cholesky', 'lsqr']
                }

                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )

                grid_search.fit(X_train, y_train)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)
                r2 = r2_score(y_test, pred_vals)
                mse = mean_squared_error(y_test, pred_vals)
                rmse = sqrt(mse)
                mae = mean_absolute_error(y_test, pred_vals)
                return {
                    "status":"ok",
                    "R2":r2,
                    "MSE":mse,
                    "RMSE":rmse,
                    "MAE":mae
                }
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                r2 = r2_score(y_test, pred_vals)
                mse = mean_squared_error(y_test, pred_vals)
                rmse = sqrt(mse)
                mae = mean_absolute_error(y_test, pred_vals)
                return {
                    "status":"ok",
                    "R2":r2,
                    "MSE":mse,
                    "RMSE":rmse,
                    "MAE":mae
                }
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }


    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame]:
        """Делает предсказания"""
        raise NotImplementedError


class PolynomialRegressionModel(BaseMLModel):
    pass


class KNNRegressionModel(BaseMLModel):
    pass


class GradientBoostingRegressionModel(BaseMLModel):
    pass


class RandomForestModel(BaseMLModel):
    pass
