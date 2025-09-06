from django.urls import path
from . import views

urlpatterns = [
    path("distributions", views.DistributionListCreateAPIView.as_view(), name="distributions_list_create_endpoint")
]