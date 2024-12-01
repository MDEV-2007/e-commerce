from django.urls import path
from store import views


app_name = 'vendor'

urlpatterns = [
    path('', views.index),

]


