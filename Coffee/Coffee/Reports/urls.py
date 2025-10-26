from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('salary/', views.salary_report, name='salary_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('shifts/', views.shift_report, name='shift_report'),
]
