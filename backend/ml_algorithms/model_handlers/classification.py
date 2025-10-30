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




def gini_score(
    y_true,
    y_score
):
    return roc_auc_score(
        y_true=y_true,
        y_score=y_score
    )*2 - 1


def build_classification_plots(
    result_column,
    X,
    y,
    features,
    target: str = "Target column"
) -> io.BytesIO | None:
    """Creates visualization for classification results with all feature combinations"""
    try:
        if (X is None or y is None or result_column is None or 
            (hasattr(X, 'empty') and X.empty) or
            (hasattr(y, 'size') and y.size == 0) or 
            (hasattr(result_column, 'size') and result_column.size == 0)):
            raise ValueError("Invalid input data provided")

        if hasattr(result_column, 'flatten'):
            result_column = result_column.flatten()
        if hasattr(y, 'flatten'):
            y = y.flatten()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(10, 6))
            sns.histplot(result_column, bins=30, kde=True)
            plt.title("Distribution of Predictions")
            plt.xlabel("Predicted Values")
            plt.ylabel("Frequency")
            plt.grid(True, alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            zipf.writestr("predictions_histogram.png", buf.getvalue())

            if (hasattr(X, '__len__') and hasattr(y, '__len__') and 
                len(X) == len(y) and len(y) == len(result_column)):
                try:
                    from sklearn.metrics import confusion_matrix
                    cm = confusion_matrix(y, result_column)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                    plt.title('Confusion Matrix')
                    plt.ylabel('True Label')
                    plt.xlabel('Predicted Label')

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    zipf.writestr("confusion_matrix.png", buf.getvalue())
                except Exception as cm_error:
                    logging.warning(f"Could not create confusion matrix: {cm_error}")

            numeric_features = []
            if hasattr(X, 'select_dtypes'):
                numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
            else:
                numeric_features = [f for f in features if f in getattr(X, 'columns', [])]

            plot_combinations = []
            for i, feat1 in enumerate(numeric_features):
                for j, feat2 in enumerate(numeric_features):
                    if i < j:
                        plot_combinations.append((feat1, feat2))

            logging.info(f"Generating {len(plot_combinations)} scatter plots...")

            for feature_1, feature_2 in plot_combinations:
                try:
                    plt.figure(figsize=(10, 6))
                    scatter = sns.scatterplot(
                        x=X[feature_1],
                        y=X[feature_2],
                        hue=y,
                        palette='viridis',
                        alpha=0.7,
                        s=50
                    )
                    plt.title(f'{feature_1} vs {feature_2} by {target}')
                    plt.xlabel(feature_1)
                    plt.ylabel(feature_2)
                    plt.legend(title=target, bbox_to_anchor=(1.05, 1), loc='upper left')
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
                    pairplot_features = numeric_features[:5]
                    if len(pairplot_features) >= 2:
                        pairplot_df = X[pairplot_features].copy()
                        pairplot_df[target] = y
                        plt.figure(figsize=(15, 12))
                        pairplot = sns.pairplot(
                            pairplot_df, 
                            hue=target,
                            palette='viridis',
                            diag_kind='hist',
                            plot_kws={'alpha': 0.7, 's': 30}
                        )
                        pairplot.fig.suptitle(f'Pairplot of Features by {target}', y=1.02)

                        buf = io.BytesIO()
                        pairplot.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                        plt.close('all')
                        buf.seek(0)
                        zipf.writestr("feature_pairplot.png", buf.getvalue())

                except Exception as pairplot_error:
                    logging.warning(f"Could not create pairplot: {pairplot_error}")

            try:
                if len(numeric_features) > 1:
                    correlation_matrix = X[numeric_features].corr()

                    plt.figure(figsize=(12, 10))
                    sns.heatmap(
                        correlation_matrix, 
                        annot=True, 
                        fmt='.2f', 
                        cmap='coolwarm', 
                        center=0,
                        square=True
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
                import __main__ as main
                if hasattr(main, 'current_model') and hasattr(main.current_model, 'feature_importances_'):
                    feature_importance = main.current_model.feature_importances_

                    indices = np.argsort(feature_importance)[::-1]
                    sorted_features = [features[i] for i in indices]
                    sorted_importance = feature_importance[indices]

                    plt.figure(figsize=(12, max(8, len(features) * 0.3)))
                    bars = plt.barh(range(len(sorted_features)), sorted_importance)
                    plt.yticks(range(len(sorted_features)), sorted_features)
                    plt.title('Feature Importance')
                    plt.xlabel('Importance Score')
                    plt.gca().invert_yaxis()

                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                                f'{width:.3f}', ha='left', va='center')

                    plt.tight_layout()

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    zipf.writestr("feature_importance.png", buf.getvalue())

            except Exception as fi_error:
                logging.warning(f"Could not create feature importance plot: {fi_error}")
        zip_buffer.seek(0)
        logging.info(f"Generated ZIP with {len(plot_combinations) + 5} plots")
        return zip_buffer
    except Exception as e:
        logging.error(f"Error building classification plots: {e}")
        return None



class LogisticRegressionModel(BaseMLModel):
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
                    ('model', LogisticRegression())
                ])
                pipeline.fit(X_train, y_train)
                param_grid = {
                    'model__C': [0.001, 0.01, 0.1, 1, 10, 100],
                    'model__penalty': ['l1', 'l2'],
                    'model__solver': ['liblinear']
                }
                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                self.set_gridsearch_params(grid_search)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)

                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )

                zip_buffer = build_classification_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

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
                build_classification_plots(
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




class SVMClassificationModel(BaseMLModel):
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
                    ('model', SVC())
                ])
                pipeline.fit(X_train, y_train)
                param_grid = {
                    'model__C': [0.1, 1, 10, 100],
                    'model__kernel': ['linear', 'rbf'],
                    'model__gamma': ['scale', 'auto', 0.1, 0.01],
                    'model__class_weight': [None, 'balanced']
                }
                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                self.set_gridsearch_params(grid_search)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)

                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )

                zip_buffer = build_classification_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

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
                build_classification_plots(
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




class KNNClassificationModel(BaseMLModel):
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
                    ('model', KNeighborsClassifier())
                ])
                pipeline.fit(X_train, y_train)
                param_grid = {
                    'model__n_neighbors': [3, 5, 7, 9, 11, 15],
                    'model__weights': ['uniform', 'distance'],
                    'model__metric': ['euclidean', 'manhattan', 'minkowski'],
                }
                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                self.set_gridsearch_params(grid_search)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)

                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )

                zip_buffer = build_classification_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

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
                build_classification_plots(
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



class RandomForestClassificationModel(BaseMLModel):
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
                    ('model', RandomForestClassifier())
                ])
                pipeline.fit(X_train, y_train)
                param_grid = {
                    'model__n_estimators': [50, 100, 200],
                    'model__max_depth': [None, 10, 20, 30],
                    'model__min_samples_split': [2, 5, 10],
                    'model__min_samples_leaf': [1, 2, 4],
                    'model__max_features': ['sqrt', 'log2', None],
                    'model__class_weight': [None, 'balanced']
                }
                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                self.set_gridsearch_params(grid_search)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)

                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )

                zip_buffer = build_classification_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

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
                build_classification_plots(
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


class GradientBoostingClassificationModel(BaseMLModel):
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
                    ('model', GradientBoostingClassifier())
                ])
                pipeline.fit(X_train, y_train)
                param_grid = {
                    'model__n_estimators': [50, 100, 200],
                    'model__learning_rate': [0.01, 0.1, 0.2],
                    'model__max_depth': [3, 4, 5, 6],
                    'model__min_samples_split': [2, 5, 10],
                    'model__min_samples_leaf': [1, 2, 4],
                    'model__subsample': [0.8, 0.9, 1.0],
                    'model__max_features': ['sqrt', 'log2', None]
                }
                grid_search = GridSearchCV(
                    pipeline, 
                    param_grid, 
                    cv=5, 
                    scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                self.set_gridsearch_params(grid_search)
                best_pipeline = grid_search.best_estimator_
                self.model = best_pipeline
                self.is_fitted = True
                pred_vals = best_pipeline.predict(X_test)

                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, None
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                self.model.fit(X_train, y_train)
                pred_vals = self.model.predict(X_test)
                precision = precision_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                recall = recall_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                f1 = f1_score(
                    y_true=y_test,
                    y_pred=pred_vals
                )
                roc_auc = roc_auc_score(
                    y_true=y_test,
                    y_score=pred_vals
                )
                gini = gini_score(
                    y_true=y_test,
                    y_score=pred_vals
                )

                zip_buffer = build_classification_plots(
                    result_column=pred_vals,
                    X = X_test,
                    y = pred_vals,
                    features = X.columns,
                    target = self.target_column
                )

                return {
                    "Status":"ok",
                    "Precision":precision,
                    "Recall":recall,
                    "F1":f1,
                    "ROC_AUC":roc_auc,
                    "Gini":gini
                }, zip_buffer
        except Exception as e:
            logging.error("Error while training the model")
            logging.error(e)
            raise

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
                build_classification_plots(
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
