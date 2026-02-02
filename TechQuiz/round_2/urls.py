from django.urls import path
from . import views

urlpatterns = [
    path('', views.round_2_view, name='round_2'),
]
