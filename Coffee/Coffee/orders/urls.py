from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('delete/<int:pk>/', views.order_delete, name='order_delete'),
    path('<int:pk>/toggle-status/', views.order_toggle_status, name='order_toggle_status'),
    path('<int:pk>/invoice/', views.order_invoice, name='order_invoice'),
    path('create-from-customer/', views.create_order_from_customer, name='create_order_from_customer'),
    path('api/list/', views.order_list_api, name='order_list_api'),
    path('api/<int:pk>/', views.order_detail_api, name='order_detail_api'),
    path('api/<int:pk>/complete/', views.order_complete_api, name='order_complete_api'),
    path('api/<int:pk>/cancel/', views.order_cancel_api, name='order_cancel_api'),
    path('api/my/', views.my_orders_api, name='my_orders_api'),
]
