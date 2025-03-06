from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import register_view

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('signup/', register_view, name='signup'),
    path('create_user/', views.create_user, name='create_user'),
    path('manage_roles/', views.manage_roles, name='manage_roles'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('reset_password_email/<int:user_id>/', views.reset_password_email, name='reset_password_email'),
    path('reset_password_direct/<int:user_id>/', views.reset_password_direct, name='reset_password_direct'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
]