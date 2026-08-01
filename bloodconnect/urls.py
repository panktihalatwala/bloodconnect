from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from donors import views as donor_views
from accounts import views as account_views

urlpatterns = [
    path('', donor_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('donors/', include('donors.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', __import__('accounts.views', fromlist=['signup']).signup, name='signup'),
]