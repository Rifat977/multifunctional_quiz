from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('reset-password/', views.reset_password, name='reset_password'),
    path('confirm-password/', views.confirm_password, name='confirm_password'),
    path('new-password/<uidb64>/<token>/', views.new_password, name='new_password'),

    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-success/', views.verification_success, name='verification_success'),
    path('verification-failed/', views.verification_failed, name='verification_failed'),

    path('profile-settings/', views.profile_setting, name="profile_settings")
]