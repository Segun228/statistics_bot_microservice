from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from django.contrib import admin
from django.urls import path, include
from users.urls import urlpatterns as auth_urls
from api.urls import urlpatterns as api_urls
from analytics.urls import urlpatterns as analitics_urls
from redis_cache.urls import urlpatterns as redis_urls
from distributions.urls import urlpatterns as dist_urls
from datasets.urls import urlpatterns as datasets_urls
from ab_tests.urls import urlpatterns as ab_tests_urls
from ml_algorithms.urls import urlpatterns as ml_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls), name="api-endpoint-group"),
    path("auth/", include(auth_urls), name="auth-endpoint-group"),
    path("analitics/", include(analitics_urls), name="analitics-endpoint-group"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("cache/", include(redis_urls), name="redis-endpoint-group"),
    path("distributions/", include(dist_urls), name="distributions-endpoint-group"),
    path("datasets/", include(datasets_urls), name="datasets-endpoint-group"),
    path("ab-tests/", include(ab_tests_urls), name="ab-tests-endpoint-group"),
    path("ml-algorithms/", include(ml_urls), name="ml-algorithms-endpoint-group"),
]
