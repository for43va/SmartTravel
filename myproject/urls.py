"""
URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path
from travel import views 
from django.contrib.auth import views as auth_views 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('arama/', views.arama_sonuclari, name='arama'),
    path('otel/<int:id>/', views.otel_detay, name='otel_detay'),
    path('otel/<int:hotel_id>/rezervasyon/', views.rezervasyon_yap, name='rezervasyon_yap'),
    path('rezervasyonlarim/', views.rezervasyonlarim, name='rezervasyonlarim'),
    path('iptal/<int:id>/', views.rezervasyon_iptal, name='rezervasyon_iptal'),
    path('otel/<int:hotel_id>/kontrol/', views.rezervasyon_kontrol, name='rezervasyon_kontrol'),
    path('password-reset-check/', views.password_reset_check, name='password_reset_check'),
    
    # Chatbot API Yolun
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]