from django.urls import path
from . import views

urlpatterns = [
    path('supplies/', views.supply_list, name='supply_list'),
    path('supplies/create/', views.supply_create, name='supply_create'),
    path('supplies/update/<int:pk>/', views.supply_update, name='supply_update'),
    path('supplies/delete/<int:pk>/', views.supply_delete, name='supply_delete'),

    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),

    path('damages/', views.damage_list, name='damage_list'),
    path('damages/create/', views.damage_create, name='damage_create'),
]
