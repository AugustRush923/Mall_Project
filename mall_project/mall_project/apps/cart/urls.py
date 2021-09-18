from django.conf.urls import url

from cart.views import CartView, CartSelectAllView

urlpatterns = [
    url(r'^$', CartView.as_view()),
    url(r'^selection/$', CartSelectAllView.as_view()),
]
