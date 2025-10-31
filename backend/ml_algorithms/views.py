import zipfile
from .models import ML_Model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse

from ml_algorithms.model_handlers.base import (
    BaseMLModel
)


from ml_algorithms.model_handlers.regression import (
    LinearRegressionModel
)

from ml_algorithms.model_handlers.factory import get_model


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
import joblib

from ml_algorithms.model_handlers.factory import get_class

load_dotenv()

from rest_framework.generics import RetrieveUpdateDestroyAPIView


def decode_bool(val)->bool:
    if type(val) is bool:
        return val
    elif not val:
        return False
    elif str(val) in ("true", "t", "tr", "1", "y", "yes"):
        return True
    else:
        return False



def rewrite_supabase_url_to_root(upload_url: str) -> str:
    filename = upload_url.rstrip("/").split("/")[-1]
    pattern = r"(https://[^/]+/storage/v1/object)/public/([^/]+)/.+"
    replacement = r"\1/\2/" + filename
    clean_url = re.sub(pattern, replacement, upload_url)
    return clean_url

CLOUD_UPLOAD_URL = os.getenv("CLOUD_UPLOAD_URL")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY", "KEY")
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
        

        model = serializer.save(
            user=request.user, 
            get_url="", 
            post_url="",
            features=[]
        )
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
            drop_features = decode_bool(request.POST.get("drop_reatures", False))

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
            )
            model_object, resp, img_zip = model_object.fit(
                df = df,
                drop_features=drop_features
            )

            final_features = model_object.get_features()

            if not CLOUD_UPLOAD_URL or CLOUD_UPLOAD_URL is None:
                raise Exception("No .env CLOUD_UPLOAD_URL provided")
            clean_url = (CLOUD_UPLOAD_URL.rstrip("/") + "/" + str(uuid.uuid4())).strip()
            clean_url = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', clean_url)

            response = requests.put(
                url=clean_url,
                data=model_object.save(),
                headers={
                    "Authorization": f"Bearer {CLOUD_API_KEY}",
                    "Content-Type": "application/octet-stream",
                }
            )
            response.raise_for_status()
            
            key = response.json().get("Key")
            if key and "statistics-bot-bucket/" in key:
                key = key.replace("statistics-bot-bucket/", "")
            if not key:
                raise ValueError("Cloud did not return a file key")

            buffer.seek(0)

            model.get_url = CLOUD_URL + key
            model.post_url = rewrite_supabase_url_to_root(CLOUD_URL + key)
            model.features = final_features
            model.save()
            """
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                if img_zip and img_zip is not None:
                    zip_file.writestr('images.zip', img_zip.getvalue())
                if resp and resp is not None:
                    zip_file.writestr('fit_result.json', json.dumps(resp))
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="prediction_results.zip"'
            return response
        """
        except Exception as e:
            model.delete()
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



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

    def post(self, request, *args, **kwargs):
        model_id = int(self.kwargs.get('model_id'))
        model = self.get_queryset().filter(id=model_id).first()
        
        if not model:
            return Response({"error": "Model not found", "status":404}, status=404)
        
        get_url = model.get_url
        if not get_url:
            return Response({"error": "No model URL found"}, status=400)
        try:
            response = requests.get(get_url)
            response.raise_for_status()
            sklearn_ml_model = joblib.load(BytesIO(response.content))
            if not model.features:
                raise Exception("Could not reach model`s features")
            ml_model = get_class(model.type).reborn(
                target_column=model.target,
                feature_columns=model.features,
                model = sklearn_ml_model,
                processed_feature_names=model.features
            )
        except Exception as e:
            logging.error(f"Model loading failed: {e}")
            return Response({"error": "Failed to load model"}, status=500)
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({"error": "CSV file is required"}, status=400)
        
        try:
            buffer = BytesIO()
            for chunk in csv_file.chunks():
                buffer.write(chunk)
            buffer.seek(0)
            df = pd.read_csv(buffer)

            try:
                df_selected = df[model.features].copy()
            except KeyError as e:
                return Response({"error": f"Feature selection failed: {e}"}, status=400)

            try:
                for col in df_selected.columns:
                    if df_selected[col].dtype == 'object':
                        df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                df_clean = df_selected.dropna()
                
                if len(df_clean) == 0:
                    return Response({"error": "No valid numeric data after cleaning"}, status=400)

            except Exception as e:
                return Response({"error": f"Data type conversion failed: {e}"}, status=400)


        except Exception as e:
            logging.error(f"CSV processing failed: {e}")
            return Response({"error": "Invalid CSV file"}, status=400)

        try:
            _, result, img_zip = ml_model.predict(df)
            predictions_df = result
            buffer = BytesIO()
            predictions_df.to_csv(buffer, index=False)
            buffer.seek(0)
            from django.http import HttpResponse

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                if buffer and buffer is not None:
                    zip_file.writestr('predictions.csv', buffer.getvalue())
                if img_zip and img_zip is not None:
                    zip_file.writestr('images.zip', img_zip.getvalue())
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="prediction_results.zip"'
            return response

        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            return Response({"error": f"Prediction failed: {str(e)}"}, status=500)


class ML_model_fit_APIView(AuthenticatedAPIView, APIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def post(self, request, *args, **kwargs):
        try:
            model_id = int(self.kwargs.get('model_id'))
            model = self.get_queryset().filter(id=model_id).first()
            
            if not model:
                return Response({"error": "Model not found", "status":404}, status=404)
            
            get_url = model.get_url
            if not get_url:
                return Response({"error": "No model URL found"}, status=400)
            try:
                response = requests.get(get_url)
                response.raise_for_status()
                sklearn_ml_model = joblib.load(BytesIO(response.content))
                if not model.features:
                    raise Exception("Could not reach model`s features")
                ml_model = get_class(model.type).reborn(
                    target_column=model.target,
                    feature_columns=model.features,
                    model = sklearn_ml_model,
                    processed_feature_names=model.features
                )
            except Exception as e:
                logging.error(f"Model loading failed: {e}")
                return Response({"error": "Failed to load model"}, status=500)
            csv_file = request.FILES.get("file")
            if not csv_file:
                return Response({"error": "CSV file is required"}, status=400)
            
            try:
                buffer = BytesIO()
                for chunk in csv_file.chunks():
                    buffer.write(chunk)
                buffer.seek(0)
                df = pd.read_csv(buffer)

                try:
                    df_selected = df[model.features].copy()
                except KeyError as e:
                    return Response({"error": f"Feature selection failed: {e}"}, status=400)

                try:
                    for col in df_selected.columns:
                        if df_selected[col].dtype == 'object':
                            df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                    df_clean = df_selected.dropna()
                    
                    if len(df_clean) == 0:
                        return Response({"error": "No valid numeric data after cleaning"}, status=400)

                except Exception as e:
                    return Response({"error": f"Data type conversion failed: {e}"}, status=400)


            except Exception as e:
                logging.error(f"CSV processing failed: {e}")
                return Response({"error": "Invalid CSV file"}, status=400)

            try:
                new_model, result, img_zip = ml_model.fit(
                    df,
                    drop_features=False
                )
                res = ml_model.get_best_gridsearch_params()
                if res is not None and res and result:
                    result = res | result

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    predictions_str = json.dumps(result, indent=2)
                    zip_file.writestr('predictions.json', predictions_str)
                    if img_zip:
                        zip_file.writestr('images.zip', img_zip.read())
                zip_buffer.seek(0)
                return HttpResponse(
                    zip_buffer.getvalue(),
                    content_type='application/zip',
                    headers={'Content-Disposition': 'attachment; filename="ml_results.zip"'}
                )
            except Exception as e:
                logging.error(f"Prediction failed: {e}")
                return Response({"error": f"Prediction failed: {str(e)}"}, status=500)
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ML_models_ListAPIView(AuthenticatedAPIView, APIView):
    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def post(self, request, *args, **kwargs):
        try:
            task = request.POST.get("task")

            if task:
                queryset = self.get_queryset().filter(task=task)
                logging.debug(f"🔍 AFTER TASK FILTER: {queryset.count()}")

            for model in queryset:
                logging.debug(f"🔍 MODEL: {model.id}, {model.name}, {model.task}, {model.type}")

            serializer = ML_ModelSerializer(queryset, many=True)
            logging.debug(f"🔍 SERIALIZED DATA: {serializer.data}")
            return Response(data=serializer.data)
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ML_models_RefitAPIView(AuthenticatedAPIView, APIView):    
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def post(self, request, *args, **kwargs):
        try:
            model_id = int(self.kwargs.get('model_id'))
            model = self.get_queryset().filter(id=model_id).first()
            
            if not model:
                return Response({"error": "Model not found", "status":404}, status=404)
            
            get_url = model.get_url
            if not get_url:
                return Response({"error": "No model URL found"}, status=400)
            try:
                response = requests.get(get_url)
                response.raise_for_status()
                sklearn_ml_model = joblib.load(BytesIO(response.content))
                if not model.features:
                    raise Exception("Could not reach model`s features")
                ml_model = get_class(model.type).reborn(
                    target_column=model.target,
                    feature_columns=model.features,
                    model = sklearn_ml_model,
                    processed_feature_names=model.features
                )
            except Exception as e:
                logging.error(f"Model loading failed: {e}")
                return Response({"error": "Failed to load model"}, status=500)
            csv_file = request.FILES.get("file")
            if not csv_file:
                return Response({"error": "CSV file is required"}, status=400)
            
            try:
                buffer = BytesIO()
                for chunk in csv_file.chunks():
                    buffer.write(chunk)
                buffer.seek(0)
                df = pd.read_csv(buffer)

                try:
                    df_selected = df[model.features].copy()
                except KeyError as e:
                    return Response({"error": f"Feature selection failed: {e}"}, status=400)

                try:
                    for col in df_selected.columns:
                        if df_selected[col].dtype == 'object':
                            df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
                    df_clean = df_selected.dropna()
                    
                    if len(df_clean) == 0:
                        return Response({"error": "No valid numeric data after cleaning"}, status=400)

                except Exception as e:
                    return Response({"error": f"Data type conversion failed: {e}"}, status=400)

            except Exception as e:
                logging.error(f"CSV processing failed: {e}")
                return Response({"error": "Invalid CSV file"}, status=400)

            try:
                new_model, result, img_zip = ml_model.refit(df)

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    predictions_str = json.dumps(result, indent=2)
                    zip_file.writestr('predictions.json', predictions_str)
                    if img_zip:
                        zip_file.writestr('images.zip', img_zip.read())
                zip_buffer.seek(0)
                return HttpResponse(
                    zip_buffer.getvalue(),
                    content_type='application/zip',
                    headers={'Content-Disposition': 'attachment; filename="ml_results.zip"'}
                )
            except Exception as e:
                logging.error(f"Prediction failed: {e}")
                return Response({"error": f"Prediction failed: {str(e)}"}, status=500)
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ML_models_get_ListAPIView(AuthenticatedAPIView, APIView):

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response(data=serializer.data)
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ML_models_get_RetrieveAPIView(AuthenticatedAPIView, RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    lookup_url_kwarg = 'model_id'

    def get_queryset(self):
        return ML_Model.objects.filter(user=self.request.user)

    serializer_class = ML_ModelSerializer

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
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            return Response(
                {"error": f"Internal server error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )