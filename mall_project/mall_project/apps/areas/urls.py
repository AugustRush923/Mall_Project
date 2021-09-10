from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^areas/$', views.AreasView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$', views.AreaSubsView.as_view()),
    url(r'^areas/$', views.AreaViewSet.as_view({'get': 'list'})),
    url(r'^areas/(?P<pk>\d+)/$', views.AreaViewSet.as_view({'get': "retrieve"})),
]
