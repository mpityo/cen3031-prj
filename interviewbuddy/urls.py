from django.urls import path

from .views import LoginView, RegisterView, home_view

urlpatterns = [
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('', home_view, name='home'),
    path('home/', home_view, name='home')
]
