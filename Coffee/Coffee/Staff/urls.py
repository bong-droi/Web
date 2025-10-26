from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('update/<int:pk>/', views.staff_update, name='staff_update'),
    path('delete/<int:pk>/', views.staff_delete, name='staff_delete'),

    path('salary/', views.salary_list, name='salary_list'),
    path('salary/create/', views.salary_create, name='salary_create'),
    path('salary/update/<int:pk>/', views.salary_update, name='salary_update'),
    path('salary/delete/<int:pk>/', views.salary_delete, name='salary_delete'),
]
