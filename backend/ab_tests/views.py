import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
)

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from api.models import Distribution, Dataset
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.serializers import DistributionSerializer, DatasetSerializer

from api.permissions import IsAdminOrDebugOrReadOnly

from backend.authentication import TelegramAuthentication

from django.shortcuts import get_object_or_404
import logging

from kafka_broker.utils import build_log_message

from rest_framework import mixins, generics

from django.core.cache import cache
from dotenv import load_dotenv

from django.http import HttpResponseBadRequest

import os
import requests

import uuid
from io import BytesIO


from rest_framework.views import APIView
from django.forms.models import model_to_dict

from rest_framework.response import Response
from rest_framework import status

from rest_framework.exceptions import ParseError, PermissionDenied, ValidationError, NotAuthenticated, APIException

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import sklearn as skl

from .handlers import handlers
import io
load_dotenv()

class AuthenticatedAPIView:
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]


logger = logging.getLogger(__name__)
CACHE = os.getenv("CACHE")

CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
if not CLOUD_API_KEY:
    raise ValueError("An error occured while trying to get env variable CLOUD_API_KEY")


if not CACHE or CACHE.lower() in ("no", "false", "none", "na", "0", 0, -1):
    CACHE = False
else:
    CACHE = True

def download_dataset(dataset: Dataset)->BytesIO|None:
    try:
        url = dataset.url
        if not url:
            raise ValueError("No URL provided for the dataset.")
        
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download. HTTP {response.status_code}")

        return BytesIO(response.content)
    
    except Exception as e:
        logging.exception("Dataset download failed.")
        local_exception_handler(e)


def local_exception_handler(e):
    if isinstance(e, ValidationError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(e, (NotAuthenticated, AuthenticationFailed)):
        code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(e, PermissionDenied):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(e, NotFound):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(e, MethodNotAllowed):
        code = status.HTTP_405_METHOD_NOT_ALLOWED
    elif isinstance(e, NotAcceptable):
        code = status.HTTP_406_NOT_ACCEPTABLE
    elif isinstance(e, UnsupportedMediaType):
        code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    elif isinstance(e, Throttled):
        code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(e, APIException):
        code = e.status_code
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.exception(f"Unhandled exception: {str(e)}", exc_info=True)
    return Response({"error": str(e)}, status=code)


class CountMDEView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"count_mde_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.count_mde(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta
            )
            if CACHE:
                cache.set(
                    f"count_mde_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class SampleSizeView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"count_n_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")
            mde = request.get("mde", 5)

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.count_n(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
                mde=mde,
                k=1
            )
            if CACHE:
                cache.set(
                    f"count_n_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)




class Z_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"ztest_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.z_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"ztest_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)



class T_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"ttest_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.t_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"ttest_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)



class Chi_2Sample_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"chi2_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.chi_2test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"chi2_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Cramer_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"cramer_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.cramer_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"cramer_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class KS_2Sample_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"ks_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.ks_2test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"ks_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class U_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"utest_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.u_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"utest_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Lilleforce_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"lil_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.lilleforce_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"lil_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Shap_Wilke_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"shap_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.shapwilk_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"shap_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Welch_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"welch_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.welch_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"welch_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Anderson_Darling_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"anderson_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.anderson_darling_test(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"anderson_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)


class Bootstrap_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Cuped_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            dataset_id = kwargs.get("dataset_id")
            if not dataset_id:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user=request.user, id=int(dataset_id))
            dataset_data = model_to_dict(dataset)

            alpha = dataset_data.get("alpha")
            beta = dataset_data.get("beta")
            alpha = alpha if alpha is not None else 0.05
            beta = beta if beta is not None else 0.2

            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Test/control columns not in dataset columns")

            history_file = request.FILES.get('file')
            if not history_file:
                raise ValueError("History file not provided")
            history_col = request.POST.get('column_name')
            if not history_col:
                raise ValueError("Column name for historical data not provided")

            history_data_buf = io.BytesIO(history_file.read())
            dataset_buf = download_dataset(dataset)
            if not dataset_buf:
                raise ValueError("Could not download the dataset")

            result_df = handlers.cuped(
                filepath_or_buffer=dataset_buf,
                test_column=test_column,
                control_column=control_column,
                history_buf=history_data_buf,
                alpha=alpha,
                beta=beta,
                history_col=history_col,
            )
            if result_df is None:
                raise ValueError("Error while conducting CUPED")

            csv_buffer = io.StringIO()
            result_df.to_csv(csv_buffer, index=False)
            byte_buffer = io.BytesIO(csv_buffer.getvalue().encode("utf-8"))

            response = requests.put(
                url=dataset.url,
                data=byte_buffer.getvalue(),
                headers={
                    "Authorization": f"Bearer {CLOUD_API_KEY}",
                    "Content-Type": "text/csv"
                }
            )
            response.raise_for_status()
            return Response({"status": 200, "success": True})
        except Exception as e:
            local_exception_handler(e)
            return Response({"status": 500, "error": str(e)})


class ANOVA_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        load_dotenv()
        try:
            dataset_id = (kwargs.get("dataset_id"))
            if CACHE:
                res = cache.get(f"anova_user_{self.request.user.id}_dataset_{dataset_id}")
                if res:
                    return Response(res)
            if dataset_id:
                dataset_id = int(dataset_id)
            else:
                raise ValueError("Invalid dataset id given")

            dataset = Dataset.objects.get(user = self.request.user, id = dataset_id)
            if not dataset:
                raise NotFound("Corresponding dataset was not found")
            
            dataset_data = model_to_dict(dataset)
            if not dataset_data:
                raise NotFound("Could not transform dataset indo dictionary")

            alpha = dataset_data.get("alpha") or 0.05
            beta = dataset_data.get("beta") or 0.2
            columns = dataset_data.get("columns")
            test_column = dataset_data.get("test")
            control_column = dataset_data.get("control")

            if not columns or not test_column or not control_column:
                raise ValueError("Could not get appropriate test and control column names")
            if test_column not in columns or control_column not in columns:
                raise ValueError("Could not get appropriate test and control column names")
            buffer = download_dataset(dataset)
            if not buffer:
                raise ValueError("Could not download the dataset")
            result = handlers.anova(
                filepath_or_buffer = buffer,
                test_column = test_column,
                control_column = control_column,
                alpha=alpha,
                beta=beta,
            )
            if CACHE:
                cache.set(
                    f"anova_user_{self.request.user.id}_dataset_{dataset_id}",
                    result[1]
                )
            return result[0]

        except Exception as e:
            local_exception_handler(e)

