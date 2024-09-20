from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate/', views.generate_schedule, name='generate_schedule'),
    path('view/', views.view_schedule, name='view_schedule'),
    path('results/', views.view_results, name='view_results'),
    path('preferences/', views.employee_preferences, name='employee_preferences'),
    path('generate-shifts/', views.generate_shifts, name='generate_shifts'),
]