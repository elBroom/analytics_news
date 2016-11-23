from django.conf.urls import url
from news_api import views

urlpatterns = [
    url(r'^source_list/', views.source_list),
    url(r'^news_list/', views.news_list),
]
