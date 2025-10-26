from django.urls import path
from . import views

urlpatterns = [
    path("menu/", views.menu_list, name="list"),
    path("menu/new/", views.menu_create, name="menu_create"),
    path("menu/<int:pk>/edit/", views.menu_edit, name="menu_edit"),
    path("menu/<int:pk>/delete/", views.menu_delete, name="menu_delete"),
    
     path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    
]
