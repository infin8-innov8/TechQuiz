from django.urls import path
from . import views

urlpatterns = [
    path('', views.round_1_view, name='round_1_view'),
]
