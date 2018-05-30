from django.conf.urls import url, include
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url('^auth/register$', views.register),
    url(r'^auth/token$', obtain_jwt_token),
    url(r'^travel/set$', views.set_travel),
    url(r'^travel/get$', views.get_travel),
]