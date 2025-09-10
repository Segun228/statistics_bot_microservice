import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
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

from rest_framework.response import Response
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

load_dotenv()

class AuthenticatedAPIView:
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]


logger = logging.getLogger(__name__)

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
        try:
            dataset_id = (kwargs.get("dataset_id"))
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
            
            response = 

        except Exception as e:
            local_exception_handler(e)


class SampleSizeView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass




class Z_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class T_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Chi_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Chi_2Sample_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class KS_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class KS_2Sample_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class U_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Lilleforce_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Shap_Wilke_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Welch_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Anderson_Darling_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


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
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class ANOVA_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass


class Regression_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            local_exception_handler(e)
        finally:
            pass
