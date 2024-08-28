from django.urls import path
from . import views

urlpatterns = [
    path('auth/sign-in', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    path('dashboard', views.dashboard.as_view(), name='dashboard'),
    path('getauthkey', views.getauthkey.as_view(), name='getauthkey'),
    path('exchange-code/', views.exchange_code_for_token, name='exchange_code_for_token'),

]
