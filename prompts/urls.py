from django.urls import path
from .views import GetAllPrompts

urlpatterns = [
    path('getprompts/', GetAllPrompts.as_view(), name='getprompts'),
]

