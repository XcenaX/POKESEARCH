from django.urls import path
from .views import login_view, register, logout_view
from django.contrib.auth import views as auth_views
from users.forms import CustomAuthForm

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    # path('login/', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login'),
    path('logout/', logout_view, name='logout'),
]