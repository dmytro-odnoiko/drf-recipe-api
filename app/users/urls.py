"""
URL mappings for the user API
"""
from django.urls import path

from users import views

app_name = 'user'

urlpatterns = [
    path('', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
]
