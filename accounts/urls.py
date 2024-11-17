from django.urls import path
from .views import profile, profile_detail, ProfileListView, UserUpdateView, signup
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/', UserUpdateView.as_view(), name='my_account'),
    path("profile/", profile, name="users-profile"),
    path('profile-detail/<int:pk>/', profile_detail, name='profile'),
    path("profiles/", ProfileListView.as_view(), name="users-profile-list"),
        path("signup/", signup, name="signup"),
    path(
        "login/", auth_views.LoginView.as_view(), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
