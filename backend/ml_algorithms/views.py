
from .models import ML_Model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import ML_ModelSerializer

from api.permissions import IsAdminOrDebugOrReadOnly

from backend.authentication import TelegramAuthentication

from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import logging

from kafka_broker.utils import build_log_message

from rest_framework.response import Response
from rest_framework import mixins, generics

from django.core.cache import cache
from dotenv import load_dotenv

from django.http import HttpResponseBadRequest

from .model_handlers.factory import get_model

import os
import requests
import pandas as pd
import uuid
from io import BytesIO
import re
import json
load_dotenv()

def rewrite_supabase_url_to_root(upload_url: str) -> str:
    filename = upload_url.rstrip("/").split("/")[-1]
    pattern = r"(https://[^/]+/storage/v1/object)/public/([^/]+)/.+"
    replacement = r"\1/\2/" + filename
    clean_url = re.sub(pattern, replacement, upload_url)
    return clean_url

CLOUD_UPLOAD_URL = os.getenv("CLOUD_UPLOAD_URL")
CLOUD_API_KEY = os.getenv("CLOUD_UPLOAD_URL", "KEY")
CLOUD_URL = os.getenv("CLOUD_URL")

if not CLOUD_UPLOAD_URL or CLOUD_UPLOAD_URL is None:
    raise Exception("No .env CLOUD_UPLOAD_URL provided")
if not CLOUD_API_KEY or CLOUD_API_KEY is None:
    raise Exception("No .env CLOUD_API_KEY provided")
if not CLOUD_URL or CLOUD_URL is None:
    raise Exception("No .env CLOUD_URL provided")

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



class ML_model_ListCreateAPIView(AuthenticatedAPIView, LoggingListCreateModelAPIView):
    authentication_classes = [TelegramAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ML_ModelSerializer

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)
    
    CLOUD_URL = os.getenv("CLOUD_URL")
    CLOUD_UPLOAD_URL = os.getenv("CLOUD_UPLOAD_URL")
    CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
        
    if not CLOUD_URL or not CLOUD_API_KEY or not CLOUD_UPLOAD_URL:
        logging.exception("Missing env required fields")
        raise ValueError("Missing env required fields")

    def perform_create(self, serializer):
        request = self.request
        
        csv_file = request.FILES.get("file")
        if not csv_file:
            logging.exception("Empty request received")
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Empty CSV file received")
        

        model = serializer.save(user=request.user, url=None, columns=None)
        try:
            buffer = BytesIO()
            for chunk in csv_file.chunks():
                buffer.write(chunk)
            buffer.seek(0)

            df = pd.read_csv(buffer)
            df.dropna()

            model.name = request.POST.get("name", "Undefined model")
            
            model.task = request.POST.get("task", "regression")
            model.type = request.POST.get("type", "linear_regression")

            model.description = request.POST.get("description", f"{model.task} undefined {model.type} model")
            request_features = request.POST.get("features")
            request_target = request.POST.get("target")

            if not request_features or not request_target:
                raise ValueError("Feature and target fields are required")

            try:
                if isinstance(request_features, str):
                    user_features = json.loads(request_features)
                elif isinstance(request_features, list):
                    user_features = request_features
                else:
                    raise Exception({"features": "Must be a list or JSON string"})
            except json.JSONDecodeError:
                raise Exception({"features": "Invalid JSON format"})

            model.target = request_target

            model_object = get_model(
                model_type=model.type,
                feature_columns= user_features,
                target_column= request_target,
                df = df
            )


            final_features = model_object.get_features()

# sending ready model to the cloud
            if not CLOUD_UPLOAD_URL or CLOUD_UPLOAD_URL is None:
                raise Exception("No .env CLOUD_UPLOAD_URL provided")
            response = requests.put(
                url=CLOUD_UPLOAD_URL + str(uuid.uuid4()),
                data=model_object.save(),
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

            model.get_url = CLOUD_URL + key
            model.post_url = rewrite_supabase_url_to_root(CLOUD_URL + key)
            model.features = final_features
            model.save()

        except Exception as e:
            logging.error(e)
            model.delete()
            raise



class ML_model_RetrieveUpdateDestroyAPIView(AuthenticatedAPIView, LoggingRetrieveUpdateDestroyModelAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer



class ML_model_Predict_APIView(AuthenticatedAPIView, APIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer



class ML_model_Teach_APIView(AuthenticatedAPIView, APIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer



class ML_models_ListAPIView(AuthenticatedAPIView, APIView):

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def get(self, request, *args, **kwargs):
        task = request.GET.get("task")
        type = request.GET.get("type")
        
        queryset = self.get_queryset()
        
        if task:
            queryset = queryset.filter(task=task, type=type)
        if type:
            queryset = queryset.filter(type=type)
        
        serializer = self.serializer_class(queryset, many=True)
        return Response(data=serializer.data)


class ML_models_get_ListAPIView(AuthenticatedAPIView, APIView):

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(data=serializer.data)



class ML_models_get_RetrieveAPIView(AuthenticatedAPIView, APIView):
    
    def get(self, request, model_id, *args, **kwargs):
        try:
            instance = ML_Model.objects.get(id=model_id, user=request.user)
            
            serializer = ML_ModelSerializer(instance)
            return Response(data=serializer.data)
            
        except ML_Model.DoesNotExist:
            return Response(
                {"error": "Model not found or access denied"}, 
                status=status.HTTP_404_NOT_FOUND
            )