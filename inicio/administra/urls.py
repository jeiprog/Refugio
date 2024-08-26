from django.urls import path
from . import views


urlpatterns = [
    path('ma/', views.mas, name='masc'),

]
