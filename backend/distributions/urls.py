from django.urls import path
from . import views


urlpatterns = [
    path("plot/<int:id>/", views.PlotView.as_view(), name="plot-endpoint"),
    path("probability/<int:id>/", views.PlotView.as_view(), name="probability-endpoint"),
    path("interval/<int:id>/", views.PlotView.as_view(), name="interval-endpoint"),
    path("quantile/<int:id>/", views.PlotView.as_view(), name="quantile-endpoint"),
    path("percentile/<int:id>/", views.PlotView.as_view(), name="percentile-endpoint"),
    path("sample/<int:id>/", views.SampleView.as_view(), name="sample-endpoint")
]