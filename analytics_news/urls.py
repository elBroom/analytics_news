"""analytics_news URL Configuration"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('news_api.urls')),
    url(r'^', include('knox.urls')),
    url(r'^admin/', admin.site.urls),
]
