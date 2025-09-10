from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from api.models import Distribution, Dataset
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import DistributionSerializer, DatasetSerializer

from .permissions import IsAdminOrDebugOrReadOnly

from backend.authentication import TelegramAuthentication


from rest_framework.exceptions import ValidationError
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
import pandas as pd
import uuid
from io import BytesIO
load_dotenv()
from rest_framework.views import APIView


class AuthenticatedAPIView:
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]


class SampleSizeView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class CountMDEView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Z_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class T_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Chi_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Chi_2Sample_TestView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class KS_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class KS_2Sample_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class U_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Lilleforce_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Shap_Wilke_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Welch_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Anderson_Darling_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Bootstrap_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Cuped_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class ANOVA_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass


class Regression_test_View(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        pass
