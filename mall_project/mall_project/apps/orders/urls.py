from django.conf.urls import url

from orders import views

urlpatterns = [
    url(r'^settlement/$', views.OrderSettlementView.as_view()),
    url(r'^$', views.SaveOrderView.as_view()),
]
