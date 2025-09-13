from django.urls import path
from . import views

urlpatterns = [
    path("mde/<int:dataset_id>/", views.CountMDEView.as_view(), name="count_mde"),
    path("sample-size/<int:dataset_id>/", views.SampleSizeView.as_view(), name="sample_size"),

    # Тесты на сравнение двух групп
    path("z-test/<int:dataset_id>/", views.Z_TestView.as_view(), name="z_test"),
    path("t-test/<int:dataset_id>/", views.T_TestView.as_view(), name="t_test"),
    path("welch-test/<int:dataset_id>/", views.Welch_test_View.as_view(), name="welch_test"),
    path("u-test/<int:dataset_id>/", views.U_test_View.as_view(), name="u_test"),
    path("chi-square-2sample/<int:dataset_id>/", views.Chi_2Sample_TestView.as_view(), name="chi_square_2sample_test"),

    # Непараметрические тесты
    path("cramer-test/<int:dataset_id>/", views.Cramer_test_View.as_view(), name="ks_test"),
    path("ks-test-2sample/<int:dataset_id>/", views.KS_2Sample_test_View.as_view(), name="ks_test_2sample"),

    # Тесты на нормальность
    path("lilliefors-test/<int:dataset_id>/", views.Lilleforce_test_View.as_view(), name="lilliefors_test"),
    path("shapiro-wilk-test/<int:dataset_id>/", views.Shap_Wilke_test_View.as_view(), name="shapiro_wilk_test"),
    path("anderson-darling-test/<int:dataset_id>/", views.Anderson_Darling_test_View.as_view(), name="anderson_darling_test"),

    # Остальные
    path("anova/<int:dataset_id>/", views.ANOVA_View.as_view(), name="anova"),
    path("bootstrap/<int:dataset_id>/", views.Bootstrap_View.as_view(), name="bootstrap"),
    path("cuped/<int:dataset_id>/", views.Cuped_View.as_view(), name="cuped"),
]