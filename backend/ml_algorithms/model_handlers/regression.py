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


def build_regression_plots(
    result_column,
    X,
    y,
    features: Iterable,
    target: str = "Target column"
) -> io.BytesIO | None:
    """Creates visualization from regression"""
    try:
        if hasattr(result_column, 'flatten'):
            result_column = result_column.flatten()
        if hasattr(y, 'flatten'):
            y = y.flatten()
        if (X is None or y is None or result_column is None or 
            X.empty or
            (hasattr(X, 'size') and X.size == 0) or 
            (hasattr(y, 'size') and y.size == 0) or 
            (hasattr(result_column, 'size') and result_column.size == 0)):
            raise Exception("Improper arrays given")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(8, 6))
            sns.histplot(result_column)
            plt.title("Result histogram")
            plt.grid(True)
            plt.tight_layout()
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"histogram_{uuid.uuid4()}.png", buf.getvalue())
            
            if (X is not None and y is not None and 
                hasattr(X, '__len__') and hasattr(y, '__len__') and 
                len(X) == len(y)):
                
                for feature in features:
                    if feature not in X.columns:
                        continue
                        
                    plt.figure(figsize=(8, 6))
                    sns.scatterplot(
                        x=X[feature],
                        y=y
                    )
                    plt.title(f"Connection between {feature} and {target}")
                    plt.grid(True)
                    plt.tight_layout()
                    plt.axhline(0, color='black', linewidth=0.5)
                    plt.axvline(0, color='black', linewidth=0.5)

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300)
                    plt.close()
                    buf.seek(0)
                    zipf.writestr(f"scatter_{feature}_{uuid.uuid4()}.png", buf.getvalue())
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        logging.error(f"Error while building plots: {e}")
        logging.error("An error while building plots")
        raise


class LinearRegressionModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            uid = uuid1()
            X[uid] = y
            X = X.dropna()
            y = X[uid].copy()
            del X[uid]
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
                    'poly__degree': [1],
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
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                r2 = r2_score(y_test, pred_vals)
                mse = mean_squared_error(y_test, pred_vals)
                rmse = sqrt(mse)
                mae = mean_absolute_error(y_test, pred_vals)

                zip_buffer = build_regression_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "status":"ok",
                    "R2":r2,
                    "MSE":mse,
                    "RMSE":rmse,
                    "MAE":mae
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }, None

    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            given_columns = X.columns
            features = self.feature_columns
            target = self.target_column
            if not features or not target:
                raise ValueError("Could not find an essential column")
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
                build_regression_plots(
                    result_column=result_taret,
                    X = X,
                    y = result_taret,
                    features = X.columns,
                    target = self.target_column
                    )
                )
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)



class PolynomialRegressionModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            uid = uuid1()
            X[uid] = y
            X = X.dropna()
            y = X[uid].copy()
            del X[uid]
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
                    'poly__degree': [1, 2, 3, 4],
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
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                r2 = r2_score(y_test, pred_vals)
                mse = mean_squared_error(y_test, pred_vals)
                rmse = sqrt(mse)
                mae = mean_absolute_error(y_test, pred_vals)

                zip_buffer = build_regression_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "status":"ok",
                    "R2":r2,
                    "MSE":mse,
                    "RMSE":rmse,
                    "MAE":mae
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }, None

    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            given_columns = X.columns
            features = self.feature_columns
            target = self.target_column
            if not features or not target:
                raise ValueError("Could not find an essential column")
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
                build_regression_plots(
                    result_column=result_taret,
                    X = X,
                    y = result_taret,
                    features = X.columns,
                    target = self.target_column
                    )
                )
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)


class KNNRegressionModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            uid = uuid1()
            X[uid] = y
            X = X.dropna()
            y = X[uid].copy()
            del X[uid]
            if not self.is_fitted or not self.model:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('model', KNeighborsRegressor(
                        n_jobs=-1
                    ))
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
                    'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
                    'n_neighbors': np.arange(1, 10),
                    'weights':['uniform', 'distance']
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
                }, None
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
                }, build_regression_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }, None


    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            given_columns = X.columns
            features = self.feature_columns
            target = self.target_column
            if not features or not target:
                raise ValueError("Could not find an essential column")
            for col in features:
                if col not in given_columns:
                    raise ValueError("Could not find an essential column")
            result_taret = np.ndarray(self.model.predict(X[features])).reshape(-1, 1)
            X_extended = X.copy()
            X_extended[target] = result_taret
            return (
                result_taret, 
                X_extended, 
                build_regression_plots(
                    result_column=result_taret,
                    X = X,
                    y = result_taret,
                    features = X.columns,
                    target = self.target_column
                    )
                )
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)


class GradientBoostingRegressionModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            uid = uuid1()
            X[uid] = y
            X = X.dropna()
            y = X[uid].copy()
            del X[uid]
            if not self.is_fitted or not self.model:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('model', GradientBoostingRegressor())
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
                    'loss': ['squared_error', 'absolute_error', 'huber', 'quantile'],
                    'criterion': ['friedman_mse', 'squared_error'],
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
                }, None
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
                }, build_regression_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }, None


    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            given_columns = X.columns
            features = self.feature_columns
            target = self.target_column
            if not features or not target:
                raise ValueError("Could not find an essential column")
            for col in features:
                if col not in given_columns:
                    raise ValueError("Could not find an essential column")
            result_taret = np.ndarray(self.model.predict(X[features])).reshape(-1, 1)
            X_extended = X.copy()
            X_extended[target] = result_taret
            return (
                result_taret, 
                X_extended, 
                build_regression_plots(
                    result_column=result_taret,
                    X = X,
                    y = result_taret,
                    features = X.columns,
                    target = self.target_column
                    )
                )
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)


class RandomForestModel(BaseMLModel):
    def _train(self, X: pd.DataFrame, y: pd.Series)->Tuple[dict|None, io.BytesIO|None]:
        try:
            """Внутренний метод обучения"""
            uid = uuid1()
            X[uid] = y
            X = X.dropna()
            y = X[uid].copy()
            del X[uid]
            if not self.is_fitted or not self.model:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                pipeline = Pipeline([
                    ('scaler', StandardScaler()),
                    ('model', RandomForestRegressor())
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
                    'n_estimators': [100, 200, 500, 700, 1000, 1500],
                    'criterion': ['friedman_mse', 'squared_error'],
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
                }, None
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
                }, build_regression_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            return {
                    "error":str(e)
                }, None


    def predict(self, X: pd.DataFrame)->tuple[np.ndarray, pd.DataFrame, io.BytesIO|None]|None:
        """Делает предсказания"""
        try:
            X = X.dropna()
            given_columns = X.columns
            features = self.feature_columns
            target = self.target_column
            if not features or not target:
                raise ValueError("Could not find an essential column")
            for col in features:
                if col not in given_columns:
                    raise ValueError("Could not find an essential column")
            result_taret = np.ndarray(self.model.predict(X[features])).reshape(-1, 1)
            X_extended = X.copy()
            X_extended[target] = result_taret
            return (
                result_taret, 
                X_extended, 
                build_regression_plots(
                    result_column=result_taret,
                    X = X,
                    y = result_taret,
                    features = X.columns,
                    target = self.target_column
                    )
                )
        except Exception as e:
            logging.error("Internal error while fitting the model")
            logging.error(e)

