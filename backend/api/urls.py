from django.urls import path
from . import views

urlpatterns = [
    path("distributions/", views.DistributionListCreateAPIView.as_view(), name="distributions_list_create_endpoint"),
    path("distributions/<int:distribution_id>/", views.DistributionRetrieveUpdateDestroyAPIView.as_view(), name="distributions_retrieve_update_destroy_endpoint"),
    path("datasets/", views.DatasetListCreateAPIView.as_view(), name="datasets_list_create_endpoint"),
    path("datasets/<int:dataset_id>/", views.DatasetRetrieveUpdateDestroyAPIView.as_view(), name="datasets_retrieve_update_destroy_endpoint"),
]