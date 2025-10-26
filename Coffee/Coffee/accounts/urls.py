# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views

# urlpatterns = [
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout'),
#     path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
#     path("owner/", views.owner_frameset, name="owner_frameset"),
#     path("owner/header/", views.owner_header, name="owner_header"),
#     path("owner/home/", views.owner_home, name="owner_home"), 
#     path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),

#     # Đổi mật khẩu
#     path('password_change/', 
#          auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), 
#          name='password_change'),
#     path('password_change/done/', 
#          auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), 
#          name='password_change_done'),
    
# ]

from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),     # có sẵn hay thêm
    path("customer/", views.customer_home, name="customer_home"),
    path("customer/order/", views.customer_order_ui, name="customer_order_ui"),

    path("dashboard/staff/", views.staff_dashboard, name="staff_dashboard"),
    path("owner/", views.owner_frameset, name="owner_frameset"),
    path("owner/header/", views.owner_header, name="owner_header"),
    path("owner/home/", views.owner_home, name="owner_home"),

    path("staff/order-ui/", views.staff_order_ui, name="staff_order_ui"),

    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/role/", views.user_role, name="user_role"),
    path("users/<int:pk>/password/", views.user_password, name="user_password"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),
]

