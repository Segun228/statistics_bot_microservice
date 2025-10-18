from django.urls import path
from .views import ML_model_Predict_APIView, ML_model_ListCreateAPIView, ML_model_Teach_APIView, ML_model_RetrieveUpdateDestroyAPIView

urlpatterns = [
    path("model-create/", ML_model_ListCreateAPIView.as_view()),
    path("model-teach/<int:model_id>", ML_model_Teach_APIView.as_view()),
    path("model-predict/<int:model_id>", ML_model_Predict_APIView.as_view()),
    path("model-reteach/<int:model_id>", ML_model_RetrieveUpdateDestroyAPIView.as_view()),
]

