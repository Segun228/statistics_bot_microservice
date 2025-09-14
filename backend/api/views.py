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


class LoggingRetrieveUpdateDestroyModelAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    View с логированием CRUD операций.
    """
    def log_crud_action(self, request, response, action):
        try:
            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=request.user.telegram_id,
                user_id=request.user.id,
                action=action,
                request_method=request.method,
                response_code=response.status_code,
                request_body=getattr(request, "data", None),
            )
        except Exception as e:
            logging.error(f"Failed to log action {action}: {e}")

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        self.log_crud_action(request, response, "retrieve_model")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.log_crud_action(request, response, "update_model")
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self.log_crud_action(request, response, "partial_update_model")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.log_crud_action(request, response, "destroy_model")
        return response

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LoggingListCreateModelAPIView(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              generics.GenericAPIView):
    """
    List or create view with logging
    """
    def log_crud_action(self, request, response, action, serializer=None):
        try:
            build_log_message(
                is_authenticated=request.user.is_authenticated,
                telegram_id=getattr(request.user, "telegram_id", None),
                user_id=request.user.id,
                action=action,
                request_method=request.method,
                response_code=response.status_code,
                request_body=request.data,
            )
        except Exception as e:
            logging.error(f"Failed to log action {action}: {e}")

    def get(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        self.log_crud_action(request, response, action="list_model")
        return response

    def post(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        self.log_crud_action(request, response, serializer=serializer, action="create_model")
        return response


class AuthenticatedAPIView:
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]


class DistributionListCreateAPIView(AuthenticatedAPIView, LoggingListCreateModelAPIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DistributionSerializer

    def get_queryset(self):
        return Distribution.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        load_dotenv()

        request = self.request
        try:
            user= request.user
            serializer.save(user=user)
        except Exception as e:
            logging.error(e)
            raise



class DistributionRetrieveUpdateDestroyAPIView(AuthenticatedAPIView, LoggingRetrieveUpdateDestroyModelAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'distribution_id'

    def get_queryset(self):
        return Distribution.objects.filter(user=self.request.user)

    serializer_class = DistributionSerializer


class DatasetListCreateAPIView(AuthenticatedAPIView, LoggingListCreateModelAPIView):

    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DatasetSerializer

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        load_dotenv()
        request = self.request
        CLOUD_URL = os.getenv("CLOUD_URL")
        CLOUD_UPLOAD_URL = os.getenv("CLOUD_UPLOAD_URL")
        CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
        
        if not CLOUD_URL or not CLOUD_API_KEY or not CLOUD_UPLOAD_URL:
            logging.exception("Missing env required fields")
            raise ValueError("Missing env required fields")
        
        csv_file = request.FILES.get("file")
        if not csv_file:
            logging.exception("Empty request received")
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Empty CSV file received")
        

        dataset = serializer.save(user=request.user, url=None, columns=None)
        try:
            buffer = BytesIO()
            for chunk in csv_file.chunks():
                buffer.write(chunk)
            buffer.seek(0)

            df = pd.read_csv(buffer)
            df.dropna()
            records = df.shape[0]
            buffer = BytesIO(df)
            
            response = requests.put(
                url=CLOUD_UPLOAD_URL + str(uuid.uuid4()),
                data=buffer.getvalue(),
                headers={
                    "Authorization": f"Bearer {CLOUD_API_KEY}",
                    "Content-Type": "text/csv"
                }
            )
            response.raise_for_status()
            
            key = response.json().get("Key")
            if not key:
                raise ValueError("Cloud did not return a file key")

            buffer.seek(0)
            columns = list(pd.read_csv(buffer).columns)

            dataset.url = CLOUD_URL + key
            dataset.columns = columns
            dataset.length = records
            dataset.user=request.user
            dataset.save()

        except Exception as e:
            logging.error(e)
            dataset.delete()
            raise



class DatasetRetrieveUpdateDestroyAPIView(AuthenticatedAPIView, LoggingRetrieveUpdateDestroyModelAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'dataset_id'

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)

    serializer_class = DatasetSerializer