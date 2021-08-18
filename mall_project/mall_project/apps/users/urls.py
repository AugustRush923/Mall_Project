from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^email/$', views.EmailUpdateView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
]
