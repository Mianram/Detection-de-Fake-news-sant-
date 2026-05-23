from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze, name='analyze'),
    path('history/', views.history, name='history'),
    path('feedback/<int:prediction_id>/', views.submit_feedback, name='submit_feedback'),
    path('api/analyze/', views.api_analyze, name='api_analyze'),
]
