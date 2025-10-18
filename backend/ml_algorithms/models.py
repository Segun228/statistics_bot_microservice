from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import User

task_choices = (
    ('regression', 'Regression'),
    ('classification', 'Classification'),
    ('clusterization', 'Clusterization'),
)


type_choices = (
    ('linear_regression', 'Linear Regression'),
    ('polinomial_regression', 'Polinomial Regression'),
    ('knn_regression', 'KNN Regression'),
    ('gradient_boosting_regression', 'Gradient Boosting Regression'),

    ('logistic_regression', 'Logistic Regression'),
    ('support_vector_machine_classification', 'SVM Classification'),
    ('knn_classification', 'KNN Classification'),
    ('random_forest_classification', 'Random Forest Classification'),
    ('gradient_boosting_classification', 'Gradient Boosting Regression'),

    ('kmeans_clusterization', 'KMeans clusterization'),
    ('density_clusterization', 'Density clusterization'),
)



class ML_Model(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ml_models")
    name = models.CharField(max_length=100, null=False, blank=False, default="Модель")
    description = models.CharField(max_length=100, null=False, blank=False, default="Описание модели")
    task = models.CharField(
        max_length=100,
        choices=task_choices,
        default="regression",
    )
    type = models.CharField(
        max_length=100,
        choices=type_choices,
        default="linear",
    )
    features = ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True)
    target = models.CharField(max_length=200, null=False, blank=False)
    get_url = models.URLField(max_length=1000, null=True, blank=True, default="")
    post_url = models.URLField(max_length=1000, null=True, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'Модель машинного обучения'
        verbose_name_plural = 'Модели машинного обучения'

