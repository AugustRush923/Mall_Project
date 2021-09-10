from django.conf.urls import url

from cart.views import CartView, CartSelectAllView

urlpatterns = [
    url(r'cart/', CartView.as_view()),
    url(r'cart/selection/', CartSelectAllView.as_view()),
]
