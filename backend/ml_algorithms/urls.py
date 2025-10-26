from django.urls import path
from .views import ML_model_Predict_APIView, ML_model_ListCreateAPIView, ML_model_fit_APIView, ML_model_RetrieveUpdateDestroyAPIView, ML_models_ListAPIView, ML_models_get_ListAPIView, ML_models_get_RetrieveAPIView

urlpatterns = [
    path("model-create/", ML_model_ListCreateAPIView.as_view()),
    path("model-fit/<int:model_id>/", ML_model_fit_APIView.as_view()),
    path("model-predict/<int:model_id>/", ML_model_Predict_APIView.as_view()),
    path("model-refit/<int:model_id>/", ML_model_RetrieveUpdateDestroyAPIView.as_view()),
    path("get_models/", ML_models_ListAPIView.as_view()),
    path("model/<int:model_id>/", ML_models_get_RetrieveAPIView.as_view()),
    path("model/", ML_models_get_ListAPIView.as_view())
]

