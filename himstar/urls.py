"""
URL configuration for himstar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import main_page, contact_us, payment_page, privacy_page, terms_page, withdraw_page      

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page, name='main_page'),
    path('contact/', contact_us, name='contact_us'),
    path('payment/', payment_page, name='payment_page'),
    path('privacy-policy/', privacy_page, name='privacy_page'),
    path('terms/', terms_page, name='terms_page'),
    path('withdrawl/', withdraw_page, name='withdraw_page'),
    path('api/', include('accounts.urls')),
    path('api/', include('banners.urls')),
    path('api/', include('dashboard.urls')),
    path('api/', include('video.urls')),
    path('api/', include('levels.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('contact.urls')),
    path('api/', include('wallet.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
