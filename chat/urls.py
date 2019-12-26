# chat/urls.py
from django.urls import path

from . import views
app_name = 'chat'

urlpatterns = [
    path('<str:room_name>/', views.index2, name='index'),
]