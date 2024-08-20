from django.urls import path
from .views import app_list, create, update_app

urlpatterns = [
    path('create_apps/', create.as_view(), name='create_apps'),
    path('get_apps/', app_list.as_view(), name='get_apps'),
    path('update_apps/', update_app.as_view(), name='update_apps'),
]

