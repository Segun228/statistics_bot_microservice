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

def build_classification_plots(
    result_column,
    X,
    y,
    features,
    target:str = "Target column"
)->io.BytesIO|None:
    """Creates visualization from classification

    Args:
        result_column (series or dataframe or nd): targets
        X (dataframe): features
        y (series or dataframe or nd): targets
        features (Iterable): list of feature names
        target (str, optional):  Defaults to "Target column"

    Returns:
        io.BytesIO|None: zip with photos
    """
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(8, 6))
            sns.histplot(result_column)
            plt.title("Class distribution histogram")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"{uuid1()}.png", buf.getvalue())
            if X is not None and y is not None and len(X) == len(y):
                buf = io.BytesIO()
                dupl_features = []
                for i in range(1, len(features)):
                    dupl_features.append((features[i-1], features[i]))
                for feature1, feature2 in dupl_features:
                    plt.figure(figsize=(8, 6))
                    sns.scatterplot(
                        x=feature1,
                        y=feature2
                    )
                    plt.title(f"Distribution between {feature1} and {feature2}")
                    plt.legend()
                    plt.grid(True)
                    plt.tight_layout()
                    plt.axhline(0, color='black', linewidth=0.5)
                    plt.axvline(0, color='black', linewidth=0.5)

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300)
                    plt.close()
                    buf.seek(0)
                    zipf.writestr(f"{uuid1()}.png", buf.getvalue())
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        logging.error(e)
        logging.error("An error while building plots")
        raise

class LogisticRegressionModel(BaseMLModel):
    pass


class SVMClassificationModel(BaseMLModel):
    pass


class KNNClassificationModel(BaseMLModel):
    pass


class RandomForestClassificationModel(BaseMLModel):
    pass


class GradientBoostingClassificationModel(BaseMLModel):
    pass
