from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("", views.APIRootView.as_view()),
    path("auth/register/", views.RegisterView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", views.MeView.as_view()),
    path("entries/", views.TimeEntryListCreateView.as_view()),
    path("entries/<int:pk>/", views.TimeEntryDetailView.as_view()),
    path("categories/", views.EntryCategoryListCreateView.as_view()),
    path("categories/<int:pk>/", views.EntryCategoryDetailView.as_view()),
    path("pto/", views.PTOEntryListCreateView.as_view()),
    path("pto/summary/", views.PTOSummaryView.as_view()),
    path("pto/<int:pk>/", views.PTOEntryDetailView.as_view()),
    path("settings/pto-policy/", views.PTOPolicyView.as_view()),
    path("import-backup/", views.ImportBackupView.as_view()),
    path("export-backup/", views.ExportBackupView.as_view()),
]
