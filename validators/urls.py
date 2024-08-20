from django.urls import path
from .views import availablevalidators, validate, EditValidator, EditAssociatedValidator

urlpatterns = [
    path('getlistofavailablevalidators/', availablevalidators.as_view(), name='availablevalidators'),
    path('validate/', validate.as_view(), name='validate'),
    path('editvalidate/', EditValidator.as_view(), name='editvalidate'),
    path('editassociatedvalidate/', EditAssociatedValidator.as_view(), name='editassociatedvalidate'),
]

