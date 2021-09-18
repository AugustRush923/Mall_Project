from django.conf.urls import url
from . import views

urlpatterns = [
    # /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
    url(r'^(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
    url(r'^(?P<pk>\d+)/$', views.CategoriesView.as_view())
]
