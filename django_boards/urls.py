"""
URL configuration for django_boards project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from accounts import views as accounts_views
from boards import views

from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.BoardListView.as_view(), name="index"),
    path("signup/", accounts_views.signup, name="signup"),
    path('', include('accounts.urls')),
    # path("accounts/", include("django.contrib.auth.urls")),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(template_name="password_change.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("boards/<pk>/", views.TopicListView.as_view(), name="board_topics"),
    path("boards/<pk>/new/", views.new_topic, name="new_topic"),
    path("boards/<pk>/topics/<topic_pk>/", views.PostListView.as_view(), name="topic_posts"),
    path("boards/<pk>/topics/<topic_pk>/reply/", views.reply_topic, name="reply_topic"),
    path(
        "boards/<pk>/topics/<topic_pk>/posts/<post_pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
    path(
        "boards/<pk>/topics/<topic_pk>/posts/<post_pk>/detail/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path(
        "boards/<pk>/topics/<topic_pk>/posts/<post_pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path('avatar/', include('avatar.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
