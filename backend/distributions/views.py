from rest_framework.views import APIView
from backend.authentication import TelegramAuthentication
from rest_framework.permissions import IsAuthenticated

import logging
import json
import os
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.http import HttpResponseBadRequest, JsonResponse

from rest_framework import status
from rest_framework.response import Response

from rest_framework.exceptions import bad_request

from api.models import Distribution, Dataset

from api.serializers import (
    DistributionSerializer,
    DatasetSerializer
)

from backend.authentication import TelegramAuthentication

from rest_framework.response import Response

from rest_framework.views import APIView

from django.http import HttpResponse

from kafka_broker.utils import build_log_message

from django.core.cache import cache

from django.forms.models import model_to_dict

from . import handlers

from dotenv import load_dotenv

load_dotenv()


CACHE = os.getenv("CACHE")
if not CACHE or CACHE.lower() in ("false", 0, "0", "no"):
    CACHE = False
else:
    CACHE = True


class AuthenticatedAPIView:
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]


class PlotView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_plot_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.plot_distribution(distribution = distribution)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_plot_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)



class ProbabilityView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        a = request.data.get("value")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_probability_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.get_probability(distribution = distribution, a = a)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_probability_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)


class IntervalView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        a = request.data.get("a")
        b = request.data.get("b")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_interval_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.get_interval(distribution = distribution, a = a, b = b)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_interval_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)


class QuantileView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        quantile = request.data.get("quantile")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_quantile_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.get_quantile(distribution = distribution, quantile=quantile)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_quantile_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)


class PercentileView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        percentile = request.data.get("percentile")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_quantile_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.get_quantile(distribution = distribution, quantile=percentile/100)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_quantile_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)


class SampleView(AuthenticatedAPIView, APIView):
    def post(self, request, *args, **kwargs):
        distribution_id = kwargs.get("id")
        n = request.data.get("n")
        if CACHE:
            cached = cache.get(key=f"distribution_{distribution_id}_quantile_{request.user.id}")
            if cached:
                return Response(cached)
        try:
            distribution = model_to_dict(Distribution.objects.get(pk=distribution_id, user=request.user))
            dist_params = (distribution.get("distribution_parameters"))
            dist_type = distribution.get("distribution_type")
            if not dist_type or not dist_params:
                raise ValueError("Invalid or empty data given")
            dist_params = json.loads(dist_params)

            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action="get_distribution_plot",
                request_method=request.method,
                response_code=200,
                request_body= request.data,
            )

            result = handlers.get_sample(distribution = distribution, n = n)

            if CACHE:
                cache.set(
                    key=f"distribution_{distribution_id}_quantile_{request.user.id}",
                    value=result[1]
                )
            
            return result[0]

        except Exception as e:
            logging.error("An error occured while generating plot image")
            logging.exception(e)
