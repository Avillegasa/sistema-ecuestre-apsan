from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Usuarios
    path('me/', views.UserDetailView.as_view(), name='user_detail'),
    path('', views.UserListView.as_view(), name='user_list'),
    
    # Jueces
    path('judges/', views.JudgeListView.as_view(), name='judge_list'),
    path('judges/<int:pk>/', views.JudgeDetailView.as_view(), name='judge_detail'),
]