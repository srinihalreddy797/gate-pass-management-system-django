from django.urls import path

from .views import (
    AdminDashboardView,
    ApplyPassView,
    CustomLoginView,
    CustomLogoutView,
    DashboardRedirectView,
    HomeRedirectView,
    LogActionView,
    PassListView,
    PassStatusUpdateView,
    SecurityDashboardView,
    SignUpView,
    UserDashboardView,
)

urlpatterns = [
    path("", HomeRedirectView.as_view(), name="home"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("dashboard/", DashboardRedirectView.as_view(), name="dashboard"),
    path("dashboard/user/", UserDashboardView.as_view(), name="user-dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("dashboard/security/", SecurityDashboardView.as_view(), name="security-dashboard"),
    path("passes/apply/", ApplyPassView.as_view(), name="apply-pass"),
    path("passes/history/", PassListView.as_view(), name="pass-list"),
    path("passes/<int:pk>/status/", PassStatusUpdateView.as_view(), name="pass-status-update"),
    path("verification/<str:pass_id>/log/", LogActionView.as_view(), name="log-action"),
]
