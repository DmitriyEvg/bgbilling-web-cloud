"""lkbilling URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import *
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='home/')),
    url(r'^admin/', admin.site.urls),
    url(r'^access/', include('access.urls')),
    url(r'^home/', include('home.urls')),
    url(r'^bill/', include('bill.urls')),
    url(r'^inet/', include('inet.urls')),
    url(r'^collocation/', include('collocation.urls')),
    url(r'^virt/', include('virt.urls')),
    url(r'^support/', include('support.urls')),
]

handler404 = 'home.views.PageNotFound'