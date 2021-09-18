from django.conf.urls import url

from . import views

urlpatterns = [
    # 编辑地址标题
    url(r'^$', views.ContentView.as_view())
]