from django.contrib import admin
from django.urls import path
from account import views

urlpatterns = [
    path('register', views.UserRegistrationView.as_view()),
    path('login', views.UserLoginView.as_view()),
    path('profile', views.UserProfileView.as_view()),
    path('change-password', views.UserChangePasswordView.as_view()),
    path('send-reset-password-email', views.SendPasswordResetEmailView.as_view()),
    path('reset-password/<uid>/<token>', views.UserPasswordResetView.as_view())
]