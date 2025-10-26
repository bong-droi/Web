from django.urls import path
from . import views

urlpatterns = [
    path('', views.shift_list, name='shift_list'),
    path('create/', views.shift_create, name='shift_create'),
    path('update/<int:pk>/', views.shift_update, name='shift_update'),
    path('delete/<int:pk>/', views.shift_delete, name='shift_delete'),
    path('detail/<int:pk>/', views.shift_detail, name='shift_detail'),
    path('assign/', views.assign_shift, name='assign_shift'),
    path('register/', views.shift_register, name='shift_register'),
    path('my/', views.my_shifts, name='my_shifts'),
    path('swap/', views.swap_request, name='swap_request'),
    path('swap/<int:pk>/<str:action>/', views.swap_respond, name='swap_respond'),
]
