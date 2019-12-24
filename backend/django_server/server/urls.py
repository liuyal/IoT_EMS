from django.conf.urls import url
from django.contrib import admin

from dashboard import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url('admin/', admin.site.urls),
]
