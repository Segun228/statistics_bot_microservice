from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

DISTRIBUTION_CHOICES = [
    ("normal", "Normal (Нормальное)"),
    ("binomial", "Binomial (Биномиальное)"),
    ("poisson", "Poisson (Пуассон)"),
    ("uniform", "Uniform (Равномерное)"),
    ("exponential", "Exponential (Экспоненциальное)"),
    ("beta", "Beta (Бета)"),
    ("gamma", "Gamma (Гамма)"),
    ("lognormal", "Log-normal (Лог-нормальное)"),
    ("chi2", "Chi-squared (Хи-квадрат)"),
    ("t", "Student t (Стьюдента)"),
    ("f", "F-distribution (Фишера)"),
    ("geometric", "Geometric (Геометрическое)"),
    ("hypergeom", "Hypergeometric (Гипергеометрическое)"),
    ("negative_binomial", "Negative Binomial (Отрицательно биномиальное)"),
]

class Distribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="distributions")
    name = models.CharField(max_length=100, null=False, blank=False, default="Распределение")
    description = models.CharField(max_length=1000, null=True, blank=True, default="Описание распределения")
    distribution_type = models.CharField(max_length=1000, null=False, blank=False, default="normal", choices=DISTRIBUTION_CHOICES,)
    distribution_parameters = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="datasets")
    name = models.CharField(max_length=100, null=False, blank=False, default="Датасет")
    columns = ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True)
    url = models.URLField(max_length=1000, null=True, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    alpha = models.FloatField(null=False, blank=False, default=0.05)
    beta = models.FloatField(null=False, blank=False, default=0.2)

    test = models.CharField(default="",max_length=100)
    control = models.CharField(default="",max_length=100)

    length = models.IntegerField(default=0)
    class Meta:
        verbose_name = 'модель юнит-экономики'
        verbose_name_plural = 'модели юнит-экономики'


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
